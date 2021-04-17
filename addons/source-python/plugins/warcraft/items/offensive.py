"""

"""

## python imports

from random import randint

## source.python imports

from effects.base import TempEntity

## warcraft.package imports

from warcraft.commands.messages import send_wcs_saytext_by_index
from warcraft.item import Item
from warcraft.players import player_dict
from warcraft.registration import events, clientcommands
from warcraft.utility import classproperty

## __all__ declaration

__all__ = (
    "DustOfAppearence",
    "ClawsOfAttack",
    "OrbOfFrost",
    "Flamethrower",
    "MaskOfDeath",
    "BlowUpBaby"
)

## dustofappearnence declaration

class DustOfAppearence(Item):
    category = "Offensive"
    cost = 1500
    description = "Your attacks makes your victims visible again."

    _msg_purchase = '{GREEN}Purchased {BLUE}Dust of Appearence.'

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

    @events('player_attack')
    def _on_player_attack(self, victim, **kwargs):
        color = victim.color
        color.a = 255
        victim.color = color

    @events('player_death', 'player_suicide')
    def _on_player_death(self, player, **kwargs):
        ## remove the item
        player.items.remove(self)

## clawsofattack declaration

class ClawsOfAttack(Item):
    category = "Offensive"
    cost = 2500
    description = "Your melee attacks deals 15-28 more damage."

    _msg_purchase = '{GREEN}Purchased {BLUE}Claws of Attack.'

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

    @events('player_attack')
    def _on_player_attack(self, info, weapon, **kwargs):
        if weapon == "weapon_knife":
            extra_damage = randint(15, 29)
            info.damage += extra_damage

    @events('player_death', 'player_suicide')
    def _on_player_death(self, player, **kwargs):
        ## remove the item
        player.items.remove(self)

## orboffrost declaration

class OrbOfFrost(Item):
    category = "Offensive"
    cost = 3500
    description = "Attacking an enemy makes them 60% slower. 33% chance."

    _msg_purchase = '{GREEN}Purchased {BLUE}Orb of Frost.'


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

    @events('player_attack')
    def _on_player_attack(self, victim, **kwargs):
        if victim.dead or victim.is_slowed or randint(0, 101) > 33:
            return

        current_speed = victim.speed
        victim.speed -= 0.6
        victim.is_slowed = True
        victim.delay(2, victim.__setattr__, args=('speed', current_speed))
        Delay(2, victim.__setattr__, args=('is_slowed', False))

    @events('player_death', 'player_suicide')
    def _on_player_death(self, player, **kwargs):
        ## remove the item
        player.items.remove(self)


## flamethrower declaration

class Flamethrower(Item):
    category = "Offensive"
    cost = 5000
    description = "Your attacks sets your target ablaze for 3 seconds."

    _msg_purchase = '{GREEN}Purchased {BLUE}Flamethrower.'

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

    @events('player_attack')
    def _on_player_attack(self, victim, **kwargs):
        victim.ignite_lifetime(3)

    @events('player_death', 'player_suicide')
    def _on_player_death(self, player, **kwargs):
        ## remove the item
        player.items.remove(self)

## mask of death

class MaskOfDeath(Item):
    category = "Offensive"
    cost = 3200
    description = "Leeches 20% of damage you do. 40% chance."

    _msg_purchase = '{GREEN}Purchased {DARK_BLUE}Mask of Death.'

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

    @events('player_attack')
    def _on_player_attack(self, attacker, dmg_health, **kwargs):
        health = int(dmg_health * 0.2)
        attacker.health += health

    @events('player_death', 'player_suicide')
    def _on_player_death(self, player, **kwargs):
        ## remove the item
        player.items.remove(self)

## blow up baby

class BlowUpBaby(Item):
    category = "Offensive"
    cost = 5000
    description = "Explode when die."

    _msg_purchase = '{GREEN}Purchased {DULL_RED}Blow Up Baby.'

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.explosion = TempEntity('Explosion',
            magnitude=100, scale=40, radius=self.range)

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

    @property
    def range(self):
        return 200

    @property
    def magnitude(self):
        return 35

    @events('player_death', 'player_suicide')
    def player_death(self, player, **kwargs):
        for target in player_dict.values():
            if player.origin.get_distance(target.origin) <= self.range and target.team != player.team:
                target.take_damage(self.magnitude, attacker_index=player.index, skip_hooks=True)
                send_wcs_saytext_by_index(self._msg_a.format(name=target.name), player.index)

        self.explosion.create(origin=player.origin)

        ## remove the item
        player.items.remove(self)