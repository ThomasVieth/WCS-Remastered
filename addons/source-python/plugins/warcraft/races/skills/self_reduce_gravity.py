"""

"""

## source.python imports

from entities.constants import MoveType
from listeners.tick import Delay
from players.constants import PlayerButtons

## warcraft.package imports

from warcraft.registration import events
from warcraft.skill import Skill

## __all__ declaration

__all__ = ("ReduceGravitySkill", )

## reducegravityskill declaration

class ReduceGravitySkill(Skill):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.state = self.parent.parent.move_type

    @property
    def min_gravity(self):
        return 0.1
    
    @property
    def reduction(self):
        return 0.05 * self.level

    def reduce_gravity(self, player, value):
        if player.gravity < self.min_gravity:
            player.gravity = max(1 - value, self.min_gravity)
            return
        player.gravity = max(player.gravity - value, self.min_gravity)

    @events('player_pre_run_command')
    def _on_player_run_command(self, player, usercmd, **kwargs):
        if (usercmd.buttons & PlayerButtons.FORWARD
            or usercmd.buttons & PlayerButtons.BACK
            or usercmd.buttons & PlayerButtons.MOVELEFT
            or usercmd.buttons & PlayerButtons.MOVERIGHT
            or usercmd.buttons & PlayerButtons.JUMP):
            if self.state == player.move_type:
                return

            if self.state == MoveType.LADDER and self.level > 0:
                Delay(0.5, self.reduce_gravity, args=(player, self.reduction))
            self.state = player.move_type

    @events('player_spawn')
    def _on_player_spawn(self, player, **kwargs):
        if self.level == 0:
            return
        Delay(0.5, self.reduce_gravity, args=(player, self.reduction))