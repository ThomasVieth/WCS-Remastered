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

__all__ = ("Item", "ItemCategory", )

## item category class declaration

class ItemCategory:
    """Todo: Probably should be a tuple. Please ignore the lack of efficiency."""

    def __init__(self, name, sort_key):
        self.name = name
        self.sort_key = sort_key

## item class declaration

class Item(CallbackHandler, NamingHandler, SubclassFinder):
    """"""
    __categories = set()
    category = ItemCategory("No Category", sort_key=99)
    cost = 0

    def __init__(self, parent=None, *args, **kwargs):
        CallbackHandler.__init__(self, *args, **kwargs)

        self.parent = parent

    # core attributes
    @classmethod
    def is_available(cls, player) -> bool:
        """Returns whether or not a item should be available to the user."""
        return player.cash > 0

    @classproperty
    def description(cls):
        return "N/A"

    @classproperty
    def requirement_string(cls):
        return "$" + str(cls.cost)

    @classproperty
    def requirement_sort_key(cls):
        return cls.cost
    
    # core events
    def get_event_variables(self):
        return {
            "player": self.parent,
            "item": self
        }

    def on_purchase(self, *args, **kwargs):
        """"""
        call_event("item_purchased", [], self.get_event_variables())


    @classproperty
    def categories(cls):
        if len(cls.__categories) == 0:
            for subcls in cls.iter_subclasses():
                cls.__categories.add(subcls.category)
        sorted_categories = sorted(cls.__categories, key=lambda category: category.sort_key)
        return list(map(cls.__categories, lambda category: category.name))

    @classmethod
    def iter_items_in_category(cls, category):
        for subcls in cls.iter_subclasses():
            if subcls.category.name == category:
                yield subcls

    @classmethod
    def list_items_in_category(cls, category):
        items = list(cls.iter_items_in_category(category))
        return sorted(items, key=lambda x: x.requirement_sort_key)