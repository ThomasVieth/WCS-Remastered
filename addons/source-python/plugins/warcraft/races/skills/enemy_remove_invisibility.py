"""

"""

## python imports

from random import randint

## warcraft.package imports

from warcraft.registration import events
from warcraft.skill import Skill

## __all__ declaration

__all__ = ("RemoveInvisibilitySkill", )

## removeinvisibilityskill declaration

class RemoveInvisibilitySkill(Skill):

    _msg_a = '{{DULL_RED}}Removed {{RED}}{name}\'s {{BLUE}}Invisibility{{GREEN}}!'
    _msg_b = '{PALE_GREEN}Your {BLUE}Invisibility {PALE_GREEN}has been {RED}removed{PALE_GREEN}...'

    @property
    def chance(self):
        return 30

    @events('player_attack')
    def _on_player_hurt_remove_invis(self, attacker, victim, **kwargs):
        if victim.color.a < 255 and randint(0, 101) < self.chance:
            color = victim.color
            color.a += 30 if color.a <= 225 else (255 - color.a)
            victim.color = color

            send_wcs_saytext_by_index(self._msg_a.format(name=victim.name), attacker.index)
            send_wcs_saytext_by_index(self._msg_b, victim.index)
