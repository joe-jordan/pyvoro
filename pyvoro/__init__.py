from . import voroplusplus
import unittest

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

class Test3D(unittest.TestCase):
    def setUp(self):
        self.positions = [[1.0, 2.0, 3.0], [4.0, 5.5, 6.0]]
        self.limits = [[0.0, 10.0], [0.0, 10.0], [0.0, 10.0]]
        self.radii = [1.3, 1.4]
        self.voronoi = compute_voronoi(
          self.positions, # point positions
          self.limits, # limits
          2.0, # block size
          radii=self.radii # particle radii -- optional, and keyword-compatible arg.
        )
    
    def test_volume(self):
        volumes = [207.1020518571429, 792.8979481428571]
        for cell,vol in zip(self.voronoi, volumes):
            self.assertAlmostEqual(cell['volume'], vol)
            
    def test_positions(self):
        for cell, pos in zip(self.voronoi, self.positions):
            for xi_cell, xi_self in zip(cell['original'], pos):
                self.assertAlmostEqual(xi_cell, xi_self)
                
    def test_adjacency(self):
        adjs =  [[[1, 4, 2],
                  [3, 5, 0],
                  [3, 0, 6],
                  [5, 1, 2],
                  [6, 0, 7],
                  [7, 1, 3],
                  [2, 4, 7],
                  [6, 4, 5]],
                 [[1, 6, 4],
                  [9, 5, 0],
                  [4, 6, 3],
                  [2, 7, 8],
                  [0, 2, 8],
                  [1, 9, 7],
                  [7, 2, 0],
                  [5, 3, 6],
                  [4, 3, 9],
                  [8, 5, 1]]]
        self.assertEqual(adjs, [cell['adjacency'] for cell in self.voronoi])
    
    def test_vertices(self):
        vertices = [[[0.0, 0.0, 0.0],
                      [10.0, 0.0, 0.0],
                      [0.0, 9.711428571428572, 0.0],
                      [10.0, 1.14, 0.0],
                      [0.0, 0.0, 10.0],
                      [10.0, 0.0, 1.33],
                      [0.0, 1.14, 10.0],
                      [1.33, 0.0, 10.0]],
                     [[0.0, 1.14, 10.0],
                      [1.33, 0.0, 10.0],
                      [0.0, 10.0, 0.0],
                      [10.0, 10.0, 0.0],
                      [0.0, 9.711428571428572, 0.0],
                      [10.0, 0.0, 10.0],
                      [0.0, 10.0, 10.0],
                      [10.0, 10.0, 10.0],
                      [10.0, 1.14, 0.0],
                      [10.0, 0.0, 1.33]]]
        for cell, vlist in zip(self.voronoi, vertices):
            for vx_cell, vx in zip(cell['vertices'], vlist):
                for xi_cell, xi_self in zip(vx_cell, vx):
                    self.assertAlmostEqual(xi_cell, xi_self)
        
    def test_faces(self):
        faces = [
         [{'adjacent_cell': -5, 'vertices': [1, 3, 2, 0]},
          {'adjacent_cell': -2, 'vertices': [1, 5, 3]},
          {'adjacent_cell': -3, 'vertices': [1, 0, 4, 7, 5]},
          {'adjacent_cell': 1, 'vertices': [2, 3, 5, 7, 6]},
          {'adjacent_cell': -1, 'vertices': [2, 6, 4, 0]},
          {'adjacent_cell': -6, 'vertices': [4, 6, 7]}],
         [{'adjacent_cell': 0, 'vertices': [1, 9, 8, 4, 0]},
          {'adjacent_cell': -3, 'vertices': [1, 5, 9]},
          {'adjacent_cell': -6, 'vertices': [1, 0, 6, 7, 5]},
          {'adjacent_cell': -5, 'vertices': [2, 4, 8, 3]},
          {'adjacent_cell': -1, 'vertices': [2, 6, 0, 4]},
          {'adjacent_cell': -4, 'vertices': [2, 3, 7, 6]},
          {'adjacent_cell': -2, 'vertices': [3, 8, 9, 5, 7]}]]
    
        for cell,cell_faces in zip(self.voronoi, faces):
            self.assertAlmostEqual(cell['faces'], cell_faces)

class Test2D(unittest.TestCase):
    def setUp(self):
        self.positions = [[1.0, 2.0], [4.0, 5.5]]
        self.limits = [[0.0, 10.0], [0.0, 10.0]]
        self.radii = [1.3, 1.4]
        self.voronoi = compute_2d_voronoi(
          self.positions, # point positions
          self.limits, # limits
          2.0, # block size
          radii=self.radii # particle radii -- optional, and keyword-compatible arg.
        )
    
    def test_volume(self):
        volumes = [19.99238571428571, 80.00761428571428]
        for cell,vol in zip(self.voronoi, volumes):
            self.assertAlmostEqual(cell['volume'], vol)
            
    def test_positions(self):
        for cell, pos in zip(self.voronoi, self.positions):
            for xi_cell, xi_self in zip(cell['original'], pos):
                self.assertAlmostEqual(xi_cell, xi_self)
                
    def test_adjacency(self):
        adjs =  [[[2, 1], [0, 2], [1, 0]], [[4, 1], [0, 2], [1, 3], [2, 4], [3, 0]]]
        self.assertEqual(adjs, [cell['adjacency'] for cell in self.voronoi])
    
    def test_vertices(self):
        vertices = [[[0.0, 5.854285714285714], [0.0, 0.0], [6.83, 0.0]],
                     [[10.0, 0.0],
                      [10.0, 10.0],
                      [0.0, 10.0],
                      [0.0, 5.854285714285715],
                      [6.83, 0.0]]]
        for cell, vlist in zip(self.voronoi, vertices):
            for vx_cell, vx in zip(cell['vertices'], vlist):
                for xi_cell, xi_self in zip(vx_cell, vx):
                    self.assertAlmostEqual(xi_cell, xi_self)
        
    def test_faces(self):
        faces = [[{'adjacent_cell': 1, 'vertices': [0, 2]},
                  {'adjacent_cell': -1, 'vertices': [0, 1]},
                  {'adjacent_cell': -3, 'vertices': [2, 1]}],
                 [{'adjacent_cell': -2, 'vertices': [0, 1]},
                  {'adjacent_cell': -3, 'vertices': [0, 4]},
                  {'adjacent_cell': -1, 'vertices': [2, 3]},
                  {'adjacent_cell': -4, 'vertices': [2, 1]},
                  {'adjacent_cell': 0, 'vertices': [3, 4]}]]
    
        for cell,cell_faces in zip(self.voronoi, faces):
            self.assertAlmostEqual(cell['faces'], cell_faces)
