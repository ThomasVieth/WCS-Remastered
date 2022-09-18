"""

"""

## python imports

from random import randint

## source.python imports

from listeners.tick import Repeat

## warcraft.package imports

from warcraft.commands.messages import send_wcs_saytext_by_index
from warcraft.item import Item, ItemCategory
from warcraft.registration import events, clientcommands
from warcraft.utility import classproperty

## __all__ declaration

__all__ = (
    "MithrilArmor",
    "BeltOfVitality",
    "RingOfDefense",
    "GemOfLife",
    "NecklaceOfImmunity"
)

## category definition

defensive_category = ItemCategory("Defensive", sort_key=1)

## mithrilarmor declaration

class MithrilArmor(Item):
    category = defensive_category
    cost = 1750
    description = "Reduces damage taken from enemy attacks by 6-10 health."

    _msg_purchase = '{GREEN}Purchased {BLUE}Mithril Armor.'
    _msg_spawn = '{{BLUE}}Mithril Armor {{PALE_GREEN}}prevented {{DULL_RED}}{damage} {{PALE_GREEN}}last round.'

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
        self.total_damage_prevented = 0
        player.cash -= self.cost
        send_wcs_saytext_by_index(self._msg_purchase, player.index)

    @events('player_spawn')
    def _on_player_spawn(self, player, **kwargs):
        send_wcs_saytext_by_index(self._msg_spawn.format(damage=int(self.total_damage_prevented)), player.index)

    @events('player_pre_victim')
    def _on_player_pre_victim(self, info, **kwargs):
        reduction = randint(6, 11)
        info.damage -= reduction
        self.total_damage_prevented += reduction

    @events('player_death', 'player_suicide')
    def _on_player_death(self, player, **kwargs):
        ## remove the item
        player.items.remove(self)

## beltofvitality declaration

class BeltOfVitality(Item):
    category = defensive_category
    cost = 2500
    description = "If low on health you'll slowly regenerate your health back up."

    _msg_purchase = '{GREEN}Purchased {BLUE}Belt of Vitality.'

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
        self.repeater = Repeat(self.on_cycle, args=(player, ))
        self.repeater.start(1)
        send_wcs_saytext_by_index(self._msg_purchase, player.index)

    def on_cycle(self, player):
        if player.health < 175:
            player.health += 5

    @events('player_death', 'player_suicide')
    def _on_player_death(self, player, **kwargs):
        self.repeater.stop()
        ## remove the item
        player.items.remove(self)

## ringofdefense declaration

class RingOfDefense(Item):
    category = defensive_category
    cost = 2500
    description = "Increases your armor by 125."

    _msg_purchase = '{GREEN}Purchased {BLUE}Ring of Defense.'

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
        player.armor += 125
        send_wcs_saytext_by_index(self._msg_purchase, player.index)

    @events('player_spawn')
    def _on_player_spawn(self, player, **kwargs):
        player.armor += 125

    @events('player_death', 'player_suicide')
    def _on_player_death(self, player, **kwargs):
        ## remove the item
        player.items.remove(self)

## gemoflife declaration

class GemOfLife(Item):
    category = defensive_category
    cost = 3000
    description = "Grants you an additional 50 health."

    _msg_purchase = '{GREEN}Purchased {BLUE}Gem of Life.'

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
        player.health += 50
        send_wcs_saytext_by_index(self._msg_purchase, player.index)

    @events('player_spawn')
    def _on_player_spawn(self, player, **kwargs):
        player.health += 50

    @events('player_death', 'player_suicide')
    def _on_player_death(self, player, **kwargs):
        ## remove the item
        player.items.remove(self)


## necklaceofimmunity declaration

class NecklaceOfImmunity(Item):
    category = defensive_category
    cost = 1200
    description = "Protects you from ultimates."

    _msg_purchase = '{GREEN}Purchased {BLUE}Necklace of Immunity.'

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
        player.ultimate_immune = True
        send_wcs_saytext_by_index(self._msg_purchase, player.index)

    @events('player_spawn')
    def _on_player_spawn(self, player, **kwargs):
        player.ultimate_immune = True

    @events('player_death', 'player_suicide')
    def _on_player_death(self, player, **kwargs):
        player.ultimate_immune = False
        ## remove the item
        player.items.remove(self)