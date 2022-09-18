
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

__all__ = ("Automaton", )

## Automaton declaration

class Automaton(Race):

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

@Automaton.add_skill
class Weapondisintegrate(Skill):
    
    @classproperty
    def description(cls):
        return 'Disintegrate the attackers weapons apon your death'

    @classproperty
    def max_level(cls):
        return 4

    @classmethod
    def is_available(cls, player):
        return player.race.level > 0

    @events('player_death')
    def _on_player_death(self, player, **kwargs):
        ## Code goes here...

@Automaton.add_skill
class Confiscate(Skill):
    
    @classproperty
    def description(cls):
        return 'Take the enemies weapon'

    @classproperty
    def max_level(cls):
        return 4

    @classmethod
    def is_available(cls, player):
        return player.race.level > 0

    @events('player_victim')
    def _on_player_victim(self, player, **kwargs):
        ## Code goes here...

@Automaton.add_skill
class Automaticmedicsystem(Skill):
    
    @classproperty
    def description(cls):
        return 'Automaticaly restore your hp or a chance to get the attackers gun'

    @classproperty
    def max_level(cls):
        return 4

    @classmethod
    def is_available(cls, player):
        return player.race.level > 0

    @events('player_attack')
    def _on_player_attack(self, player, **kwargs):
        ## Code goes here...

@Automaton.add_skill
class AutomaticTargetSystem(Skill):
    
    @classproperty
    def description(cls):
        return 'Auto Aim.'

    @classproperty
    def max_level(cls):
        return 4

    @classmethod
    def is_available(cls, player):
        return player.race.level > 8

    @events('player_ultimate')
    def _on_player_ultimate(self, player, **kwargs):
        ## Code goes here...
