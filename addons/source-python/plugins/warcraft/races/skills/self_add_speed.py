"""

"""

## warcraft.package imports

from warcraft.registration import events
from warcraft.skill import Skill

## __all__ declaration

__all__ = ("AddSpeedSkill", )

## speedskill declaration

class AddSpeedSkill(Skill):

    @property
    def base_speed_addition(self):
        return 0.06 * self.level

    @events('player_spawn')
    def _on_player_spawn(self, player, **kwargs):
        if self.level == 0:
            return

        player.speed += self.base_speed_addition