"""

"""

## python imports

from collections import defaultdict
from functools import wraps
from re import compile as re_compile
from time import time
from typing import Generator, List

## __all__ declaration

__all__ = ("classproperty", "CooldownDict", "NamingHandler", "SubclassFinder")

## classproperty declaration

class classproperty(property):
    """
    """

    def __new__(cls, fget=None, doc=None, lazy=False):
        if fget is None:
            # Being used as a decorator--return a wrapper that implements
            # decorator syntax
            def wrapper(func):
                return cls(func, lazy=lazy)

            return wrapper

        return super().__new__(cls)

    def __init__(self, fget, doc=None, lazy=False):
        self._lazy = lazy
        if lazy:
            self._cache = {}
        fget = self._wrap_fget(fget)

        super().__init__(fget=fget, doc=doc)

        # There is a buglet in Python where self.__doc__ doesn't
        # get set properly on instances of property subclasses if
        # the doc argument was used rather than taking the docstring
        # from fget
        # Related Python issue: https://bugs.python.org/issue24766
        if doc is not None:
            self.__doc__ = doc

    def __get__(self, obj, objtype):
        if self._lazy and objtype in self._cache:
            return self._cache[objtype]

        # The base property.__get__ will just return self here;
        # instead we pass objtype through to the original wrapped
        # function (which takes the class as its sole argument)
        val = self.fget.__wrapped__(objtype)

        if self._lazy:
            self._cache[objtype] = val

        return val

    def getter(self, fget):
        return super().getter(self._wrap_fget(fget))

    def setter(self, fset):
        raise NotImplementedError(
            "classproperty can only be read-only; use a metaclass to "
            "implement modifiable class-level properties")

    def deleter(self, fdel):
        raise NotImplementedError(
            "classproperty can only be read-only; use a metaclass to "
            "implement modifiable class-level properties")

    @staticmethod
    def _wrap_fget(orig_fget):
        if isinstance(orig_fget, classmethod):
            orig_fget = orig_fget.__func__

        # Using stock functools.wraps instead of the fancier version
        # found later in this module, which is overkill for this purpose

        @wraps(orig_fget)
        def fget(obj):
            return orig_fget(obj.__class__)

        return fget

## naminghandler class definition

class NamingHandler:
    """Used to automatically create a readable `name` attribute for the object
    directly created from the __name__ attribute. This takes any class name
    obeying a typical PEP standard and makes it readable for end users.
    """

    name_deconstructor = re_compile('[A-Z][^A-Z]*')

    @classproperty
    def name(cls) -> str:
        """Returns the class's name by formatting the __name__ accordingly."""
        return " ".join(cls.name_deconstructor.findall(cls.__name__))

## subclassfinder class definition

class SubclassFinder:
    """
    """

    @classmethod
    def iter_subclasses(cls) -> Generator[type, None, None]:
        """Iterates through all subclasses of this class."""
        subclasses = cls.__subclasses__()
        for subcls in subclasses:
            yield from subcls.iter_subclasses()
        yield from subclasses

    @classmethod
    def sort_subclasses(cls, *args, **kwargs) -> list:
        """Lists all subclasses of this class and sorts them using the *args and **kwargs."""
        subclasses = list(cls.iter_subclasses())
        return sorted(subclasses, *args, **kwargs)

    @classproperty
    def subclasses(cls) -> list:
        """Lists all subclasses of this class and sorts them using the *args and **kwargs."""
        subclasses = list()
        for subcls in cls.__subclasses__():
            subclasses.append(subcls)
            subclasses.extend(subcls.subclasses)
        return sorted(subclasses, key=lambda x: x.name)

    @classproperty
    def subclasses_as_dict(cls) -> dict:
        """Lists all subclasses of this class and sorts them using the *args and **kwargs."""
        subclasses = dict()
        for subcls in cls.__subclasses__():
            subclasses[subcls.name] = subcls
            subclasses.update(subcls.subclasses_as_dict)
        return sorted(subclasses, key=lambda x: x.name)

##

class CooldownDict(defaultdict):
    """
    """
    
    def __init__(self, default_factory=int, *args, **kwargs):
        super().__init__(default_factory, *args, **kwargs)

    def __getitem__(self, key):
        return super().__getitem__(key) - time()

    def __setitem__(self, key, value):
        return super().__setitem__(key, value + time())