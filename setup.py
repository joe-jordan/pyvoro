# 
# setup.py : pyvoro python interface to voro++
# 
# this extension to voro++ is released under the original modified BSD license
# and constitutes an Extension to the original project.
#
# Copyright (c) Joe Jordan 2012
# contact: <joe.jordan@imperial.ac.uk> or <tehwalrus@h2j9k.org>
#

import subprocess
from setuptools import setup, Extension
from Cython.Build import cythonize

# make library
pipe = subprocess.Popen("make")
pipe.wait()

extensions = [
    Extension("voroplusplus", ["pyvoro/voroplusplus.pyx"],
              language="c++")
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
