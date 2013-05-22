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
  version="1.2.0",
  description="Python wrapper for the voro++ c++ library.",
  author="Joe Jordan",
  author_email="joe.jordan@imperial.ac.uk",
  url="http://github.com/joe-jordan/pyvoro",
  packages=["pyvoro"]
)
