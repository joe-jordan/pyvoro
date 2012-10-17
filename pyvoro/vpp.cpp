/*
 * vpp.cpp : pyvoro C interface to voro++ (implementation)
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

#include "vpp.h"
#include "../src/voro++.hh"
using namespace voro;

void* container_create(double ax_, double bx_, double ay_, double by_,
  double az_, double bz_, int nx_, int ny_, int nz_) {
  
  return (void*)new container(ax_, bx_, ay_, by_, az_, bz_, nx_, ny_, nz_, false, false, false, 3);
}

/* void* container_periodic_create(); (TODO) */

void put_particle(void* container_, int i_, double x_, double y_, double z_) {
  container* c = (container*)container_;
  c->put(i_, x_, y_, z_);
}

void put_particles(void* container_, int n_, double* x_, double* y_, double* z_) {
  container* c = (container*)container_;
  int i;
  for (i = 0; i < n_; i++) {
    c->put(i, x_[i], y_[i], z_[i]);
  }
}

void** compute_voronoi_tesselation(void* container_, int n_) {
  container* con = (container*)container_;
  int found = 0;
  int i;
  double x, y, z, r;
  c_loop_all* cla = new c_loop_all(*(con));
	voronoicell_neighbor cell;
  voronoicell_neighbor* cellptr = NULL;
  
  void** vorocells = (void**)malloc(sizeof(void*) * n_);
  
  for (i = 0; i < n_; i++) vorocells[i] = NULL;
  
	if(cla->start()) do if (con->compute_cell(cell, *(cla))) {

		// Get the position and ID information for the particle
		// currently being considered by the loop. Ignore the radius
		// information.
		cla->pos(i, x, y, z, r);
    
    // Store the resulting cell instance at the appropriate index on vorocells.
    cellptr = new voronoicell_neighbor();
    *(cellptr) = cell;
    vorocells[i] = (void*)cellptr;
    found++;
    
	} while (cla->inc());
  
  delete cla;
  
  if (found != n_) {
    for (i = 0; i < n_; i++) {
      if (vorocells[i] != NULL) {
        delete (voronoicell_neighbor*)vorocells[i];
      }
    }
    free(vorocells);
    return NULL;
  }
  
  return vorocells;
}

void dispose_all(void* container_, void** vorocells, int n_) {
  delete (container*)container_;
  
  if (vorocells == NULL) return;
  
  int i;
  
  for (i = 0; i < n_; i++) {
    delete (voronoicell_neighbor*)vorocells[i];
  }
  
  free(vorocells);
}