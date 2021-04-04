"""

"""

## warcraft.package imports

from warcraft.commands.messages import send_wcs_saytext_by_index
from warcraft.item import Item
from warcraft.registration import events, clientcommands
from warcraft.utility import classproperty

## __all__ declaration

__all__ = (
    "BootsOfSpeed",
    "GryphonFeather",
    "LeaperPotion",
    "CloakOfShadows",
    "HeartOfThePhoenix"
)

## bootsofspeed declaration

class BootsOfSpeed(Item):
    category = "Enhancements"
    cost = 2500
    description = "Increases your speed by 25% of the base speed."

    _msg_purchase = '{GREEN}Purchased {BLUE}Boots of Speed.'

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
        player.speed += 0.25
        send_wcs_saytext_by_index(self._msg_purchase, player.index)

    @events('player_spawn')
    def _on_player_spawn(self, player, **kwargs):
        player.speed += 0.25

    @events('player_death')
    def _on_player_death(self, player, **kwargs):
        ## remove the item
        player.items.remove(self)

## gryphonfeather declaration

class GryphonFeather(Item):
    category = "Enhancements"
    cost = 2500
    description = "Reduces your base gravity by 35%."

    _msg_purchase = '{GREEN}Purchased {BLUE}Gryphon Feather.'

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
        player.gravity -= 0.35
        send_wcs_saytext_by_index(self._msg_purchase, player.index)

    @events('player_spawn')
    def _on_player_spawn(self, player, **kwargs):
        player.gravity -= 0.35

    @events('player_death')
    def _on_player_death(self, player, **kwargs):
        ## remove the item
        player.items.remove(self)

## leaperpotion declaration

class LeaperPotion(Item):
    category = "Enhancements"
    cost = 3000
    description = "Increases the length of your jumps."

    _msg_purchase = '{GREEN}Purchased {BLUE}Leaper Potion.'

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

    @events('player_jump')
    def _on_player_jump(self, player, **kwargs):
        player.push(100, 100)

    @events('player_death')
    def _on_player_death(self, player, **kwargs):
        ## remove the item
        player.items.remove(self)

## cloakofshadows declaration

class CloakOfShadows(Item):
    category = "Enhancements"
    cost = 3500
    description = "Causes you to become 70% invisible."

    _msg_purchase = '{GREEN}Purchased {BLUE}Cloak of Shadows.'

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
        color = player.color
        color.a = (255 * 0.7)
        player.color = color
        send_wcs_saytext_by_index(self._msg_purchase, player.index)

    @events('player_spawn')
    def _on_player_spawn(self, player, **kwargs):
        color = player.color
        color.a = (255 * 0.7)
        player.color = color

    @events('player_death')
    def _on_player_death(self, player, **kwargs):
        ## remove the item
        player.items.remove(self)

## heartofthephoenix declaration

class HeartOfThePhoenix(Item):
    category = "Enhancements"
    cost = 5000
    description = "Respawns you if you're dead, or respawns you when you die."

    _msg_instant = '{GREEN}Respawning {PALE_GREEN}using {BLUE}Heart of the Phoenix.'
    _msg_purchase = '{GREEN}Purchased {BLUE}Heart of the Phoenix.'

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
        if player.dead:
            player.spawn()
            send_wcs_saytext_by_index(self._msg_instant, player.index)
            ## remove the item to not trigger upon death
            player.items.remove(self)
        else:
            send_wcs_saytext_by_index(self._msg_purchase, player.index)

    @events('player_death')
    def _on_player_death(self, player, **kwargs):
        Delay(1, player.spawn)
        ## remove the item
        player.items.remove(self)