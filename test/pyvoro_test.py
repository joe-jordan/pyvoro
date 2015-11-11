import unittest
import pyvoro

class Test3D(unittest.TestCase):
    def setUp(self):
        self.positions = [[1.0, 2.0, 3.0], [4.0, 5.5, 6.0]]
        self.limits = [[0.0, 10.0], [0.0, 10.0], [0.0, 10.0]]
        self.radii = [1.3, 1.4]
        self.voronoi = pyvoro.compute_voronoi(
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
        self.voronoi = pyvoro.compute_2d_voronoi(
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


if __name__ == "__main__":
    unittest.main()
