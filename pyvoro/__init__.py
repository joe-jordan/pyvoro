import voroplusplus

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


def _2d_vol_calc(py_cell):
  area = 0.0
  vertices = py_cell['vertices']
  
  for i in range(2, len(vertices)):
    base = [vertices[i][0] - vertices[i-1][0], vertices[i][1] - vertices[i-1][1]]
    side = [vertices[0][0] - vertices[i-1][0], vertices[0][1] - vertices[i-1][1]]
    area += 0.5 * abs(base[0] * side[1] - base[1] * side[0])
  
  return area
  

def compute_2d_voronoi(points, limits, dispersion, radii=[], periodic=[False]*2):
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
  vector_class = points[0].__class__
  points3d = [p[:] +[0.] for p in points]
  limits3d = [l[:] for l in limits] + [[-0.5, +0.5]]
  periodic = periodic + [False]
  py_cells3d = voroplusplus.compute_voronoi(points3d, limits3d, dispersion, radii, periodic)
  
  # we assume that each cell is a prism, and so the 2D solution for each cell contains
  # half of the vertices from the 3D solution. We verify this assumption by asserting
  # that each cell has a face adjacent to both -5 and -6, and that they don't share
  # any vertices. We simply take the -5 cell, and ignore the z components.
  
  py_cells = []
  
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
      'vertices' : [vector_class(p3d['vertices'][v][:-1]) for v in vertices_to_keep]
    })
    
    py_cells[-1]['volume'] = _2d_vol_calc(py_cells[-1])
    
    adj = [[len(vertices_to_keep)-1, 1]]
    for i in range(1, len(vertices_to_keep)-1):
      adj.append([i-1, i+1])
    adj.append([len(vertices_to_keep)-2, 0])
      
    py_cells[-1]['adjacency'] = adj
  
  return py_cells


