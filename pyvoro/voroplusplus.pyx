# distutils: language = c++
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

from __future__ import division

from libcpp.vector cimport vector
from libcpp.map cimport map
from cython.operator cimport dereference as deref

cdef extern from "vpp.h":
  void* container_poly_create(double ax_, double bx_, double ay_, double by_,
    double az_, double bz_, int nx_, int ny_, int nz_, int px_, int py_, int pz_)
  void put_particle(void* container_poly_, int i_, double x_, double y_, double z_, double r_)
  void put_particles(void* container_poly_, int n_, double* x_, double* y_, double* z_, double* r_)
  void** compute_voronoi_tesselation(void* container_poly_, int n_)
  double cell_get_volume(void* cell_)
  double cell_get_surface(void* cell_)
  double cell_get_max_radius_squared(void* cell_)
  vector[double] cell_get_vertex_positions(void* cell_, double x_, double y_, double z_)
  vector[double] cell_get_normals(void* cell_)
  vector[double] cell_get_areas(void* cell_)
  void** cell_get_vertex_adjacency(void* cell_)
  void** cell_get_faces(void* cell_)
  void dispose_all(void* container_poly_, void** vorocells, int n_)
  void* container_loop_all_create(void* container_poly_)
  void* cell_create()
  int container_loop_all_next(void* container_poly_, void* container_loop_all_, void *cell_, int* nfound)
  void dispose_loop_all(void* container_poly_, void* container_loop_all_, void* cell_)


cdef extern from "stdlib.h":
  ctypedef unsigned long size_t
  void free(void *ptr)
  void* malloc(size_t size)

import sys
import math

class VoronoiPlusPlusError(Exception):
  pass


def get_constructor(obj):
  """
Input arg format:
  obj = the object we want to get the constructor for
  """
  typ = type(obj)

  # Test if we have a numpy array
  if hasattr(typ, '__module__'):
    if typ.__module__ == 'numpy':
      numpy = sys.modules['numpy']
      typ = numpy.array

  return typ


def compute_voronoi(points, limits, dispersion, radii=[], periodic=[False]*3):
  """
Input arg formats:
  points = list of 3-vectors (lists or compatible class instances) of doubles,
    being the coordinates of the points to voronoi-tesselate.
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
      'adjacency' : [[1,3,4, ...], ...],   # cell-vertices adjacent to i by index
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
  cdef int n = len(points), i, j
  cdef double *xs
  cdef double *ys
  cdef double *zs
  cdef double *rs
  cdef void** voronoi_cells

  vector_class = get_constructor(points[0])

  periodic = [1 if p else 0 for p in periodic]

  # we must make sure we have at least one block, or voro++ will segfault when
  # we look for cells.

  blocks = [
    max([1, int(math.floor((limits[0][1] - limits[0][0]) / dispersion))]),
    max([1, int(math.floor((limits[1][1] - limits[1][0]) / dispersion))]),
    max([1, int(math.floor((limits[2][1] - limits[2][0]) / dispersion))])
  ]

  # if no radii provided, we still run the radical routine, but with all the same small radius.
  if len(radii) != len(points):
    radii = [dispersion / 10.] * len(points)

  # build the container object
  cdef void* container = container_poly_create(
    <double>limits[0][0],
    <double>limits[0][1],
    <double>limits[1][0],
    <double>limits[1][1],
    <double>limits[2][0],
    <double>limits[2][1],
    <int>blocks[0],
    <int>blocks[1],
    <int>blocks[2],
    <int>periodic[0],
    <int>periodic[1],
    <int>periodic[2]
  )

  xs = <double*>malloc(sizeof(double) * n)
  ys = <double*>malloc(sizeof(double) * n)
  zs = <double*>malloc(sizeof(double) * n)
  rs = <double*>malloc(sizeof(double) * n)

  # initialise particle positions:
  for i from 0 <= i < n:
    xs[i] = <double>points[i][0]
    ys[i] = <double>points[i][1]
    zs[i] = <double>points[i][2]
    rs[i] = <double>radii[i]

  # and add them to the container:
  put_particles(container, n, xs, ys, zs, rs)

  # now compute the tessellation:
  voronoi_cells = compute_voronoi_tesselation(container, n)

  if voronoi_cells == NULL:
    dispose_all(container, NULL, 0)
    raise VoronoiPlusPlusError("number of cells found was not equal to the number of particles.")

  # extract the Voronoi cells into python objects:
  py_cells = [{'original':p} for p in points]
  cdef vector[double] vertex_positions
  cdef void** lists = NULL
  cdef vector[int]* vptr = NULL
  for i from 0 <= i < n:
    py_cells[i]['volume'] = float(cell_get_volume(voronoi_cells[i]))
    vertex_positions = cell_get_vertex_positions(voronoi_cells[i], xs[i], ys[i], zs[i])
    cell_vertices = []
    for j from 0 <= j < vertex_positions.size() // 3:
      cell_vertices.append(vector_class([
        float(vertex_positions[3 * j]),
        float(vertex_positions[3 * j + 1]),
        float(vertex_positions[3 * j + 2])
      ]))
    py_cells[i]['vertices'] = cell_vertices

    lists = cell_get_vertex_adjacency(voronoi_cells[i])
    adjacency = []
    j = 0
    while lists[j] != NULL:
      py_vertex_adjacency = []
      vptr = <vector[int]*>lists[j]
      for k from 0 <= k < vptr.size():
        py_vertex_adjacency.append(int(deref(vptr)[k]))
      del vptr
      adjacency.append(py_vertex_adjacency)
      j += 1
    free(lists)
    py_cells[i]['adjacency'] = adjacency

    lists = cell_get_faces(voronoi_cells[i])
    faces = []
    j = 0
    while lists[j] != NULL:
      face_vertices = []
      vptr = <vector[int]*>lists[j]
      for k from 0 <= k < vptr.size() - 1:
        face_vertices.append(int(deref(vptr)[k]))
      faces.append({
        'adjacent_cell' : int(deref(vptr)[vptr.size() - 1]),
        'vertices' : face_vertices
      })
      del vptr
      j += 1
    free(lists)
    py_cells[i]['faces'] = faces

  # finally, tidy up.
  dispose_all(container, voronoi_cells, n)
  free(xs)
  free(ys)
  free(zs)
  free(rs)
  return py_cells

def compute_3d_voronoi(points, limits, dispersion, radii=[], periodic=[False]*3, excluded=[], properties=[]):
  """
  Same as compute_voronoi method with lower memory requirements and extra arguments for
  controlling the points to be used for the tessellation and the properties of the voronoi
  cells to be retrieved.  
Input arg formats:
  points = list of 3-vectors (lists or compatible class instances) of doubles,
    being the coordinates of the points to voronoi-tesselate.
  limits = 3-list of 2-lists, specifying the start and end sizes of the box the
    points are in.
  dispersion = max distance between two points that might be adjacent (sets
    voro++ block sizes.)
  radii (optional) = list of python floats as the sphere radii of the points,
    for radical (weighted) tessellation.
  periodic (optional) = 3-list of bools indicating x, y and z periodicity of
    the system box.
  excluded = boolean indicating if a point should be considered or not.
  properties = (optional) a str list with the properties to retrieve and
    return for each cell. The available properties are:
    'original'  : 3-vectors, point coordinates
    'radius'    : float, point radius
    'volume'    : float, cell volume
    'surface'   : float, cell surfae
    'rmaxsq'    : float, the maximum radius squared of a vertex from the center of the cell
    'vertices'  : list (3-vectors), positions of cell verices
    'normals'   : lits (3-vectors), faces normal vectors
    'areas'     : list (flost), faces surface area
    'adjacency' : list (list(int)), for eaech cell-vertice the adjacent cell-vertices
    'faces'     : list ({}),[{'vertices':[],'adjacent_cell'}:int] for each adjacent cell
                  its id and the list of the common vertices.
    'neighbors' : list (int), the indxes of the neighbor cells.

    If this argument is omitted, only the 'neighbors' property will be retrieved.
    If the provided list is empty, all the available properties will be retrieved.
    
Output format is a list of cells as follows (the keys of the dictionaries
depends on the properties argument):
  [ # list in same order as original points.
    {
      'original' : point[index]   # the original instance from args
      'radius' : 1.0,             # point radius
      'volume' : 1.0,
      'surface' : 1.0,
      'rmaxsq' : 1.0,
      'vertices' : [[1.0, 2.0, 3.0], ...], # positions of vertices
      'normals' : [[1.0, 2.0, 3.0], ...],  # faces normal vectors
      'areas' : [1.0, 2.0, 3.0, ...],      # faces surface area
      'adjacency' : [[1,3,4, ...], ...],   # cell-vertices adjacent to i by index
      'faces' : [
        {
          'vertices' : [7,4,13, ...], # vertex ids in loop order
          'adjacent_cell' : 34 # *cell* id, negative if a wall
        }, ...]
      'neighbors' : [1,2,3,...]       # neighbor cells
    },
    ...
  ]
  NOTE: The class from items in input points list is reused for all 3-vector
  outputs. It must have a constructor which accepts a list of 3 python floats
  (python's list type does satisfy this requirement.)
  """
  cdef int n = len(points), i, _i, j, nexclude = sum(excluded)
  cdef _xn = n - nexclude
  cdef map[int,int] _xmap
  cdef double *xs, *ys, *zs, *rs
  cdef void** voronoi_cells

  vector_class = get_constructor( points[0])

  periodic = [1 if p else 0 for p in periodic]

  # we must make sure we have at least one block, or voro++ will segfault when
  # we look for cells.

  blocks = [
    max([1, int(math.floor((limits[0][1] - limits[0][0]) / dispersion))]),
    max([1, int(math.floor((limits[1][1] - limits[1][0]) / dispersion))]),
    max([1, int(math.floor((limits[2][1] - limits[2][0]) / dispersion))])
  ]

  # if no radii provided, we still run the radical routine, but with all the same small radius.
  if len(radii) != len(points):
    radii = [dispersion / 10.] * len(points)

  # build the container object
  cdef void* container = container_poly_create(
    <double>limits[0][0],
    <double>limits[0][1],
    <double>limits[1][0],
    <double>limits[1][1],
    <double>limits[2][0],
    <double>limits[2][1],
    <int>blocks[0],
    <int>blocks[1],
    <int>blocks[2],
    <int>periodic[0],
    <int>periodic[1],
    <int>periodic[2]
  )

  xs = <double*>malloc(sizeof(double) * _xn)
  ys = <double*>malloc(sizeof(double) * _xn)
  zs = <double*>malloc(sizeof(double) * _xn)
  rs = <double*>malloc(sizeof(double) * _xn)

  # initialise particle positions:
  j = 0
  for i from 0 <= i < n:
    if nexclude > 0 and excluded[i]: continue
    xs[j] = <double>points[i][0]
    ys[j] = <double>points[i][1]
    zs[j] = <double>points[i][2]
    rs[j] = <double>radii[i]
    _xmap[j]=i
    j+=1

  # and add them to the container:
  put_particles(container, _xn, xs, ys, zs, rs)

  # now create the loop stuff
  cdef void* c_loop_all = container_loop_all_create( container)
  cdef void* cellptr = cell_create()

  # now compute the tessellation:
  #py_cells = [{'original':p,'radius':r} for p, r in zip(points,radii)]

  py_cells = [ {} for i in range(n) ]
  cdef vector[double] vertex_positions
  cdef void** lists = NULL
  cdef vector[int]* vptr = NULL
  cdef int found = 0, found_ = 0

  # enable property retrieval if found in properties list or if
  # properties list is empty.
  _isempy = len(properties)==0
  cdef int GEToriginal = 1 if _isempy or 'original' in properties else 0
  cdef int GETradius = 1 if _isempy or 'radius' in properties else 0
  cdef int GETvolume = 1 if _isempy or 'volume' in properties else 0
  cdef int GETsurface = 1 if _isempy or 'surface' in properties else 0
  cdef int GETrmaxsq = 1 if _isempy or 'rmaxsq' in properties else 0
  cdef int GETvertices = 1 if _isempy or 'vertices' in properties else 0
  cdef int GETnormals = 1 if _isempy or 'normals' in properties else 0
  cdef int GETareas = 1 if _isempy or 'areas' in properties else 0
  cdef int GETadjacency = 1 if _isempy or 'adjacency' in properties else 0
  cdef int GETfaces = 1 if _isempy or 'faces' in properties else 0
  cdef int GETneighbors = 1 if _isempy or 'neighbors' in properties else 0

  while ( found < _xn):
    _i = container_loop_all_next(container, c_loop_all, cellptr, &found)
    if found == found_ or _i == -1:
      break
    else:
      i = _xmap[_i]
      #print("remain %d" % (_xn-found))
      found_ = found
      py_cell = py_cells[i]

      if GEToriginal:
        py_cell['original'] = points[i]

      if GETradius:
        py_cell['radius'] = radii[i]

      if GETvolume:
        py_cell['volume'] = float(cell_get_volume(cellptr))

      if GETsurface:
        py_cell['surface'] = float(cell_get_surface(cellptr))

      if GETrmaxsq:
        py_cell['rmaxsq'] = float(cell_get_max_radius_squared(cellptr))

      if GETvertices:
        vertex_positions = cell_get_vertex_positions(cellptr, xs[_i], ys[_i], zs[_i])
        cell_vertices = []
        for j from 0 <= j < vertex_positions.size() // 3:
          cell_vertices.append(vector_class([
            float(vertex_positions[3 * j]),
            float(vertex_positions[3 * j + 1]),
            float(vertex_positions[3 * j + 2])
          ]))
        py_cell['vertices'] = cell_vertices

      if GETnormals:
        normals = cell_get_normals(cellptr)
        face_normals = []
        for j from 0 <= j < normals.size() // 3:
          face_normals.append(vector_class([
            float(normals[3 * j]),
            float(normals[3 * j + 1]),
            float(normals[3 * j + 2])
          ]))
        py_cell['normals'] = face_normals

      if GETareas:
        areas = cell_get_areas(cellptr)
        face_areas = []
        for j from 0 <= j < areas.size():
          face_areas.append( float(areas[j]))
        py_cell['areas'] = face_areas

      if GETadjacency:
        lists = cell_get_vertex_adjacency(cellptr)
        adjacency = []
        j = 0
        while lists[j] != NULL:
          py_vertex_adjacency = []
          vptr = <vector[int]*>lists[j]
          for k from 0 <= k < vptr.size():
            py_vertex_adjacency.append(int(deref(vptr)[k]))
          del vptr
          adjacency.append(py_vertex_adjacency)
          j += 1
        free(lists)
        py_cell['adjacency'] = adjacency

      if GETfaces:
        lists = cell_get_faces(cellptr)
        faces = []
        j = 0
        while lists[j] != NULL:
          face_vertices = []
          vptr = <vector[int]*>lists[j]
          for k from 0 <= k < vptr.size() - 1:
            face_vertices.append(int(deref(vptr)[k]))
          faces.append({
            'adjacent_cell' : _xmap[ int(deref(vptr)[vptr.size() - 1]) ],
            'vertices' : face_vertices
          })
          del vptr
          j += 1
        free(lists)
        py_cell['faces'] = faces

      if GETneighbors:
        lists = cell_get_faces(cellptr)
        adjacent = []
        j = 0
        while lists[j] != NULL:
          vptr = <vector[int]*>lists[j]
          adjacent.append( _xmap[ int(deref(vptr)[vptr.size() - 1]) ])
          del vptr
          j += 1
        free(lists)
        py_cell['neighbors'] = tuple(adjacent)

  if not found == _xn:
    raise VoronoiPlusPlusError("number of cells found (%d) was not equal to the number of particles (%d)." % (found, _xn) )

  # finally, tidy up.
  dispose_loop_all(container, c_loop_all, cellptr)
  free(xs)
  free(ys)
  free(zs)
  free(rs)
  return py_cells
