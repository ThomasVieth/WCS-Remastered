"""

"""

## python imports

from random import randint

## warcraft.package imports

from warcraft.commands.messages import send_wcs_saytext_by_index
from warcraft.item import Item
from warcraft.registration import events, clientcommands
from warcraft.utility import classproperty

## __all__ declaration

__all__ = (
    "AppearenceDust",
    "RazorClaws",
    "BottledFlame"
)

## appearnencedust declaration

class AppearenceDust(Item):
    category = "Offensive"
    cost = 1500
    description = "Your attacks makes your victims visible again."

    _msg_purchase = '{GREEN}Purchased {BLUE}Appearence Dust.'

    @classmethod
    def is_available(cls, player):
        return player.cash >= cls.cost and not player.dead

    @classproperty
    def requirement_string(cls):
        return "${}".format(cls.cost)

    @classproperty
    def requirement_sort_key(cls):
        return cls.cost

    def on_purchase(self, player):
        super().on_purchase(player)
        player.cash -= self.cost
        send_wcs_saytext_by_index(self._msg_purchase, player.index)

    @events('player_attack')
    def _on_player_attack(self, victim, **kwargs):
        color = victim.color
        color.a = 255
        victim.color = color

    @events('player_death')
    def _on_player_death(self, player, **kwargs):
        ## remove the item
        player.items.remove(self)

## razorclaws declaration

class RazorClaws(Item):
    category = "Offensive"
    cost = 2500
    description = "Your melee attacks deals 15-28 more damage."

    _msg_purchase = '{GREEN}Purchased {BLUE}Razor Claws.'

    @classmethod
    def is_available(cls, player):
        return player.cash >= cls.cost and not player.dead

    @classproperty
    def requirement_string(cls):
        return "${}".format(cls.cost)

    @classproperty
    def requirement_sort_key(cls):
        return cls.cost

    def on_purchase(self, player):
        super().on_purchase(player)
        player.cash -= self.cost
        send_wcs_saytext_by_index(self._msg_purchase, player.index)

    @events('player_attack')
    def _on_player_attack(self, info, weapon, **kwargs):
        if weapon == "weapon_knife":
            extra_damage = randint(15, 29)
            info.damage += extra_damage

    @events('player_death')
    def _on_player_death(self, player, **kwargs):
        ## remove the item
        player.items.remove(self)

## bottledflame declaration

class BottledFlame(Item):
    category = "Offensive"
    cost = 2500
    description = "Your attacks sets your target ablaze for 3 seconds."

    _msg_purchase = '{GREEN}Purchased {BLUE}Bottled Flame.'

    @classmethod
    def is_available(cls, player):
        return player.cash >= cls.cost and not player.dead

    @classproperty
    def requirement_string(cls):
        return "${}".format(cls.cost)

    @classproperty
    def requirement_sort_key(cls):
        return cls.cost

    def on_purchase(self, player):
        super().on_purchase(player)
        player.cash -= self.cost
        send_wcs_saytext_by_index(self._msg_purchase, player.index)

    @events('player_attack')
    def _on_player_attack(self, victim, **kwargs):
        victim.ignite_lifetime(3)

    @events('player_death')
    def _on_player_death(self, player, **kwargs):
        ## remove the item
        player.items.remove(self)