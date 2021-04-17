"""

"""

## python imports

from random import randint

## source.python imports

from colors import Color
from effects.base import TempEntity
from engines.precache import Model
from engines.sound import Sound
from entities.constants import DamageTypes
from players.constants import HitGroup

## warcraft.package imports

from warcraft.commands.messages import send_wcs_saytext_by_index
from warcraft.players import player_dict
from warcraft.race import Race
from warcraft.registration import events, clientcommands
from warcraft.skill import Skill
from warcraft.utility import classproperty, CooldownDict

## warcraft.skills imports

from .skills.enemy_is_in_fov import IsInFOVSkill
from .skills.self_reduce_gravity import ReduceGravitySkill

## __all__ declaration

__all__ = ("Athena", )

## athena declaration

class Athena(Race):

    @classproperty
    def description(cls):
        return ''

    @classproperty
    def max_level(cls):
        return 99

    @classproperty
    def requirement_sort_key(cls):
        return 17

    @classmethod
    def is_available(cls, player):
        return player.total_level > 200

    @classproperty
    def requirement_string(cls):
        return "Total Level 200"


@Athena.add_skill
class AthenaSpear(Skill):
    model = Model("sprites/lgtning.vmt")

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.model._precache()
        self.effect = TempEntity('BeamRingPoint', model=self.model,
            start_radius=20, end_radius=500, life_time=3, start_width=100,
            end_width=100, spread=10, amplitude=0, red=255, green=105, blue=155,
            alpha=255, speed=50)

    
    @classproperty
    def description(cls):
        return 'Spear your enemy for 5-13 extra damage. 2-10% chance.'

    @classproperty
    def max_level(cls):
        return 4

    @property
    def chance(self):
        return 2 + (self.level * 2)

    @property
    def extra_damage(self):
        return 5 + (self.level * 2)

    _msg_a = '{{LIGHT_BLUE}}Athena\'s Spear {{PALE_GREEN}}dealt {{DULL_RED}}{damage} {{PALE_GREEN}}extra to {{RED}}{name}{{PALE_GREEN}}.'

    @events('player_pre_attack')
    def _on_player_pre_attack(self, attacker, victim, info, **kwargs):
        if victim.dead or randint(0, 101) > self.chance or self.level == 0:
            return

        damage = randint(5, self.extra_damage)
        info.damage += damage
        send_wcs_saytext_by_index(self._msg_a.format(damage=damage, name=victim.name), attacker.index)
        self.effect.create(center=victim.origin)

@Athena.add_skill
class GoldenHelmet(Skill):

    @classproperty
    def description(cls):
        return 'Immunity against headshots. 10-70% chance'

    @classproperty
    def max_level(cls):
        return 4

    @property
    def chance(self):
        return 10 + (self.level * 15)
    
    _msg_a = '{{YELLOW}}Golden Helmet {{PALE_GREEN}}evaded {{DULL_RED}}{damage:0.0f} {{PALE_GREEN}}damage.'

    @events('player_pre_victim')
    def _on_player_pre_victim(self, victim, info, **kwargs):
        if randint(1, 101) > self.chance or self.level == 0 or victim.hitgroup != HitGroup.HEAD:
            return

        send_wcs_saytext_by_index(self._msg_a.format(damage=info.damage), victim.index)
        info.damage = 0

@Athena.add_skill
class BrightEyed(ReduceGravitySkill):

    @classproperty
    def description(cls):
        return "Reduce your current gravity."

    @classproperty
    def max_level(cls):
        return 4

    @property
    def reduction(self):
        return 0.4 + (0.06 * self.level)

@Athena.add_skill
class MedusaGaze(IsInFOVSkill):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.cooldowns = CooldownDict()

    @classproperty
    def description(cls):
        return "Turn enemy players in view into stone, freezing then for 1-2 seconds. Ultimate."

    @classproperty
    def max_level(cls):
        return 4

    @property
    def duration(self):
        return 1 + (self.level * 0.25)

    @property
    def range(self):
        return 300 + (self.level * 50)

    _msg_a = '{{DARK_BLUE}}Medusa Gaze {{DULL_RED}}stunned {{RED}}{name} {{PALE_GREEN}}for {{DULL_RED}}{time:0.1f} seconds.'
    _msg_c = '{{DARK_BLUE}}Medusa Gaze {{PALE_GREEN}}is on cooldown for {{DULL_RED}}{time:0.1f} seconds.'
    _msg_f = '{DARK_BLUE}Medusa Gaze {PALE_GREEN}found no {RED}enemies.'

    @clientcommands('ultimate')
    def _on_player_ultimate(self, player, **kwargs):
        if self.level == 0:
            return

        _cooldown = self.cooldowns['ultimate']
        if _cooldown <= 0:
            location = player.origin
            hit = False
            for target in player_dict.values():
                in_fov = self.is_in_fov(player, target)
                distance = location.get_distance(target.origin)
                if target.team != player.team and in_fov and distance < self.range:
                    hit = True
                    target.stuck = True
                    color = target.color
                    target.color = Color(0, 0, 0, 255)
                    target.delay(self.duration, setattr, args=(target, 'stuck', False))
                    target.delay(self.duration, setattr, args=(target, 'color', color))
                    send_wcs_saytext_by_index(self._msg_a.format(name=target.name, time=self.duration), player.index)
            if hit:
                self.cooldowns['ultimate'] = 15
            else:
                send_wcs_saytext_by_index(self._msg_f, player.index)
        else:
            send_wcs_saytext_by_index(self._msg_c.format(time=_cooldown), player.index)