
"""

"""

## python imports

from random import randint

## source.python imports

## warcraft.package imports

from warcraft.commands.messages import send_wcs_saytext_by_index
from warcraft.players import player_dict
from warcraft.race import Race
from warcraft.registration import events, clientcommands
from warcraft.skill import Skill
from warcraft.utility import classproperty, CooldownDict

## __all__ declaration

__all__ = ("JihadJoe", )

## JihadJoe declaration

class JihadJoe(Race):

    @classproperty
    def description(cls):
        return ''

    @classproperty
    def max_level(cls):
        return 99

    @classproperty
    def requirement_sort_key(cls):
        return 1

    @classmethod
    def is_available(cls, player):
        return player.total_level > 0

@JihadJoe.add_skill
class Bombs(Skill):
    
    @classproperty
    def description(cls):
        return 'Critical grenade'

    @classproperty
    def max_level(cls):
        return 4

    @classmethod
    def is_available(cls, player):
        return player.race.level > 0

    @events('player_pre_attack')
    def _on_player_attack(self, player, **kwargs):
        ## Code goes here...

@JihadJoe.add_skill
class CreateBomb(Youneedthis)(Skill):
    
    @classproperty
    def description(cls):
        return 'Endless Grenades'

    @classproperty
    def max_level(cls):
        return 4

    @classmethod
    def is_available(cls, player):
        return player.race.level > 0

    @events('player_spawn')
    def _on_player_spawn(self, player, **kwargs):
        ## Code goes here...

@JihadJoe.add_skill
class Fanatacism(Skill):
    
    @classproperty
    def description(cls):
        return 'Devotion to mecca'

    @classproperty
    def max_level(cls):
        return 4

    @classmethod
    def is_available(cls, player):
        return player.race.level > 0

    @events('player_spawn')
    def _on_player_spawn(self, player, **kwargs):
        ## Code goes here...

@JihadJoe.add_skill
class NAPALM(Skill):
    
    @classproperty
    def description(cls):
        return 'Burning grenade'

    @classproperty
    def max_level(cls):
        return 4

    @classmethod
    def is_available(cls, player):
        return player.race.level > 0

    @events('player_attack')
    def _on_player_attack(self, player, **kwargs):
        ## Code goes here...

@JihadJoe.add_skill
class SuicideBomber(Skill):
    
    @classproperty
    def description(cls):
        return 'This is for allah!'

    @classproperty
    def max_level(cls):
        return 4

    @classmethod
    def is_available(cls, player):
        return player.race.level > 8

    @events('player_death')
    def _on_player_death(self, player, **kwargs):
        ## Code goes here...
