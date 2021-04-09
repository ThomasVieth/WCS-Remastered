"""

"""

## source.python imports

from entities.constants import MoveType
from listeners.tick import Delay
from messages import SayText2
from players.constants import PlayerButtons

## warcraft.package imports

from warcraft.registration import events, clientcommands
from warcraft.skill import Skill
from warcraft.utility import classproperty

## __all__ declaration

__all__ = ("ReduceGravitySkill", )

## reducegravity declaration

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

            if self.state == MoveType.LADDER:
                Delay(0.5, self.reduce_gravity, args=(player, self.reduction))
            self.state = player.move_type

    @events('player_spawn')
    def _on_player_spawn(self, player, **kwargs):
        Delay(0.5, self.reduce_gravity, args=(player, self.reduction))