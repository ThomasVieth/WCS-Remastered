
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

__all__ = ("LaserLightShow", )

## LaserLightShow declaration

class LaserLightShow(Race):

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

@LaserLightShow.add_skill
class LaserShot(Skill):
    
    @classproperty
    def description(cls):
        return 'Extra Damage'

    @classproperty
    def max_level(cls):
        return 4

    @classmethod
    def is_available(cls, player):
        return player.race.level > 0

    @events('player_pre_attack')
    def _on_player_attack(self, player, **kwargs):
        ## Code goes here...

@LaserLightShow.add_skill
class LaserLauncher(Skill):
    
    @classproperty
    def description(cls):
        return 'Launch Up Enemies'

    @classproperty
    def max_level(cls):
        return 4

    @classmethod
    def is_available(cls, player):
        return player.race.level > 0

    @events('player_attack')
    def _on_player_attack(self, player, **kwargs):
        ## Code goes here...

@LaserLightShow.add_skill
class LaserShock(Skill):
    
    @classproperty
    def description(cls):
        return 'Freeze Enemies'

    @classproperty
    def max_level(cls):
        return 4

    @classmethod
    def is_available(cls, player):
        return player.race.level > 0

    @events('player_attack')
    def _on_player_attack(self, player, **kwargs):
        ## Code goes here...

@LaserLightShow.add_skill
class LaserFast(Skill):
    
    @classproperty
    def description(cls):
        return 'Move Really Fast and Jump High'

    @classproperty
    def max_level(cls):
        return 4

    @classmethod
    def is_available(cls, player):
        return player.race.level > 0

    @events('player_spawn')
    def _on_player_spawn(self, player, **kwargs):
        ## Code goes here...

@LaserLightShow.add_skill
class LaserBullet(Skill):
    
    @classproperty
    def description(cls):
        return 'Laser Bullets'

    @classproperty
    def max_level(cls):
        return 4

    @classmethod
    def is_available(cls, player):
        return player.race.level > 8

    @events('player_ultimate')
    def _on_player_ultimate(self, player, **kwargs):
        ## Code goes here...

@LaserLightShow.add_skill
class LaserShield(Skill):
    
    @classproperty
    def description(cls):
        return 'Shield Yourself'

    @classproperty
    def max_level(cls):
        return 4
