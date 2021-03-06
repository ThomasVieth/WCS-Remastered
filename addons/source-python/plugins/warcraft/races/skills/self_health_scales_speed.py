"""

"""

## warcraft.package imports

from warcraft.registration import events
from warcraft.skill import Skill

from .self_add_speed import AddSpeedSkill

## __all__ declaration

__all__ = ("HealthScalesSpeedSkill", )

## healthscalespeedskill declaration

class HealthScalesSpeedSkill(AddSpeedSkill):

    def scale_speed_calc(self, player):
        return round(player.health / 120, 2)

    @events('player_attack', 'player_victim')
    def _change_player_speed(self, player, **kwargs):
        if self.level == 0:
            return

        if player.health > 100:
            speed = max(self.scale_speed_calc(player), 1 + self.base_speed_addition)
            player.speed = speed