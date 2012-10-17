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

Initially only non-radical tesselation, and computing *all* information 
(including cell adjacency). Other code paths may be added later.
