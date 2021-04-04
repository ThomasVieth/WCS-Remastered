"""

"""

## python imports

from random import randint

## warcraft.package imports

from warcraft.commands.messages import send_wcs_saytext_by_index
from warcraft.item import Item
from warcraft.utility import classproperty

## __all__ declaration

__all__ = (
    "ScrollOfKnowledge",
    "TomeOfMinorExperience",
    "TomeOfLesserExperience",
    "TomeOfGreaterExperience",
    "TomeOfInsight"
)

## scrollofknowledge declaration

class ScrollOfKnowledge(Item):
    category = "Experience & Levels"
    cost = 1750
    description = "Gives you 50% chance to receive 50 or 100 experience."

    _msg_purchase1 = '{PALE_GREEN}You\'ve gained 50 experience.'
    _msg_purchase2 = '{PALE_GREEN}You\'ve gained 100 experience.'

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
        determiner = randint(0, 2)
        if determiner == 0:
            player.race.experience_up(50)
            send_wcs_saytext_by_index(self._msg_purchase1, player.index)
        else:
            player.race.experience_up(100)
            send_wcs_saytext_by_index(self._msg_purchase2, player.index)
        player.items.remove(self)

## tomeofminorexperience declaration

class TomeOfMinorExperience(Item):
    category = "Experience & Levels"
    cost = 2500
    description = "Grants your current race 100 experience."

    _msg_purchase = '{PALE_GREEN}You\'ve gained 100 experience.'

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
        player.race.experience_up(100)
        send_wcs_saytext_by_index(self._msg_purchase, player.index)
        player.items.remove(self)

## tomeoflesserexperience declaration

class TomeOfLesserExperience(Item):
    category = "Experience & Levels"
    cost = 5000
    description = "Grants your current race 200 experience."

    _msg_purchase = '{PALE_GREEN}You\'ve gained 200 experience.'

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
        player.race.experience_up(200)
        send_wcs_saytext_by_index(self._msg_purchase, player.index)
        player.items.remove(self)

## tomeofgreaterexperience declaration

class TomeOfGreaterExperience(Item):
    category = "Experience & Levels"
    cost = 10000
    description = "Grants your current race 400 experience."

    _msg_purchase = '{PALE_GREEN}You\'ve gained 400 experience.'

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
        player.race.experience_up(400)
        send_wcs_saytext_by_index(self._msg_purchase, player.index)
        player.items.remove(self)

## tomeofinsight declaration

class TomeOfInsight(Item):
    category = "Experience & Levels"
    cost = 12000
    description = "Receive 1 level in your current race."

    _msg_purchase = '{PALE_GREEN}You\'ve gained 1 level/s.'

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
        player.race.level_up(1)
        send_wcs_saytext_by_index(self._msg_purchase, player.index)
        player.items.remove(self)