"""

"""

## source.python imports

from engines.sound import StreamSound
from engines.trace import engine_trace
from engines.trace import ContentMasks
from engines.trace import GameTrace
from engines.trace import Ray
from engines.trace import TraceFilterSimple

## warcraft.package imports

from warcraft.commands.messages import send_wcs_saytext_by_index
from warcraft.registration import events, clientcommands
from warcraft.skill import Skill
from warcraft.utility import CooldownDict

## __all__ declaration

__all__ = ("TeleportSkill", )

## teleportskill declaration

teleport_sound = StreamSound('source-python/warcraft/timeleap.mp3', download=True)

class TeleportSkill(Skill):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.cooldowns = CooldownDict()

    _msg_c = '{{BLUE}}Teleport {{PALE_GREEN}}is on cooldown for {{DULL_RED}}{time:0.1f} {{PALE_GREEN}}seconds.'
    _msg_f = '{GREEN}Cannot {BLUE}teleport {DULL_RED}due to obstruction.'

    @property
    def cooldown(self):
        return 8 - (0.5 * self.level)

    @property
    def distance(self):
        return 300 + 50 * self.level

    @property
    def retry_distance(self):
        return 100 + 50 * self.level

    @events('player_spawn')
    def _on_player_spawn_reset(self, player, **eargs):
        self.cooldowns['ultimate'] = 4

    def _get_trace(self, start, end, mask, player, trace):
        engine_trace.trace_ray(Ray(start, end),
            ContentMasks.ALL, TraceFilterSimple((player, )), trace)
        return trace

    def validate_teleport(self, player, origin, teleport_vector):
        ## These vectors should create a line diagonally through the player model,
        ## allowing us to see if the teleport is safe.
        trace_vector1 = teleport_vector.copy()
        trace_vector2 = teleport_vector.copy()
        trace_vector1.z += 72
        trace_vector1.x += 26
        trace_vector1.y -= 26
        trace_vector2.x -= 26
        trace_vector2.y += 26

        check1 = self._get_trace(
                    origin, teleport_vector, ContentMasks.ALL, player,
                    GameTrace()
                    )

        check2 = self._get_trace(
                    trace_vector1, trace_vector2, ContentMasks.ALL, player,
                    GameTrace()
                    )

        return check1, check2

    @clientcommands('ultimate')
    def _on_player_use_ultimate(self, player, **eargs):
        _cooldown = self.cooldowns['ultimate']
        if _cooldown <= 0:
            view_vector = player.view_vector
            origin = player.origin.copy()
            teleport_vector = origin + (view_vector * self.distance)
            origin.z += 50

            check1, check2 = self.validate_teleport(player, origin, teleport_vector)

            if check1.did_hit() or check2.did_hit():
                teleport_vector = origin + (view_vector * self.retry_distance)
                check3, check4 = self.validate_teleport(player, origin, teleport_vector)
                if check3.did_hit() or check4.did_hit():
                    send_wcs_saytext_by_index(self._msg_f, player.index)
                else:
                    player.teleport(teleport_vector, None, None)
                    teleport_sound.play(player.index)
                    self.cooldowns['ultimate'] = self.cooldown
            else:
                player.teleport(teleport_vector, None, None)
                teleport_sound.play(player.index)
                self.cooldowns['ultimate'] = cooldown
        else:
            send_wcs_saytext_by_index(self._msg_c.format(time=_cooldown), player.index)