"""

"""

## warcraft.package imports
from warcraft.events import call_event
from warcraft.logging import debug, error, WARCRAFT_LOG_PATH
from warcraft.registration import CallbackHandler
from warcraft.utility import classproperty, NamingHandler, SubclassFinder ## descriptor

## logging definition

skilllog_path = WARCRAFT_LOG_PATH / "skills.log"

## __all__ declaration

__all__ = ("Item", )

## item class declaration

class Item(CallbackHandler, NamingHandler, SubclassFinder):
    """"""

    def __init__(self, *args, **kwargs):
        CallbackHandler.__init__(self, *args, **kwargs)

    # core attributes
    @classmethod
    def is_available(cls, player) -> bool:
        """Returns whether or not a skill should be available to the user."""
        return player.cash > 0

    @classproperty
    def description(cls):
        return "N/A"
    
    # core events
    def get_event_variables(self):
        return {
            "player": self.parent.parent,
            "item": self
        }

    def on_purchase(self, *args, **kwargs):
        """"""
        call_event("item_purchased", [], self.get_event_variables())

    def on_remove(self, *args, **kwargs):
        """"""
        call_event("item_removed", [], self.get_event_variables())

    # core functionality
    def call_events(self, event_name, *args, **kwargs):
        for callback in self._events[event_name]:
            callback(*args, **kwargs)

    def call_clientcommands(self, command_name, *args, **kwargs):
        for callback in self._clientcommands[command_name]:
            callback(*args, **kwargs)