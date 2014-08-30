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
    assert cython_version > "0.15"
    use_cython = True
    ext = ".pyx"
except (ImportError, AssertionError):
    use_cython = False
    ext = ".cpp"

# fall back to provided cpp file if Cython is not found
extensions = [
    Extension("voroplusplus",
              sources=["pyvoro/voroplusplus" + ext,
                       "pyvoro/vpp.cpp",
                       "src/voro++.cc"],
              include_dirs=["src"],
              language="c++",
              )
]

# cythonize pyx file if right version of Cython is found
if use_cython:
    from Cython.Build import cythonize
    extensions = cythonize(extensions)

setup(
    name="pyvoro",
    version="1.3.1",
    description="2D and 3D Voronoi tessellations: a python entry point for the voro++ library.",
    author="Joe Jordan",
    author_email="joe.jordan@imperial.ac.uk",
    url="https://github.com/joe-jordan/pyvoro",
    download_url="https://github.com/joe-jordan/pyvoro/tarball/v1.3.1",
    packages=["pyvoro",],
    package_dir={"pyvoro": "pyvoro"},
    ext_modules=extensions,
    keywords=["geometry", "mathematics", "Voronoi"],
    classifiers=[],
)
