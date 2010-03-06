# setup.py, config file for distutils

from distutils.core import setup
import py2exe


setup(name="sampleapp",
      windows=[{"script": "sampleapp.py",
                "icon_resources": [(1, "COW.ICO")]}])
