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
using namespace std;

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

/* access methods for retrieving voronoi cell instance data. */
double cell_get_volume(void* cell_) {
  voronoicell_neighbor* cell = (voronoicell_neighbor*)cell_;
  return cell->volume();
}

/* input: (x_, y_, z_) the position of the original input point.
 * returns:
 * NULL-terminated list of doubles, coord j of vertex i at ret[i*3 + j]
 */
double* cell_get_vertex_positions(void* cell_, double x_, double y_, double z_) {
  voronoicell_neighbor* cell = (voronoicell_neighbor*)cell_;
  int i, limit = cell->p * 3;
  
  double* positions = (double*)malloc(sizeof(double) * (limit + 1));
  
  for (i = 0; i < limit; i++) {
    positions[i] = cell->pts[i];
  }
  positions[limit] = NULL;
  
  return positions;
}

/* NULL-termed list (i) of NULL-termed lists (j) of vertices adjacent to i. */
int** cell_get_vertex_adjacency(void* cell_) {
  voronoicell_neighbor* cell = (voronoicell_neighbor*)cell_;
  int i, j, v_i_order, num_vertices = cell->p;
  
  int** adjacency = (int**)malloc(sizeof(int*) * (num_vertices + 1));
  
  for (i = 0; i < num_vertices; i++) {
    v_i_order = cell->nu[i];
    adjacency[i] = (int*)malloc(sizeof(int) * (v_i_order + 1));
    for (j = 0; j < v_i_order; j++) {
      adjacency[i][j] = cell->ed[i][j];
    }
    adjacency[i][v_i_order] = NULL;
  }
  adjacency[num_vertices] = NULL;
  
  return adjacency;
}

/* NULL-termed list (i) of NULL-termed lists of vertices on this face,
 * followed by adjacent cell id. e.g for ret[i]:
 * [2 0 5 7 3 NULL 249] for loop 2,0,5,7,3 leading to cell 249.
 */
int** cell_get_faces(void* cell_) {
  voronoicell_neighbor* cell = (voronoicell_neighbor*)cell_;
  int i, j, f_i_order, num_faces = cell->number_of_faces();
  
  int** faces = (int**)malloc(sizeof(int*) * (num_faces + 1));
  vector<int> vertices;
  vector<int> neighbours;
  
  cell->neighbors(neighbours);
  for (i = 0; i < num_faces; i++) {
    cell->face_vertices(vertices);
    f_i_order = vertices.size();
    faces[i] = (int*)malloc(sizeof(int) * (f_i_order + 2));
    for (j = 0; j < f_i_order; j++) {
      faces[i][j] = vertices[i];
    }
    faces[i][f_i_order] = NULL;
    faces[i][f_i_order+1] = neighbours[i];
  }
  faces[num_faces] = NULL;
  
  return faces;
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