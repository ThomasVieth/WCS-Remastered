
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

__all__ = ("Mummy", )

## Mummy declaration

class Mummy(Race):

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

@Mummy.add_skill
class DeathBook(Skill):
    
    @classproperty
    def description(cls):
        return 'Gain Hp from killing the living.'

    @classproperty
    def max_level(cls):
        return 4

    @classmethod
    def is_available(cls, player):
        return player.race.level > 0

    @events('player_kill')
    def _on_player_kill(self, player, **kwargs):
        ## Code goes here...

@Mummy.add_skill
class FleshSteal(Skill):
    
    @classproperty
    def description(cls):
        return 'Steal the flesh right from the living.'

    @classproperty
    def max_level(cls):
        return 4

    @classmethod
    def is_available(cls, player):
        return player.race.level > 0

    @events('player_attack')
    def _on_player_attack(self, player, **kwargs):
        ## Code goes here...

@Mummy.add_skill
class BandageWrap(Skill):
    
    @classproperty
    def description(cls):
        return 'Your bandages absorb grenades.'

    @classproperty
    def max_level(cls):
        return 4

    @classmethod
    def is_available(cls, player):
        return player.race.level > 0

    @events('player_pre_victim')
    def _on_player_victim(self, player, **kwargs):
        ## Code goes here...

@Mummy.add_skill
class EmbalmedSkin(Skill):
    
    @classproperty
    def description(cls):
        return 'Your skin is too tough for knives.'

    @classproperty
    def max_level(cls):
        return 4

    @classmethod
    def is_available(cls, player):
        return player.race.level > 0

    @events('player_attack')
    def _on_player_attack(self, player, **kwargs):
        ## Code goes here...

@Mummy.add_skill
class Mummy'sBreath(Skill):
    
    @classproperty
    def description(cls):
        return 'Ancient poison breath.'

    @classproperty
    def max_level(cls):
        return 4

    @classmethod
    def is_available(cls, player):
        return player.race.level > 8

    @events('player_ultimate')
    def _on_player_ultimate(self, player, **kwargs):
        ## Code goes here...

@Mummy.add_skill
class SwarmofScarabs(Skill):
    
    @classproperty
    def description(cls):
        return 'Send scarabs after an enemy.'

    @classproperty
    def max_level(cls):
        return 4
