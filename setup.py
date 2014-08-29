# 
# setup.py : pyvoro python interface to voro++
# 
# this extension to voro++ is released under the original modified BSD license
# and constitutes an Extension to the original project.
#
# Copyright (c) Joe Jordan 2012
# contact: <joe.jordan@imperial.ac.uk> or <tehwalrus@h2j9k.org>
#

from distutils.core import setup, Extension

# check for Cython version
try:
    from Cython import __version__ as cython_version
    assert cython_version >= "0.15"
except ImportError:
    print " You need to install Cython >= 0.15 to build pyvoro. " \
          " Please use `pip|yum|apt-get install Cython` depending on your Linux distribution"
    raise
except AssertionError:
    print " pyvoro requires a more recent Cython version." + \
          " If you are using a Linux distro's default package, you should switch to a version" + \
          " from https://github.com/cython/cython/ (preferably a stable version above 0.17.x.)"
    raise

from Cython.Build import cythonize

extensions = [
    Extension("voroplusplus",
              sources=["pyvoro/voroplusplus.pyx",
                       "pyvoro/vpp.cpp",
                       "src/c_loops.cc",
                       "src/cell.cc",
                       "src/common.cc",
                       "src/container.cc",
                       "src/container_prd.cc",
                       "src/pre_container.cc",
                       "src/unitcell.cc",
                       "src/v_base.cc",
                       "src/v_compute.cc",
                       "src/wall.cc"],
              include_dirs=["src"],
              language="c++",
              )
]

setup(
    name="pyvoro",
    version="1.2.1",
    description="Python wrapper for the voro++ c++ library.",
    author="Joe Jordan",
    author_email="joe.jordan@imperial.ac.uk",
    url="http://github.com/joe-jordan/pyvoro",
    packages=["pyvoro",],
    package_dir={"pyvoro": "pyvoro"},
    ext_modules=cythonize(extensions),
)
