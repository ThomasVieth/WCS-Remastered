"""

"""

## warcraft.package imports

from warcraft.item import Item
from warcraft.registration import events, clientcommands

## __all__ declaration

__all__ = ("BootsOfSpeed", )

## bootsofspeed declaration

class BootsOfSpeed(Item):
    category = "Enhancements"

    @classmethod
    def is_available(cls, player):
        return player.cash >= 3200

    def on_purchase(self, player):
        player.cash -= 3200
        player.speed += 0.2

    @events('player_spawn')
    def _on_player_spawn(self, player, **kwargs):
        player.speed += 0.2

    @events('player_death')
    def _on_player_death(self, player, **kwargs):
        ## remove the item
        player.items.remove(self)