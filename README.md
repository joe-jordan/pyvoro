pyvoro
======

3D Voronoi tessellations: a python entry point for the [voro++ library](http://math.lbl.gov/voro++/)

**Recently Added Features:**

*Released on PyPI* - thanks to a contribution from @ansobolev, you can now install the project with
`pip` - just type `pip install pyvoro`, with sudo if that's your thing.

*support for numpy arrays* - thanks to a contribution from @christopherpoole, you can now pass in
a 2D (Nx3 or Nx2) numpy array.

*2D helper*, which translates the results of a 3D tesselation of points on the plane back into
2D vectors and cells (see below for an example.)

*Radical (weighted) option*, which weights the voronoi cell sizes according to a set of supplied
radius values.

*periodic boundary support*, note that each cell is returned in the frame of reference of its source
point, so points can (and will) be outside the bounding box.

Installation
------------

Recommended - installation via `pip`:

    pip install pyvoro

Installation from source is the same as for any other python module. Issuing 
  
    python setup.py install
    
will install pyvoro system-wide, while 

    python setup.py install --user

will install it only for the current user. Any 
[other](https://pythonhosted.org/an_example_pypi_project/setuptools.html#using-setup-py)  `setup.py` keywords 
can also be used, including 
 
    python setup.py develop
    
to install the package in 'development' mode. Alternatively, if you want all the dependencies pulled in automatically,  
you can still use `pip`:

    pip install -e .

`-e` option makes pip install package from source in development mode. 

You can then use the code with:

    import pyvoro
    pyvoro.compute_voronoi( ... )
    pyvoro.compute_2d_voronoi( ... )

Example:
--------

```python
import pyvoro
pyvoro.compute_voronoi(
  [[1.0, 2.0, 3.0], [4.0, 5.5, 6.0]], # point positions
  [[0.0, 10.0], [0.0, 10.0], [0.0, 10.0]], # limits
  2.0, # block size
  radii=[1.3, 1.4] # particle radii -- optional, and keyword-compatible arg.
)
```

returning an array of voronoi cells in the form:

```python
{ # (note, this cell is not calculated using the above example)
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
    [0.0, 0.0, 0.0],
    [2.6952010660213537, 0.0, 0.0],
    [0.0, 0.0, 1.3157105644765856],
    [2.6796085747800173, 0.9893738662896467, 0.0],
    [0.0, 1.1577688788929044, 0.9667194826924593],
    [2.685575135451888, 0.0, 1.2139446383811037],
    [1.5434724537773115, 0.0, 2.064891808748473],
    [0.0, 1.2236852383897006, 0.0],
    [2.6700186049990116, 1.0246853171897545, 1.1392273839598812],
    [1.6298653128290692, 1.8592211309121414, 0.0],
    [1.8470793965350985, 1.7199178301499591, 1.6938166537039874],
    [1.7528279426840703, 1.7963648490662445, 1.625024494263244]
  ]
}
```

Note that this particle was the closest to the coord system origin - hence
(unimportantly) lots of vertex positions that are zero or roughly zero, and
(importantly) **negative cell ids** which correspond to the boundaries (of which
there are three at the corner of a box, specifically ids `1`, `3` and `5`, (the
`x_i = 0` boundaries, represented with negative ids hence `-1`, `-3` and `-5` --
this is voro++'s conventional way of referring to boundary interfaces.)

Initially only non-radical tessellation, and computing *all* information 
(including cell adjacency). Other code paths may be added later.

2D tessellation
---------------

You can now run a simpler function to get the 2D cells around your points, with all the details
handled for you:

```python
import pyvoro
cells = pyvoro.compute_2d_voronoi(
  [[5.0, 7.0], [1.7, 3.2], ...], # point positions, 2D vectors this time.
  [[0.0, 10.0], [0.0, 10.0]], # box size, again only 2D this time.
  2.0, # block size; same as before.
  radii=[1.2, 0.9, ...] # particle radii -- optional and keyword-compatible.
)
```

the output follows the same schema as the 3D for now, since this is not as annoying as having a 
whole new schema to handle. The adjacency is now a bit redundant since the cell is a polygon and the
vertices are returned in the correct order. The cells look like a list of these:

```python
{ # note that again, this is computed with a different example
  'adjacency': [
    [5, 1],
    [0, 2],
    [1, 3],
    [2, 4],
    [3, 5],
    [4, 0]
  ],
  'faces': [
    { 'adjacent_cell': 23, 'vertices': [0, 5]},
    { 'adjacent_cell': -2, 'vertices': [0, 1]},
    { 'adjacent_cell': 39, 'vertices': [2, 1]},
    { 'adjacent_cell': 25, 'vertices': [2, 3]},
    { 'adjacent_cell': 12, 'vertices': [4, 3]},
    { 'adjacent_cell': 9, 'vertices': [5, 4]}
  ],
  'original': [8.168525781010283, 5.943711239620341],
  'vertices': [
    [10.0, 5.324580764844442],
    [10.0, 6.442713105218478],
    [9.088894888250326, 7.118847221681966],
    [6.740750220282158, 6.444386346261051],
    [6.675322891805883, 5.678806294642725],
    [7.77400067532073, 5.02320427474993]
  ],
  'volume': 5.102702932807149
}
```

*(note that the edges will now be indexed -1 to -4, and the 'volume' key is in fact the area.)*

NOTES:
* on compilation: if a cython .pyx file is being compiled in C++ mode, all cython-visible code must be compiled "as c++" - this will not be compatible with any C functions declared `extern "C" { ... }`. In this library, the author just used c++ functions for everything, in order to be able to utilise the c++ `std::vector<T>` classes to represent the (ridiculously non-specific) geometry of a Voronoi cell.
* A checkout of voro++ itself is included in this project. moving `setup.py` and the `pyvoro` folder into a newer checkout of the voro++ source may well also work, but if any of the definitions used are changed then it will fail to compile. by all means open a support issue if you need this library to work with a newer version of voro++; better still fix it and send me a pull request :)
