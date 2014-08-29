# 
# setup.py : pyvoro python interface to voro++
# 
# this extension to voro++ is released under the original modified BSD license
# and constitutes an Extension to the original project.
#
# Copyright (c) Joe Jordan 2012
# contact: <joe.jordan@imperial.ac.uk> or <tehwalrus@h2j9k.org>
#

from setuptools import setup, Extension
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
    ext_modules=cythonize(extensions)
)
