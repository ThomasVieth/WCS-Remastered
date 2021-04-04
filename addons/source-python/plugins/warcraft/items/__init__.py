"""

"""

## python imports

from configobj import ConfigObj
from glob import glob
from os.path import dirname, basename, isfile

## warcraft.package imports

from warcraft.item import Item
from warcraft.utility import classproperty

## __all__ declaration

modules = glob(dirname(__file__) + '/*.py')
__all__ = ["ini_items", "load_ini_items"] + list(basename(f)[:-3] for f in modules if isfile(f))

ini_items = None
load_ini_items = None ## TODO