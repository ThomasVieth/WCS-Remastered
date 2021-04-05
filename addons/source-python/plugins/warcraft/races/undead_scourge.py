"""

"""

## python imports

from random import randint

## source.python imports

from effects.base import TempEntity
from engines.precache import Model
from filters.players import PlayerIter
from messages import SayText2
from weapons.manager import weapon_manager

## warcraft.package imports

from warcraft.commands.messages import send_wcs_saytext_by_index
from warcraft.race import Race
from warcraft.registration import events
from warcraft.skill import Skill
from warcraft.utility import classproperty

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
        return 32

    @events('player_spawn')
    def _on_player_spawn(self, player, **kwargs):
        location = player.origin
        location2 = location
        location2.z += 20
        location3 = location2
        location3.z += 20
        location4 = location3
        location4.z += 20
        self.beam.create(center=location, start_radius=60, end_radius=80)
        self.beam.create(center=location2, start_radius=70, end_radius=90)
        self.beam.create(center=location3, start_radius=80, end_radius=100)
        self.beam.create(center=location4, start_radius=80, end_radius=100)

@UndeadScourge.add_skill
class VampiricAura(Skill):
    laser = Model("sprites/lgtning.vmt", True)
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.max_health = self.parent.parent.health + 100
        self.beam = TempEntity('BeamPoints', alpha=255, red=255, green=0, blue=0,
            life_time=1.0, model_index=self.laser.index, start_width=7, end_width=7,
            frame_rate=255, halo_index=self.laser.index)

    @classproperty
    def description(cls):
        return "Attacking an enemy causes you to steal their life."

    @classproperty
    def max_level(cls):
        return 8

    _msg_a = '{{PALE_GREEN}}Healed {{GREEN}}{heal} {{PALE_GREEN}}HP by {{DULL_RED}}stealing {{PALE_GREEN}}life from {{RED}}{name}.'

    @events('player_spawn')
    def _on_player_spawn(self, player, **kwargs):
        self.max_health = player.health + 100

    @events('player_pre_attack')
    def _on_player_pre_attack(self, attacker, victim, info, **kwargs):
        if self.level == 0:
            return

        chance = 8 * self.level
        heal = int(info.damage * 0.6)
        can_heal = self.max_health > attacker.health + heal

        if chance > randint(0, 100) or not can_heal:
            return

        attacker.health += heal

        send_wcs_saytext_by_index(self._msg_a.format(heal=heal, name=victim.name), attacker.index)

        weapon = attacker.active_weapon
        if weapon and weapon.weapon_name.split("_")[-1] not in weapon_manager.projectiles:
            start_location = weapon.origin
            end_location = attacker.get_view_coordinates()

            self.beam.create(start_point=start_location, end_point=end_location)

@UndeadScourge.add_skill
class UnholyAura(Skill):

    @classproperty
    def description(cls):
        return "Increase your base speed, and scales when health changes."

    @classproperty
    def max_level(cls):
        return 8

    @events('player_spawn')
    def _on_player_spawn(self, player, **kwargs):
        if self.level == 0:
            return

        player.speed += 0.06 * self.level

    @events('player_attack', 'player_victim')
    def _change_player_speed(self, player, **kwargs):
        if self.level == 0:
            return

        if player.health > 100:
            speed = max(round(player.health / 120, 2), 1 + 0.06 * self.level)
            player.speed = speed

@UndeadScourge.add_skill
class Levitation(Skill):

    @classproperty
    def description(cls):
        return "Reduce your current gravity and damage taken when jumping."

    @classproperty
    def max_level(cls):
        return 8

    _msg_a = '{{PALE_GREEN}}Reduced {{DULL_RED}}damage taken {{PALE_GREEN}}from {{RED}}{name}.'

    @events('player_spawn')
    def _on_player_spawn(self, player, **eargs):
        if self.level == 0:
            return

        player.gravity = 1 - 0.08 * self.level

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
class SuicideBomber(Skill):

    @classproperty
    def description(cls):
        return "Explode upon death causing enemies to bleed."

    @classproperty
    def max_level(cls):
        return 8

    _msg_a = '{{RED}}Exploded {{PALE_GREEN}}damaging {{RED}}{name}{{PALE_GREEN}}!'

    @property
    def _range(self):
        return 300 + 25*self.level

    @property
    def _magnitude(self):
        return 50 + 5*self.level

    @events('player_death')
    def player_death(self, player, **eargs):
        if self.level == 0:
            return

        team = ['ct', 't'][player.team-2]

        for target in PlayerIter(is_filters=team):
            if player.origin.get_distance(target.origin) <= self._range:
                target.take_damage(self._magnitude, attacker_index=player.index)
                send_wcs_saytext_by_index(self._msg_a.format(name=target.name), player.index)

        explosion = TempEntity('Explosion',
            magnitude=100, scale=40, radius=self._range, origin=player.origin)
        explosion.create()