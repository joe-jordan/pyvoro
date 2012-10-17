/*
 * vpp.h : pyvoro C interface to voro++
 *
 * this file provides pure C wrapper functions for creating, manipulating,
 * performing computations on and exporting the voro++ C++ classes.
 *
 * this extension to voro++ is released under the original modified BSD license
 * and constitutes an Extension to the original project.
 *
 * Copyright (c) Joe Jordan 2012
 * contact: <joe.jordan@imperial.ac.uk> or <tehwalrus@h2j9k.org>
 * 
 */

#ifndef __VPP_H__
#define __VPP_H__ 1

#ifdef __cplusplus
extern "C" {
#endif

void* container_create(double ax_, double bx_, double ay_, double by_,
  double az_, double bz_, int nx_, int ny_, int nz_);

/* void* container_periodic_create(); (TODO) */

void put_particle(void* container_, int i_, double x_, double y_, double z_);

void put_particles(void* container_, int n_, double* x_, double* y_, double* z_);

void** compute_voronoi_tesselation(void* container_, int n_);

/* access methods for retrieving voronoi cell instance data. */
double cell_get_volume(void* cell_);

/* input: (x_, y_, z_) the position of the original input point.
 * returns:
 * NULL-terminated list of doubles, coord j of vertex i at ret[i*3 + j]
 */
double* cell_get_vertex_positions(void* cell_, double x_, double y_, double z_);

/* NULL-termed list (i) of NULL-termed lists (j) of vertices adjacent to i. */
int** cell_get_vertex_adjacency(void* cell_);

/* NULL-termed list (i) of NULL-termed lists of vertices on this face,
 * followed by adjacent cell id. e.g for ret[i]:
 * [2 0 5 7 3 NULL 249] for loop 2,0,5,7,3 leading to cell 249.
 */
int** cell_get_faces(void* cell_);

void dispose_all(void* container_, void** vorocells, int n_);

#ifdef __cplusplus
}
#endif

#endif


