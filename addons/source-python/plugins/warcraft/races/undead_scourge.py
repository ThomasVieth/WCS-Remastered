"""

"""

## source.python imports

from effects.base import TempEntity
from engines.precache import Model

## warcraft.package imports

from warcraft.commands.messages import send_wcs_saytext_by_index
from warcraft.race import Race
from warcraft.registration import events
from warcraft.utility import classproperty

## warcraft.skills imports

from .skills.enemy_limited_lifesteal import LifestealSkill
from .skills.self_health_scales_speed import HealthScalingSpeedSkill
from .skills.self_reduce_gravity import ReduceGravitySkill
from .skills.self_explode import ExplosionSkill

## __all__ declaration

__all__ = ("UndeadScourge", )

## undeadscourge declaration

class UndeadScourge(Race):
    laser = Model("sprites/lgtning.vmt", True)  

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.beam = TempEntity('BeamRingPoint', alpha=255, red=255, green=0, blue=0,
            life_time=1.0, model_index=self.laser.index, start_width=7, end_width=7,
            frame_rate=255, halo_index=self.laser.index, speed=1)

    @classproperty
    def description(cls):
        return 'Recoded Undead Scourge. (Kryptonite)'

    @classproperty
    def max_level(cls):
        return 99

    @classproperty
    def requirement_sort_key(cls):
        return 1

    @events('player_spawn')
    def _on_player_spawn(self, player, **kwargs):
        location = player.origin
        location2 = location.copy()
        location2.z += 20
        location3 = location2.copy()
        location3.z += 20
        location4 = location3.copy()
        location4.z += 20
        self.beam.create(center=location, start_radius=60, end_radius=80)
        self.beam.create(center=location2, start_radius=70, end_radius=90)
        self.beam.create(center=location3, start_radius=80, end_radius=100)
        self.beam.create(center=location4, start_radius=80, end_radius=100)


@UndeadScourge.add_skill
class VampiricAura(Lifesteal):

    @classproperty
    def description(cls):
        return "Attacking an enemy causes you to steal their life."

    @classproperty
    def max_level(cls):
        return 8


@UndeadScourge.add_skill
class UnholyAura(HealthScalingSpeedSkill):

    @classproperty
    def description(cls):
        return "Increase your base speed, and scales when health changes."

    @classproperty
    def max_level(cls):
        return 8


@UndeadScourge.add_skill
class Levitation(ReduceGravitySkill):

    @classproperty
    def description(cls):
        return "Reduce your current gravity and damage taken when jumping."

    @classproperty
    def max_level(cls):
        return 8

    @property
    def reduction(self):
        return 0.06 * self.level

    _msg_a = '{{PALE_GREEN}}Reduced {{DULL_RED}}damage taken {{PALE_GREEN}}from {{RED}}{name}.'

    @events('player_pre_victim')
    def _on_player_pre_victim(self, attacker, victim, info, **eargs):
        if self.level == 0:
            return

        if victim.ground_entity == -1:
            info.damage *= 1 - 0.06 * self.level
            send_wcs_saytext_by_index(self._msg_a.format(name=attacker.name), victim.index)
            ricochet = TempEntity('Armor Ricochet', position=victim.origin)
            ricochet.create()


@UndeadScourge.add_skill
class SuicideBomber(ExplosionSkill):

    @classproperty
    def description(cls):
        return "Explode upon death causing enemies to bleed."

    @classproperty
    def max_level(cls):
        return 8