"""

"""

## warcraft.package imports

from warcraft.registration import events
from warcraft.skill import Skill

## __all__ declaration

__all__ = ("InvisibilitySkill", )

## invisibilityskill declaration

class InvisibilitySkill(Skill):

    @property
    def alpha(self):
        return 255 - (20 * self.level)

    @events('player_death', 'player_suicide')
    def _on_player_death_remove_invis(self, player, **kwargs):
        color = player.color
        color.a = 255
        player.color = color

    @events('player_spawn', 'skill_level_up')
    def _on_player_spawn_give_invis(self, player, **kwargs):
        color = player.color
        color.a = self.alpha
        player.color = color