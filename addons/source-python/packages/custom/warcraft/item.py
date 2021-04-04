"""

"""

## warcraft.package imports
from warcraft.events import call_event
from warcraft.logging import debug, error, WARCRAFT_LOG_PATH
from warcraft.registration import CallbackHandler
from warcraft.utility import classproperty, NamingHandler, SubclassFinder ## descriptor

## logging definition

itemlog_path = WARCRAFT_LOG_PATH / "items.log"

## __all__ declaration

__all__ = ("Item", )

## item class declaration

class Item(CallbackHandler, NamingHandler, SubclassFinder):
    """"""
    __categories = set()

    def __init__(self, *args, **kwargs):
        CallbackHandler.__init__(self, *args, **kwargs)

    # core attributes
    @classmethod
    def is_available(cls, player) -> bool:
        """Returns whether or not a item should be available to the user."""
        return player.cash > 0

    @classproperty
    def description(cls):
        return "N/A"

    @classproperty
    def cost(cls):
        return 0
    
    # core events
    def get_event_variables(self):
        return {
            "player": self.parent,
            "item": self
        }

    def on_purchase(self, *args, **kwargs):
        """"""
        call_event("item_purchased", [], self.get_event_variables())

    # core functionality
    def call_events(self, event_name, *args, **kwargs):
        for callback in self._events[event_name]:
            callback(*args, **kwargs)

    def call_clientcommands(self, command_name, *args, **kwargs):
        for callback in self._clientcommands[command_name]:
            callback(*args, **kwargs)

    @classproperty
    def categories(cls):
        if len(cls.__categories) == 0:
            for subcls in cls.iter_subclasses():
                if hasattr(subcls, "category"):
                    cls.__categories.add(subcls.category)
        return cls.__categories

    @classmethod
    def iter_items_in_category(cls, category):
        for subcls in cls.iter_subclasses():
            if subcls.category == category:
                yield subcls