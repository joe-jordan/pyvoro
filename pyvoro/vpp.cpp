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
#include <stdio.h>
using namespace voro;
using namespace std;

void* container_poly_create(double ax_, double bx_, double ay_, double by_,
  double az_, double bz_, int nx_, int ny_, int nz_, int px_, int py_, int pz_) {
  
  return (void*)new container_poly(ax_, bx_, ay_, by_, az_, bz_, nx_, ny_, nz_, (bool)px_,
      (bool)py_, (bool)pz_, 3);
}

void put_particle(void* container_poly_, int i_, double x_, double y_, double z_, double r_) {
  container_poly* c = (container_poly*)container_poly_;
  c->put(i_, x_, y_, z_, r_);
}

void put_particles(void* container_poly_, int n_, double* x_, double* y_, double* z_, double* r_) {
  container_poly* c = (container_poly*)container_poly_;
  int i;
  for (i = 0; i < n_; i++) {
    c->put(i, x_[i], y_[i], z_[i], r_[i]);
  }
}

void** compute_voronoi_tesselation(void* container_poly_, int n_) {
  container_poly* con = (container_poly*)container_poly_;
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
    // currently being considered by the loop.
    cla->pos(i, x, y, z, r);
    
    // Store the resulting cell instance at the appropriate index on vorocells.
    cellptr = new voronoicell_neighbor();
    *(cellptr) = cell;
    vorocells[i] = (void*)cellptr;
    found++;
    
  } while (cla->inc());
  
  delete cla;
  
  if (found != n_) {
    printf("missing cells: ");
    for (i = 0; i < n_; i++) {
      if (vorocells[i] != NULL) {
        delete (voronoicell_neighbor*)vorocells[i];
      } else {
        printf("%i ", i);
      }
    }
    free(vorocells);
    printf("\n");
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
 * vector of doubles, coord j of vertex i at ret[i*3 + j]
 */
vector<double> cell_get_vertex_positions(void* cell_, double x_, double y_, double z_) {
  voronoicell_neighbor* cell = (voronoicell_neighbor*)cell_;
  vector<double> positions;
  
  cell->vertices(x_, y_, z_, positions);
  
  return positions;
}

/* NULL-termed list (i) of vector<int>s (j) of vertices adjacent to i. */
void** cell_get_vertex_adjacency(void* cell_) {
  voronoicell_neighbor* cell = (voronoicell_neighbor*)cell_;
  int i, j, v_i_order, num_vertices = cell->p;
  
  void** adjacency = (void**)malloc(sizeof(void*) * (num_vertices + 1));
  vector<int>* vertex_adjacency;
  
  for (i = 0; i < num_vertices; i++) {
    v_i_order = cell->nu[i];
    vertex_adjacency = new vector<int>();
    for (j = 0; j < v_i_order; j++) {
      vertex_adjacency->push_back(cell->ed[i][j]);
    }
    adjacency[i] = (void*)vertex_adjacency;
  }
  adjacency[num_vertices] = NULL;
  
  return adjacency;
}

/* NULL-termed list (i) of vector<int>s of vertices on this face,
 * followed by adjacent cell id. e.g for ret[i]:
 * [2 0 5 7 3 -1 249] for loop 2,0,5,7,3 leading to cell 249.
 */
void** cell_get_faces(void* cell_) {
  voronoicell_neighbor* cell = (voronoicell_neighbor*)cell_;
  int i, j, f_i_order, num_faces = cell->number_of_faces();
  
  void** faces = (void**)malloc(sizeof(void*) * (num_faces + 1));
  vector<int> vertices;
  vector<int> neighbours;
  vector<int>* output_list = NULL;
  
  cell->neighbors(neighbours);
  cell->face_vertices(vertices);
  for (i = 0; i < num_faces; i++) {
    f_i_order = vertices[0];
    output_list = new vector<int>();
    for (j = 1; j <= f_i_order; j++) {
      output_list->push_back(vertices[j]);
    }
    output_list->push_back(neighbours[i]);
    vertices.erase(vertices.begin(),vertices.begin()+f_i_order+1);
    faces[i] = (void*)output_list;
  }
  faces[num_faces] = NULL;
  
  return faces;
}


void dispose_all(void* container_poly_, void** vorocells, int n_) {
  delete (container_poly*)container_poly_;
  
  if (vorocells == NULL) return;
  
  int i;
  for (i = 0; i < n_; i++) {
    delete (voronoicell_neighbor*)vorocells[i];
  }
  
  free(vorocells);
}

