# 
# setup.py : pyvoro python interface to voro++
# 
# this extension to voro++ is released under the original modified BSD license
# and constitutes an Extension to the original project.
#
# Copyright (c) Joe Jordan 2012
# contact: <joe.jordan@imperial.ac.uk> or <tehwalrus@h2j9k.org>
#

try:
  import cb
except ImportError:
  print "downloading complicated build..."
  import urllib2
  response = urllib2.urlopen('https://raw.github.com/joe-jordan/complicated_build/master/cb/__init__.py')
  content = response.read()
  f = open('cb.py', 'w')
  f.write(content)
  f.close()
  import cb
  print "done!"

# We know that this project requires Cython, and that version 0.14.1 is bugged.
import Cython
cython_major_version = int(Cython.__version__.split('.')[0])
if cython_major_version == 0:
  cython_minor_version = int(Cython.__version__.split('.')[1])
  assert cython_minor_version > 15, "pyvoro requires a more recent Cython version." + \
    " If you are using a Linux distro's default package, you should switch to a version" + \
    " from https://github.com/cython/cython/ (preferably a stable version above 0.17.x.)"

cb.compiler['cc'] = cb.compiler['cpp']

extensions = [
  {
    'name': "pyvoro.voroplusplus",
    'sources' : [
      'pyvoro/voroplusplus.pyx',
      "pyvoro/vpp.cpp",
      "src/voro++.cc"
    ]
  }
]

cb.setup(extensions)(
  name="pyvoro",
  version="1.2.1",
  description="Python wrapper for the voro++ c++ library.",
  author="Joe Jordan",
  author_email="joe.jordan@imperial.ac.uk",
  url="http://github.com/joe-jordan/pyvoro",
  packages=["pyvoro"]
)
