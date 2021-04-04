"""

"""

## warcraft.package imports

from warcraft.item import Item
from warcraft.registration import events, clientcommands
from warcraft.utility import classproperty

## __all__ declaration

__all__ = ("BootsOfSpeed", )

## bootsofspeed declaration

class BootsOfSpeed(Item):
    category = "Enhancements"
    cost = 3200

    @classmethod
    def is_available(cls, player):
        return player.cash >= cls.cost

    @classproperty
    def requirement_string(cls):
        return "${}".format(cls.cost)

    @classproperty
    def requirement_sort_key(cls):
        return cls.cost

    def on_purchase(self, player):
        super().on_purchase(player)
        player.cash -= self.cost
        player.speed += 0.2

    @events('player_spawn')
    def _on_player_spawn(self, player, **kwargs):
        player.speed += 0.2

    @events('player_death')
    def _on_player_death(self, player, **kwargs):
        ## remove the item
        player.items.remove(self)