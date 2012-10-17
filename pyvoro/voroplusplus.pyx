# distutils: language = c++
# distutils: sources = ../src/voro++.cpp
# 
# voroplusplus.pyx : pyvoro cython interface to voro++
#
# this file provides a python interface for performing 3D voronoi tesselations
# using voro++.
#
# this extension to voro++ is released under the original modified BSD license
# and constitutes an Extension to the original project.
#
# Copyright (c) Joe Jordan 2012
# contact: <joe.jordan@imperial.ac.uk> or <tehwalrus@h2j9k.org>
#


cdef extern from "vpp.h":
  void* container_create(double ax_, double bx_, double ay_, double by_,
    double az_, double bz_, int nx_, int ny_, int nz_)
  void put_particle(void* container_, int i_, double x_, double y_, double z_)
  void put_particles(void* container_, int n_, double* x_, double* y_, double* z_)
  void** compute_voronoi_tesselation(void* container_, int n_)
  double cell_get_volume(void* cell_)
  double* cell_get_vertex_positions(void* cell_, double x_, double y_, double z_)
  int** cell_get_vertex_adjacency(void* cell_)
  int** cell_get_faces(void* cell_)
  void dispose_all(void* container_, void** vorocells, int n_)


cdef extern from "stdlib.h":
  ctypedef unsigned long size_t
  void free(void *ptr)
  void* malloc(size_t size)

import math

class VoronoiPlusPlusError(Exception):
  pass

def compute_voronoi(points, limits, dispersion):
  """
Input arg formats:
  points = list of 3-vectors (lists or compatible class instances) of doubles,
    being the coordinates of the points to voronoi-tesselate.
  limits = 3-list of 2-lists, specifying the start and end sizes of the box the
    points are in.
  dispersion = max distance between two points that might be adjacent (sets
    voro++ block sizes.)
  
Output format is a list of cells as follows:
  [ # list in same order as original points.
    {
      'volume' : 1.0,
      'vetices' : [[1.0, 2.0, 3.0], ...], # positions of vertices
      'adjacency' : [[1,3,4, ...], ...], # cell-vertices adjacent to i by index
      'faces' : [
        {
          'vertices' : [7,4,13, ...], # vertex ids in loop order
          'adjacent_cell' : 34 # *cell* id
        }, ...]
      'original' : point[index] # the original instance from args
    },
    ... 
  ]
  
  NOTE: The class from items in input points list is reused for all 3-vector
  outputs. It must have a contructor which accepts a list of 3 python floats
  (python's list type does satisfy this requirement.)
  """
  cdef int n = len(points), i, j
  cdef double *xs, *ys, *zs
  cdef void** voronoi_cells
  vector_class = points[0].__class__
  
  # build the container object
  cdef void* container = container_create(
    <double>limits[0][0],
    <double>limits[0][1],
    <double>limits[1][0],
    <double>limits[1][1],
    <double>limits[2][0],
    <double>limits[2][1],
    <int>int(math.floor((limits[0][1] - limits[0][0]) / dispersion)),
    <int>int(math.floor((limits[1][1] - limits[1][0]) / dispersion)),
    <int>int(math.floor((limits[2][1] - limits[2][0]) / dispersion))
  )
  
  xs = <double*>malloc(sizeof(double) * n)
  ys = <double*>malloc(sizeof(double) * n)
  zs = <double*>malloc(sizeof(double) * n)
  
  # initialise particle positions:
  for i from 0 <= i < n:
    xs[i] = <double>points[i][0]
    ys[i] = <double>points[i][1]
    zs[i] = <double>points[i][2]
  
  # and add them to the container:
  put_particles(container, n, xs, ys, zs)
  
  # now compute the tessellation:
  voronoi_cells = compute_voronoi_tesselation(container, n)
  
  if voronoi_cells == NULL:
    dispose_all(container, NULL, 0)
    raise VoronoiPlusPlusError("number of cells found was not equal to the number of particles.")
  
  # extract the Voronoi cells into python objects:
  py_cells = [{'original':p} for p in points]
  cdef double* vertex_positions = NULL
  cdef int** lists = NULL
  for i from 0 <= i < n:
    py_cells[i]['volume'] = float(cell_get_volume(voronoi_cells[i]))
    vertex_positions = cell_get_vertex_positions(voronoi_cells[i], xs[i], ys[i], zs[i])
    j = 0
    while vertex_positions[j] != NULL:
      py_cells[i]['vertices'].append(vector_class([
        float(vertex_positions[j]),
        float(vertex_positions[j+1]),
        float(vertex_positions[j+2])
      ]))
      j += 3
    
    free(vertex_positions)
    
    lists = cell_get_vertex_adjacency(voronoi_cells[i])
    py_cells[i]['adjacency'] = []
    j = 0
    while lists[j] != NULL:
      py_cells[i]['adjacency'].append([])
      k = 0
      while lists[j][k] != NULL:
        py_cells[i]['adjacency'][j].append(int(lists[j][k]))
        k += 1
      free(lists[j])
      j += 1
    free(lists)
    
    lists = cell_get_faces(voronoi_cells[i])
    py_cells[i]['faces'] = []
    j = 0
    while lists[j] != NULL:
      py_cells[i]['faces'].append({'vertices' : []})
      k = 0
      while lists[j][k] != NULL:
        py_cells[i]['faces'][j]['vertices'].append(int(lists[j][k]))
        k += 1
      py_cells[i]['faces'][j]['adjacent_cell'] = int(lists[j][k+1])
      free(lists[j])
      j += 1
    free(lists)
  
  # finally, tidy up.
  dispose_all(container, voronoi_cells, n)
  free(xs)
  free(ys)
  free(zs)
  return {'voronoi_cells' : py_cells, 'cell_adjacency' : None}


