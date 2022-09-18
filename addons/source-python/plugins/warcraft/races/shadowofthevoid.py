
"""

"""

## python imports

from random import randint

## source.python imports

from colors import Color
from effects.base import TempEntity
from engines.precache import Model
from engines.sound import Sound
from listeners.tick import Delay
from mathlib import Vector
from messages import Fade

## warcraft.package imports

from warcraft.commands.messages import send_wcs_saytext_by_index
from warcraft.players import player_dict
from warcraft.race import Race
from warcraft.registration import events, clientcommands
from warcraft.skill import Skill
from warcraft.utility import classproperty, CooldownDict

## __all__ declaration

__all__ = ("ShadowOfTheVoid", )

## ShadowOfTheVoid declaration

death_sound = Sound('ambient/explosions/explode_6.wav')

class ShadowOfTheVoid(Race):

    @classproperty
    def description(cls):
        return ''

    @classproperty
    def max_level(cls):
        return 99 

    @classproperty
    def requirement_sort_key(cls):
        return 24

    @classproperty
    def requirement_string(cls):
        return "Total Level 300"

    @classmethod
    def is_available(cls, player):
        return player.total_level > 300

@ShadowOfTheVoid.add_skill
class UltimateImmunity(Skill):
    
    @classproperty
    def description(cls):
        return 'Immune To Enemy Ultimates'

    @classproperty
    def max_level(cls):
        return 8

    _msg_a = '{DARK_BLUE}Resistance {PALE_GREEN}provides {BLUE}you {ORANGE}ultimate immunity{PALE_GREEN}.'

    @property
    def chance(self):
        return 20 + (10 * self.level)

    @events('player_spawn')
    def _on_player_spawn(self, player, **kwargs):
        if randint(0, 101) > self.chance or self.level == 0:
            return
            
        player.ultimate_immune = True
        send_wcs_saytext_by_index(self._msg_a, player.index)

    @events('player_death', 'player_suicide')
    def _on_player_death(self, player, **kwargs):
        player.ultimate_immune = False


@ShadowOfTheVoid.add_skill
class DeathsShadow(Skill):
    
    @classproperty
    def description(cls):
        return 'Do Extra Damage'

    @classproperty
    def max_level(cls):
        return 8

    @classmethod
    def is_available(cls, player):
        return player.race.level > 0

    @property
    def multiplier(self):
        return 1 + (0.05 * self.level)
    
    @events('player_pre_attack')
    def _on_player_attack(self, info, **kwargs):
        info.damage *= self.multiplier


@ShadowOfTheVoid.add_skill
class FadingBlack(Skill):
    
    @classproperty
    def description(cls):
        return 'Blinds your enemy for 1-5 seconds. 10-26% chance.'

    @classproperty
    def max_level(cls):
        return 8

    @classmethod
    def is_available(cls, player):
        return player.race.level > 0

    @property
    def chance(self):
        return 10 + (self.level * 2)

    @property
    def duration(self):
        return 1 + (self.level * 0.5)

    _msg_blind = "{{DARK_BLUE}}Fading Black {{PALE_GREEN}}has {{BLUE}}blinded {{RED}}{name}{{PALE_GREEN}}."

    @events('player_attack')
    def _on_player_attack(self, attacker, victim, **kwargs):
        if randint(0, 101) > self.chance or self.level == 0:
            return

        Fade(int(self.duration - 2), int(self.duration - (self.level * 0.5)), Color(0, 0, 0)).send(victim.index)
        send_wcs_saytext_by_index(self._msg_blind.format(name=victim.name), attacker.index)


@ShadowOfTheVoid.add_skill
class IntotheVoid(Skill):
    model = Model('sprites/physcannon_bluecore1b.vmt', True)
    model2 = Model('sprites/lgtning.vmt', True)

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.effect = TempEntity('GlowSprite',
            model=self.model, life_time=6, scale=3, brightness=255
        )
        self.effect2 = TempEntity('BeamRingPoint', model=self.model2,
            start_radius=500, end_radius=20, life_time=6, start_width=200,
            end_width=200, spread=10, amplitude=0, red=10, green=10, blue=10,
            alpha=255, speed=50)
    
    @classproperty
    def description(cls):
        return 'Create a black hole when you die, sucking enemies into this.'

    @classproperty
    def max_level(cls):
        return 8

    @classmethod
    def is_available(cls, player):
        return player.race.level > 8

    @property
    def outer_range(self):
        return 600 + (200 * self.level)
    
    @property
    def inner_range(self):
        return 75

    def _on_tick(self, player):
        center = player.origin.copy()
        center.z += 38

        for target in player_dict.values():
            if target.team == player.team or target.team_index == 0:
                continue

            distance = target.origin.get_distance(center)
            if distance < self.outer_range:
                diff_vec = center - target.origin
                diff_normalized = diff_vec.normalized()
                ## calc multiplier to give pull
                multiplier = (distance / 600) * 200
                target_v = diff_normalized * multiplier
                target.base_velocity = target_v
            if distance < self.inner_range:
                target.take_damage(10, attacker_index=player.index)

    @events('player_death')
    def _on_player_death(self, player, **kwargs):
        repeat = player.repeat(self._on_tick, args=(self.parent.parent, ))
        repeat.start(0.2)
        death_sound.play()
        self.effect.create(origin=player.origin)
        self.effect2.create(center=player.origin)
        Delay(6, repeat.stop)