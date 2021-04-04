"""

"""

## warcraft.package imports
from warcraft.events import call_event
from warcraft.logging import debug, error, WARCRAFT_LOG_PATH
from warcraft.objects import Levelable
from warcraft.registration import CallbackHandler
from warcraft.utility import classproperty, NamingHandler, SubclassFinder ## descriptor

## logging definition

skilllog_path = WARCRAFT_LOG_PATH / "skills.log"

## __all__ declaration

__all__ = ("Skill", )

## skill class declaration

class Skill(Levelable, CallbackHandler, NamingHandler, SubclassFinder):
	""""""

	def __init__(self, *args, **kwargs):
		Levelable.__init__(self, *args, **kwargs)
		CallbackHandler.__init__(self, *args, **kwargs)

	# core attributes
	@classmethod
	def is_available(cls, player) -> bool:
		"""Returns whether or not a skill should be available to the user."""
		return player.race.level > 0

	@classproperty
	def description(cls):
		return "N/A"
	
	# core events
	def get_event_variables(self):
		return {
			"player": self.parent.parent,
			"race": self.parent,
			"skill": self
		}

	def level_up(self, *args, **kwargs):
		""""""
		super().level_up(*args, **kwargs)
		call_event("skill_level_up", [], self.get_event_variables())

	def level_down(self, *args, **kwargs):
		""""""
		super().level_down(*args, **kwargs)
		call_event("skill_level_down", [], self.get_event_variables())