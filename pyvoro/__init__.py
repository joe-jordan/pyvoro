from . import voroplusplus

def compute_voronoi(points, limits, dispersion, radii=[], periodic=[False]*3):
  """
Input arg formats:
  points = list of 3-vectors (lists or compatible class instances) of doubles,
    being the coordinates of the points to Voronoi-tessellate.
  limits = 3-list of 2-lists, specifying the start and end sizes of the box the
    points are in.
  dispersion = max distance between two points that might be adjacent (sets
    voro++ block sizes.)
  radii (optional) = list of python floats as the sphere radii of the points,
    for radical (weighted) tessellation.
  periodic (optional) = 3-list of bools indicating x, y and z periodicity of 
    the system box.
  
Output format is a list of cells as follows:
  [ # list in same order as original points.
    {
      'volume' : 1.0,
      'vertices' : [[1.0, 2.0, 3.0], ...], # positions of vertices
      'adjacency' : [[1,3,4, ...], ...], # cell-vertices adjacent to i by index
      'faces' : [
        {
          'vertices' : [7,4,13, ...], # vertex ids in loop order
          'adjacent_cell' : 34 # *cell* id, negative if a wall
        }, ...]
      'original' : point[index] # the original instance from args
    },
    ... 
  ]
  
  NOTE: The class from items in input points list is reused for all 3-vector
  outputs. It must have a constructor which accepts a list of 3 python floats
  (python's list type does satisfy this requirement.)
  """
  return voroplusplus.compute_voronoi(points, limits, dispersion, radii, periodic)

def compute_2d_voronoi(points, limits, dispersion, radii=[], periodic=[False]*2, z_height=0.5):
  """Input arg formats:
  points = list of 2-vectors (lists or compatible class instances) of doubles,
    being the coordinates of the points to Voronoi-tessellate.
  limits = 2-list of 2-lists, specifying the start and end sizes of the box the
    points are in.
  dispersion = max distance between two points that might be adjacent (sets
    voro++ block sizes.)
  radii (optional) = list of python floats as the circle radii of the points,
    for radical (weighted) tessellation.
  periodic (optional) = 2-list of bools indicating x and y periodicity of 
    the system box.
  z_height = a suitable system-size dimension value (if this is particularly different to the
    other system lengths, voro++ will be very inefficient.)
  
Output format is a list of cells as follows:
  [ # list in same order as original points.
    {
      'volume' : 1.0, # in fact, in 2D, this is the area.
      'vertices' : [[1.0, 2.0], ...], # positions of vertices
      'adjacency' : [[1,3], ...], # cell-vertices adjacent to i by index
      'faces' : [
        {
          'vertices' : [7,4], # vertex ids, always 2 for a 2D cell edge.
          'adjacent_cell' : 34 # *cell* id, negative if a wall
        }, ...]
      'original' : point[index] # the original instance from args
    },
    ... 
  ]"""
  vector_class = voroplusplus.get_constructor(points[0])
  points = [list(p) for p in points]
  points3d = [p[:] +[0.] for p in points]
  limits3d = [l[:] for l in limits] + [[-z_height, +z_height]]
  periodic = periodic + [False]
  
  py_cells3d = voroplusplus.compute_voronoi(points3d, limits3d, dispersion, radii, periodic)
  
  # we assume that each cell is a prism, and so the 2D solution for each cell contains
  # half of the vertices from the 3D solution. We verify this assumption by asserting
  # that each cell has a face adjacent to both -5 and -6, and that they don't share
  # any vertices. We simply take the -5 cell, and ignore the z components.
  
  py_cells = []
  depth = z_height * 2
  
  for p3d in py_cells3d:
    faces_to = [f['adjacent_cell'] for f in p3d['faces']]
    assert(-5 in faces_to and -6 in faces_to)
    vertices_to_keep = p3d['faces'][faces_to.index(-5)]['vertices']
    
    faces2d = []
    for f in p3d['faces']:
      if f['adjacent_cell'] == -5 or f['adjacent_cell'] == -6:
        continue
      faces2d.append({
        'adjacent_cell':f['adjacent_cell'],
        'vertices' : [vertices_to_keep.index(vid) for vid in f['vertices'] if vid in vertices_to_keep]
      })
    
    py_cells.append({
      'faces' : faces2d,
      'original' : vector_class(p3d['original'][:-1]),
      'vertices' : [vector_class(p3d['vertices'][v][:-1]) for v in vertices_to_keep],
      'volume' : p3d['volume'] / depth
    })
    
    adj = [[len(vertices_to_keep)-1, 1]]
    for i in range(1, len(vertices_to_keep)-1):
      adj.append([i-1, i+1])
    adj.append([len(vertices_to_keep)-2, 0])
      
    py_cells[-1]['adjacency'] = adj
  
  return py_cells

def compute_3d_voronoi(points, limits, dispersion, radii=[], periodic=[False]*3, excluded=[], properties=['neighbors']):
  """
  Same as compute_voronoi method with lower memory requirements and extra arguments for
  controlling the points to be used for the tessellation and the properties of the voronoi
  cells to be retrieved.
Input arg formats:
  points = list of 3-vectors (lists or compatible class instances) of doubles,
    being the coordinates of the points to Voronoi-tessellate.
  limits = 3-list of 2-lists, specifying the start and end sizes of the box the
    points are in.
  dispersion = max distance between two points that might be adjacent (sets
    voro++ block sizes.)
  radii (optional) = list of python floats as the sphere radii of the points,
    for radical (weighted) tessellation.
  periodic (optional) = 3-list of bools indicating x, y and z periodicity of 
    the system box.
  excluded (optional) = list of python bools indicating if a point  will be
    considered for the tessellation.
  properties = (optional) a str list with the properties to retrieve and
    return for each cell. The available properties are:
    'original'  : 3-vectors, point coordinates
    'radius'    : float, point radius
    'volume'    : float, cell volume
    'surface'   : float, cell surfae
    'rmaxsq'    : float, the maximum radius squared of a vertex from the center of the cell
    'vertices'  : list (3-vectors), positions of cell verices
    'normals'   : list (3-vectors), faces normal vectors
    'areas'     : list (float), faces surface area
    'adjacency' : list (list(int)), for eaech cell-vertice the adjacent cell-vertices
    'faces'     : list ({}),[{'vertices':[],'adjacent_cell'}:int] for each adjacent cell
                  its id and the list of the common vertices.
    'neighbors' : list (int), the indxes of the neighbor cells.

    If this argument is omitted, only the 'neighbors' property will be retrieved.
    If the provided list is empty, all the available properties will be retrieved.

Output format is a list of cells as follows:
  if Full is True
  [ # list in same order as original non-excluded points.
    {
      'original'  : point[index]   # the original instance from args
      'radius'    : 1.0,             # point radius
      'volume'    : 1.0,
      'surface'   : 1.0,
      'rmaxsq'    : 1.0,
      'vertices'  : [[1.0, 2.0, 3.0], ...], # positions of vertices
      'adjacency' : [[1,3,4, ...], ...], # cell-vertices adjacent to i by index
      'faces' : [
        {
          'vertices' : [7,4,13, ...], # vertex ids in loop order
          'adjacent_cell' : 34        # *cell* id, negative if a wall
        }, ...],
      'neighbors' : [1,2,3,...]       # neighbor cells
    },
    ... 
  ]

  NOTE: The class from items in input points list is reused for all 3-vector
  outputs. It must have a constructor which accepts a list of 3 python floats
  (python's list type does satisfy this requirement.)
  """
  return voroplusplus.compute_3d_voronoi(points, limits, dispersion, radii, periodic, excluded, properties)
