"""

"""

## source.python imports

from entities.constants import MoveType
from entities.entity import Entity
from listeners.tick import Delay
from mathlib import Vector
from messages import SayText2
from players.constants import PlayerButtons

## warcraft.package imports

from warcraft.commands.messages import send_wcs_saytext_by_index
from warcraft.item import Item, ItemCategory
from warcraft.registration import events, clientcommands
from warcraft.utility import classproperty

## __all__ declaration

__all__ = (
    "BootsOfSpeed",
    "GryphonFeather",
    "Longjump",
    "CloakOfShadows",
    "AnkhOfReincarnation",
    "ScrollOfRespawning",
    "Amulet of the Cat"
)

## category definition

enhancements_category = ItemCategory("Enhancements", sort_key=2)

## bootsofspeed declaration

class BootsOfSpeed(Item):
    category = enhancements_category
    cost = 2500
    description = "Increases your speed by 25% of the base speed."

    _msg_purchase = '{GREEN}Purchased {BLUE}Boots of Speed.'

    @classmethod
    def is_available(cls, player):
        item_count = sum(isinstance(item, cls) for item in player.items)
        return player.cash >= cls.cost and not player.dead and item_count < 1

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

    @events('player_death', 'player_suicide')
    def _on_player_death(self, player, **kwargs):
        ## remove the item
        player.items.remove(self)

## gryphonfeather declaration

class GryphonFeather(Item):
    category = enhancements_category
    cost = 2500
    description = "Reduces your base gravity by 35%."

    _msg_purchase = '{GREEN}Purchased {BLUE}Gryphon Feather.'

    @classmethod
    def is_available(cls, player):
        item_count = sum(isinstance(item, cls) for item in player.items)
        return player.cash >= cls.cost and not player.dead and item_count < 1

    @classproperty
    def requirement_string(cls):
        return "${}".format(cls.cost)

    @classproperty
    def requirement_sort_key(cls):
        return cls.cost

    @property
    def min_gravity(self):
        return 0.1
    
    @property
    def reduction(self):
        return 0.35

    def reduce_gravity(self, player, value):
        if player.gravity < self.min_gravity:
            player.gravity = max(1 - value, self.min_gravity)
            return
        player.gravity = max(player.gravity - value, self.min_gravity)

    def on_purchase(self, player):
        super().on_purchase(player)
        player.cash -= self.cost
        self.reduce_gravity(player, self.reduction)
        self.state = player.move_type
        send_wcs_saytext_by_index(self._msg_purchase, player.index)    

    @events('player_pre_run_command')
    def _on_player_run_command(self, player, usercmd, **kwargs):
        if (usercmd.buttons & PlayerButtons.FORWARD
            or usercmd.buttons & PlayerButtons.BACK
            or usercmd.buttons & PlayerButtons.MOVELEFT
            or usercmd.buttons & PlayerButtons.MOVERIGHT
            or usercmd.buttons & PlayerButtons.JUMP):
            if self.state == player.move_type:
                return

            if self.state == MoveType.LADDER:
                self.reduce_gravity(player, self.reduction)
            self.state = player.move_type

    @events('player_spawn')
    def _on_player_spawn(self, player, **kwargs):
        Delay(0.5, self.reduce_gravity, args=(player, self.reduction))

    @events('player_death', 'player_suicide')
    def _on_player_death(self, player, **kwargs):
        ## remove the item
        player.items.remove(self)

## longjump declaration

class Longjump(Item):
    category = enhancements_category
    cost = 3000
    description = "Increases the length of your jumps."

    _msg_purchase = '{GREEN}Purchased {BLUE}Leaper Potion.'

    @classmethod
    def is_available(cls, player):
        item_count = sum(isinstance(item, cls) for item in player.items)
        return player.cash >= cls.cost and not player.dead and item_count < 1

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
        velocity = Vector()
        player.get_velocity(velocity, None)
        velocity.x *= 2
        velocity.y *= 2
        velocity.z = 10
        player.base_velocity = velocity

    @events('player_death', 'player_suicide')
    def _on_player_death(self, player, **kwargs):
        ## remove the item
        player.items.remove(self)

## cloakofshadows declaration

class CloakOfShadows(Item):
    category = enhancements_category
    cost = 3500
    description = "Causes you to become 70% invisible."

    _msg_purchase = '{GREEN}Purchased {BLUE}Cloak of Shadows.'

    @classmethod
    def is_available(cls, player):
        item_count = sum(isinstance(item, cls) for item in player.items)
        return player.cash >= cls.cost and not player.dead and item_count < 1

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
        color.a = int(255 * 0.3)
        player.color = color
        send_wcs_saytext_by_index(self._msg_purchase, player.index)

    @events('player_spawn')
    def _on_player_spawn(self, player, **kwargs):
        color = player.color
        color.a = int(255 * 0.3)
        player.color = color

    @events('player_death', 'player_suicide')
    def _on_player_death(self, player, **kwargs):
        color = player.color
        color.a = 255
        player.color = color
        ## remove the item
        player.items.remove(self)

## secondaryclipenhancer declaration

class SecondaryClipEnhancer(Item):
    category = enhancements_category
    cost = 400
    description = "Gives you a 50 bullet clip for your secondary weapon."

    _msg_purchase = '{GREEN}Purchased {BLUE}Secondary Clip Enhancer.'

    @classmethod
    def is_available(cls, player):
        item_count = sum(isinstance(item, cls) for item in player.items)
        return player.cash >= cls.cost and item_count < 1

    @classproperty
    def requirement_string(cls):
        return "${}".format(cls.cost)

    @classproperty
    def requirement_sort_key(cls):
        return cls.cost

    def on_purchase(self, player):
        super().on_purchase(player)
        player.secondary.clip = 50
        player.items.remove(self)

## ankhofreincarnation declaration

class AnkhOfReincarnation(Item):
    category = enhancements_category
    cost = 2000
    description = "Weapons are saved upon death and given to you on spawn."

    _msg_purchase = '{GREEN}Purchased {BLUE}Ankh of Reincarnation.'

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.weapons = []

    @classmethod
    def is_available(cls, player):
        item_count = sum(isinstance(item, cls) for item in player.items)
        return player.cash >= cls.cost and not player.dead and item_count < 1

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

    def _force_drop_weapons(self, player):
        for index in player.weapon_indexes(not_filters='knife'):
            entity = Entity(index)
            player.drop_weapon(entity.pointer, None, None)

    @events('player_pre_victim')
    def _on_pre_death_obtain_weapons(self, victim, **kwargs):
        self.weapons = [Entity(index).class_name for index in victim.weapon_indexes(
                not_filters='knife')
            ]

    @events('player_spawn')
    def _on_respawn_give_weapons_and_remove(self, player, **kwargs):
        self._force_drop_weapons(player)
        for weapon in self.weapons:
            player.delay(0.2, player.give_named_item, args=(weapon, ))

        ## remove the item
        player.items.remove(self)

## scrollofrespawning declaration

class ScrollOfRespawning(Item):
    category = enhancements_category
    cost = 5000
    description = "Respawns you if you're dead, or respawns you when you die."

    _msg_instant = '{GREEN}Respawning {PALE_GREEN}using {BLUE}Heart of the Phoenix.'
    _msg_purchase = '{GREEN}Purchased {BLUE}Heart of the Phoenix.'

    @classmethod
    def is_available(cls, player):
        item_count = sum(isinstance(item, cls) for item in player.items)
        return player.cash >= cls.cost and item_count < 1

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

    @events('player_death', 'player_suicide')
    def _on_player_death(self, player, **kwargs):
        Delay(1, player.spawn)
        Delay(1, send_wcs_saytext_by_index, args=(self._msg_instant, player.index))
        ## remove the item
        player.items.remove(self)

## amuletofthecat

class AmuletOfTheCat(Item):
    category = enhancements_category
    cost = 1500
    description = "Mutes your footsteps to enemies. Crouch to enable (once)."

    _msg_purchase = '{GREEN}Purchased {BLUE}Amulet of the Cat.'

    @classmethod
    def is_available(cls, player):
        item_count = sum(isinstance(item, cls) for item in player.items)
        return player.cash >= cls.cost and item_count < 1

    @classproperty
    def requirement_string(cls):
        return "${}".format(cls.cost)

    @classproperty
    def requirement_sort_key(cls):
        return cls.cost

    def on_purchase(self, player):
        super().on_purchase(player)
        player.set_property_int("m_fFlags", 2)
        player.items.remove(self)