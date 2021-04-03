"""

"""

## warcraft.package imports
from .config import default_race, race_minimum_level, race_maximum_level
from .events import call_event
from .logging import debug, error, WARCRAFT_LOG_PATH
from .objects import LevelableXP
from .registration import CallbackHandler
from .utility import classproperty, NamingHandler, SubclassFinder ## descriptor

## logging definition

racelog_path = WARCRAFT_LOG_PATH / "races.log"

## __all__ declaration

__all__ = ("Race", )

## race class declaration

class Race(LevelableXP, CallbackHandler, NamingHandler, SubclassFinder):
	""""""
	__default = None

	def __init__(self, *args, **kwargs):
		""""""
		LevelableXP.__init__(self, *args, **kwargs)

		self.skills = [
			Skill(parent=self) for Skill in self._skills
		]

		CallbackHandler.__init__(self, *args, **kwargs)

	# core attributes
	@classmethod
	def is_available(cls, player) -> bool:
		"""Returns whether or not a race should be available to the user."""
		return player.total_level >= 0

	@classproperty
	def description(cls):
		return "N/A"

	@classproperty
	def requirement_string(cls):
		return "DEFAULT"

	@classproperty
	def requirement_sort_key(cls):
		return 0

	@property
	def unused_points(self):
		return self.level - sum(skill.level for skill in self.skills)

	# core events
	def get_event_variables(self, amount):
		return {
			"player": self.parent,
			"race": self,
			"amount": amount
		}

	def level_up(self, amount):
		""""""
		super().level_up(amount)
		call_event("race_level_up", [], self.get_event_variables(amount))

	def level_down(self, amount):
		""""""
		super().level_down(amount)
		call_event("race_level_down", [], self.get_event_variables(amount))

	def experience_up(self, amount):
		""""""
		super().experience_up(amount)
		call_event("race_experience_up", [], self.get_event_variables(amount))

	def experience_down(self, amount):
		""""""
		super().experience_down(amount)
		call_event("race_experience_down", [], self.get_event_variables(amount))

	# core functionality
	_skills = tuple()

	@classmethod
	def add_skill(cls, skill_class):
		debug(racelog_path, f"Adding skill {skill_class} to {cls.name}.")
		cls._skills += (skill_class, )
		return skill_class

	def call_events(self, event_name, *args, **kwargs):
		for callback in self._events[event_name]:
			callback(*args, **kwargs)
		for skill in self.skills:
			skill.call_events(event_name, *args, **kwargs)

	def call_clientcommands(self, command_name, *args, **kwargs):
		for callback in self._clientcommands[command_name]:
			callback(*args, **kwargs)
		for skill in self.skills:
			skill.call_clientcommands(command_name, *args, **kwargs)

	@classproperty
	def default(cls):
		default_race_convar = default_race.cvar.get_string()
		if cls.__default and cls.__default.name == default_race_convar:
			return cls.__default

		## If not already retrieved, store and return.
		for subcls in cls.iter_subclasses():
			if subcls.name == default_race_convar:
				cls.__default = subcls
				return subcls

	@classmethod
	def find_race(cls, race_name):
		for subcls in cls.iter_subclasses():
			debug(racelog_path, subcls.name)
			if subcls.name == race_name:
				return subcls