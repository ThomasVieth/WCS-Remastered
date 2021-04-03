"""

"""

## python imports

from math import inf
from typing import Any

## warcraft.package imports

from .utility import classproperty

## __all__ declaration

__all__ = ("Levelable", "LevelableXP", )

## levelable class declaration

class Levelable:
	"""Abstract class."""
	def __init__(self, init_level: int = 0, parent: Any = None):
		""""""
		self._level = init_level
		self.parent = parent

	@property
	def level(self):
		return self._level

	@level.setter
	def level(self, value):
		if value < self.min_level or value > self.max_level:
			raise ValueError(f"{self.name}.level.set value must be within minimum and maximum level range.")
		self._level = value

	@property
	def is_max_level(self):
		return self.level == self.max_level

	@classproperty
	def max_level(self):
		return inf
	
	@classproperty
	def min_level(self):
		return 0

	def level_up(self, amount: int):
		""""""
		if amount < 0:
			raise ValueError(f"{self.name}.level_up must be given a positive value.")
		self._level = min(self.max_level or inf, self._level + amount)

	def level_down(self, amount: int):
		""""""
		if amount < 0:
			raise ValueError(f"{self.name}.level_down must be given a positive value.")
		self._level = max(self.min_level, self._level - amount)

## experience gain class declaration

class LevelableXP(Levelable):
	"""Abstract class."""
	def __init__(self, init_exp: int = 0, *args, **kwargs):
		""""""
		super().__init__(*args, **kwargs)
		self._exp = init_exp

	def experience_up(self, amount: int):
		""""""
		while self._exp + amount >= self.required_experience:
			amount -= self.required_experience - self._exp
			self.level_up(1)
			self._exp = 0
		self._exp += amount
		if self._exp > self.required_experience:
			self._exp = self.required_experience

	def experience_down(self, amount: int):
		""""""
		while self._exp - amount < 0:
			amount -= self._exp
			self.level_down(1)
			self._exp = self.required_experience
		self._exp -= amount
		if self._exp < 0:
			self._exp = 0

	@property
	def experience(self):
		return self._exp

	@experience.setter
	def experience(self, value):
		self._value = experience

	@property
	def required_experience(self):
		""""""
		level = max(self._level, 1)
		return level * 80