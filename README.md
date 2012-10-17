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

Initially only non-radical tessellation, and computing *all* information 
(including cell adjacency). Other code paths may be added later.

DEPENDENCIES:
requires Cython > 0.13, which is when c++ support was added. Tested with Cython 0.17.

NOTES:
* on compilation: if a cython .pyx file is being compiled in C++ mode, all cython-visible code must be compiled "as c++" - this will not be compatible with any C functions declared `extern "C" { ... }`. In this library, the author just used c++ functions for everything, in order to be able to utilise the c++ `std::vector<T>` classes to represent the (ridiculously non-specific) geometry of a Voronoi cell.
* A checkout of voro++ itself is included in this project. moving `setup.py` and the `pyvoro` folder into a newer checkout of the voro++ source may well also work, but if any of the definitions used are changed then it will fail to compile. by all means open a support issue if you need this library to work with a newer version of voro++; better still fix it and send me a pull request :)