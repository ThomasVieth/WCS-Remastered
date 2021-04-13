"""

"""

## python imports

from random import randint

## source.python imports

from messages import Shake

## warcraft.package imports

from warcraft.commands.messages import send_wcs_saytext_by_index
from warcraft.registration import events
from warcraft.skill import Skill

## __all__ declaration

__all__ = ("ShakeSkill", )

## shakeskill declaration

class ShakeSkill(Skill):

    _msg_a = '{{GREEN}}Shaken {{RED}}{name} {{PALE_GREEN}}with {{BLUE}}Frost Bomb{{GREEN}}!'

    @property
    def chance(self):
        return self.level * 8

    @property
    def duration(self):
        return 1.5
    
    @property
    def magnitude(self):
        return 100

    @events('player_attack')
    def _on_player_hurt_shake(self, attacker, victim, **eargs):
        if randint(1, 101) <= self.chance:
            Shake(self.magnitude, self.duration).send(victim.index)
            send_wcs_saytext_by_index(self._msg_a.format(name=victim.name), attacker.index)