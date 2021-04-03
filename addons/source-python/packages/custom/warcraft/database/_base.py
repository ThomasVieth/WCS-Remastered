"""

"""

## python imports

from sqlalchemy.ext.declarative import declared_attr, declarative_base

## __all__ declaration

__all__ = ("Base", "_BaseMixin", )

## base mixin declaration

class _BaseMixin(object):
	"""Pseudo-abstract class for declaring sqlalchemy constructs."""

	@declared_attr
	def __tablename__(cls):
		return cls.__name__.lower() + 's'

	def __repr__(self):
		"""Overriden __repr__ to return in format _BaseMixin<{self.name}>."""
		return f"{self.__class__.__name__}<\"{self.name}\">"

	def __str__(self):
		"""Overriden __str__ to return in format _BaseMixin<{self.name}>{...}"""
		return f"{self.__class__.__name__}<\"{self.name}\">" + str(self.__dict__)

Base = declarative_base(cls=_BaseMixin)