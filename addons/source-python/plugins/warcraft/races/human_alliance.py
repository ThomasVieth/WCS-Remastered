"""

"""

## python imports

from random import randint
from time import time

## source.python imports

from engines.sound import StreamSound
from engines.trace import engine_trace
from engines.trace import ContentMasks
from engines.trace import GameTrace
from engines.trace import Ray
from engines.trace import TraceFilterSimple
from filters.players import PlayerIter
from messages import Shake, SayText2

## warcraft.package imports

from warcraft.commands.messages import send_wcs_saytext_by_index
from warcraft.race import Race
from warcraft.registration import events, clientcommands
from warcraft.skill import Skill
from warcraft.utility import classproperty, CooldownDict

## __all__ declaration

__all__ = ("HumanAlliance", )

## HumanAlliance declaration

teleport_sound = StreamSound('source-python/warcraft/timeleap.mp3', download=True)

class HumanAlliance(Race):

    @classproperty
    def description(cls):
        return 'Recoded Human Alliance. (Kryptonite)'

    @classproperty
    def max_level(cls):
        return 40

    @classproperty
    def requirement_sort_key(cls):
        return 2

@HumanAlliance.add_skill
class Invisibility(Skill):

    @classproperty
    def description(cls):
        return "Gain control of Invisibility by the Kirin Tor."

    @classproperty
    def max_level(cls):
        return 8

    def _calculate_invis(self):
        return 255 - (20 * self.level)

    _msg_a = '{{DULL_RED}}Removed {{RED}}{name}\'s {{BLUE}}Invisibility{{GREEN}}!'
    _msg_b = '{PALE_GREEN}Your {BLUE}Invisibility {PALE_GREEN}has been {RED}removed{PALE_GREEN}...'

    @events('player_spawn', 'skill_level_up')
    def _on_player_spawn_give_invis(self, player, **eargs):
        color = player.color
        color.a = self._calculate_invis()
        player.color = color

    @events('player_attack')
    def _on_player_hurt_remove_invis(self, attacker, victim, **eargs):
        if victim.color.a < 255:
            color = victim.color
            color.a += 30 if color.a <= 225 else (255 - color.a)
            victim.color = color

            send_wcs_saytext_by_index(self._msg_a.format(name=victim.name), attacker.index)
            send_wcs_saytext_by_index(self._msg_b, victim.index)

@HumanAlliance.add_skill
class CauterizeWounds(Skill):

    @classproperty
    def description(cls):
        return 'You and your allies gain increased health.'

    @classproperty
    def max_level(cls):
        return 8

    @events('player_spawn')
    def _on_player_spawn_give_team_health(self, player, **eargs):
        team = ['t', 'ct'][player.team-2]
        for ally in PlayerIter(is_filters=team):
            ally.health += 5 * self.level


@HumanAlliance.add_skill
class FrostBomb(Skill):

    @classproperty
    def description(cls):
        return 'Upon damaging an enemy, shake them.'

    @classproperty
    def max_level(cls):
        return 8

    _msg_a = '{{GREEN}}Shaken {{RED}}{name} {{PALE_GREEN}}with {{BLUE}}Frost Bomb{{GREEN}}!'

    @events('player_attack')
    def _on_player_hurt_shake(self, attacker, victim, **eargs):
        if randint(1, 100) <= 20 + self.level:
            Shake(100, 1.5).send(victim.index)
            send_wcs_saytext_by_index(self._msg_a.format(name=victim.name), attacker.index)

@HumanAlliance.add_skill
class Teleport(Skill):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.cooldowns = CooldownDict()
    
    @classproperty
    def description(cls):
        return 'Teleport a distance infront of yourself, if not obstructed. Ultimate.'

    @classmethod
    def is_available(cls, player):
        return player.race.level > 8

    @classproperty
    def max_level(cls):
        return 8

    _msg_c = '{{BLUE}}Teleport {{PALE_GREEN}}is on cooldown for {{DULL_RED}}{time:0.1f} {{PALE_GREEN}}seconds.'
    _msg_f = '{GREEN}Cannot {BLUE}teleport {DULL_RED}due to obstruction.'

    @events('player_spawn')
    def _on_player_spawn_reset(self, player, **eargs):
        self.cooldowns['ultimate'] = 4

    def _get_trace(self, start, end, mask, player, trace):
        engine_trace.trace_ray(Ray(start, end),
            ContentMasks.ALL, TraceFilterSimple((player, )), trace)
        return trace

    @clientcommands('ultimate')
    def _on_player_use_ultimate(self, player, **eargs):
        _cooldown = self.cooldowns['ultimate']
        if _cooldown <= 0:
            distance = 300 + 50 * self.level
            view_vector = player.view_vector
            origin = player.origin
            teleport_vector = origin + (view_vector * distance)

            ## These vectors should create a line diagonally through the player model,
            ## allowing us to see if the teleport is safe.
            trace_vector1 = teleport_vector.copy()
            trace_vector2 = teleport_vector.copy()
            trace_vector1.z += 80
            trace_vector1.x += 20
            trace_vector1.y -= 20
            trace_vector2.x -= 20
            trace_vector2.y += 20
            origin.z += 60

            view = self._get_trace(
                        origin, teleport_vector, ContentMasks.ALL, player,
                        GameTrace()
                        )

            trace = self._get_trace(
                        trace_vector1, trace_vector2, ContentMasks.ALL, player,
                        GameTrace()
                        )

            if trace.did_hit() or view.did_hit():
                send_wcs_saytext_by_index(self._msg_f, player.index)
            else:
                player.teleport(teleport_vector, None, None)
                teleport_sound.play(player.index)
                self.cooldowns['ultimate'] = 8 - (0.5 * self.level)
        else:
            send_wcs_saytext_by_index(self._msg_c.format(time=_cooldown), player.index)