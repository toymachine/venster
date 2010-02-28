# setup.py, config file for distutils

from distutils.core import setup

setup(name="Venster",
      version="0.63",
      description="Venster Windows GUI toolkit",
      author="Henk Punt",
      author_email="henk@entree.nl",
      url="http://venster.sourceforge.net",
      packages=["venster", "venster.lib"],
      data_files=[('', ['LICENSE.TXT'])],
      )

