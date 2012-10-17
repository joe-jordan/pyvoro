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
from Cython.Distutils import build_ext

ext_modules = [
  Extension("pyvoro.voroplusplus",
    sources=["pyvoro/voroplusplus.pyx",
      "pyvoro/vpp.cpp",
      "src/voro++.cc"])]

setup(
  cmdclass = {'build_ext': build_ext},
  ext_modules = ext_modules,
  name="pyvoro",
  version="1.0",
  description="Python wrapper for the voro++ c++ library.",
  author="Joe Jordan",
  author_email="joe.jordan@imperial.ac.uk",
  url="http://github.com/joe-jordan/pyvoro",
  packages=["pyvoro"]
)