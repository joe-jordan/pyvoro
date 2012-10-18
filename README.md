pyvoro
======

3D Voronoi tessellations: a python entry point for the [voro++ library](http://math.lbl.gov/voro++/)

example:

    import pyvoro
    pyvoro.compute_voronoi(
      [[1.0, 2.0, 3.0], [4.0, 5.5, 6.0]], # point positions
      [[0.0, 10.0], [0.0, 10.0], [0.0, 10.0]], # limits
      2.0 # block size
    )

returning an array of voronoi cells in the form:

    {
      'volume': 6.07031902214448, 
      'faces': [
        {'adjacent_cell': 1, 'vertices': [1, 5, 8, 3]},
        {'adjacent_cell': -3, 'vertices': [1, 0, 2, 6, 5]},
        {'adjacent_cell': -5, 'vertices': [1, 3, 9, 7, 0]},
        {'adjacent_cell': 146, 'vertices': [2, 4, 11, 10, 6]},
        {'adjacent_cell': -1, 'vertices': [2, 0, 7, 4]},
        {'adjacent_cell': 9, 'vertices': [3, 8, 10, 11, 9]},
        {'adjacent_cell': 11, 'vertices': [4, 7, 9, 11]},
        {'adjacent_cell': 139, 'vertices': [5, 6, 10, 8]}
      ],
      'adjacency': [
        [1, 2, 7],
        [5, 0, 3],
        [4, 0, 6],
        [8, 1, 9],
        [11, 7, 2],
        [6, 1, 8],
        [2, 5, 10],
        [9, 0, 4],
        [5, 3, 10],
        [11, 3, 7],
        [6, 8, 11],
        [10, 9, 4]
      ],
      'original': [1.58347382116, 0.830481034382, 0.84264445125],
      'vertices': [
        [-1.58347382116, -0.830481034382, -0.84264445125],
        [-0.830481034382, -0.84264445125, -0.0774882476040002],
        [-0.84264445125, -0.0774882476040002, -0.8548078681179999],
        [-0.0774882476040002, -0.8548078681179999, 3.066098940972707],
        [-0.8548078681179999, 3.066098940972707, -0.10181508134000006],
        [3.066098940972707, -0.10181508134000006, 3.0539355241047073],
        [-0.10181508134000006, 3.0539355241047073, -0.8183176175140001],
        [3.0539355241047073, -0.8183176175140001, 3.8069283108827072],
        [-0.8183176175140001, 3.8069283108827072, -0.830481034382],
        [3.8069283108827072, -0.830481034382, -0.84264445125],
        [-0.830481034382, -0.84264445125, -0.0774882476040002],
        [-0.84264445125, -0.0774882476040002, -0.8548078681179999]
      ]
    }

Initially only non-radical tessellation, and computing *all* information 
(including cell adjacency). Other code paths may be added later.

DEPENDENCIES:
requires Cython > 0.13, which is when c++ support was added. Tested with Cython 0.17.

NOTES:
* on compilation: if a cython .pyx file is being compiled in C++ mode, all cython-visible code must be compiled "as c++" - this will not be compatible with any C functions declared `extern "C" { ... }`. In this library, the author just used c++ functions for everything, in order to be able to utilise the c++ `std::vector<T>` classes to represent the (ridiculously non-specific) geometry of a Voronoi cell.
* A checkout of voro++ itself is included in this project. moving `setup.py` and the `pyvoro` folder into a newer checkout of the voro++ source may well also work, but if any of the definitions used are changed then it will fail to compile. by all means open a support issue if you need this library to work with a newer version of voro++; better still fix it and send me a pull request :)