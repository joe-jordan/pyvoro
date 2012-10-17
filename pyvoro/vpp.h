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

/* TODO: access methods for retrieving voronoi cell instance data. */

void dispose_all(void* container_, void** vorocells, int n_);

#ifdef __cplusplus
}
#endif

#endif


