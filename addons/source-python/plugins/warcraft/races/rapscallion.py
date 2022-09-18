
"""

"""

## python imports

from random import randint

## source.python imports

from colors import Color
from effects.base import TempEntity
from engines.precache import Model
from entities.constants import RenderMode, RenderEffects
from filters.weapons import WeaponClassIter
from mathlib import Vector
from messages import Fade

## warcraft.package imports

from warcraft.commands.messages import send_wcs_saytext_by_index
from warcraft.players import player_dict
from warcraft.race import Race
from warcraft.registration import events, clientcommands
from warcraft.skill import Skill
from warcraft.utility import classproperty, CooldownDict

from .skills.self_add_speed import AddSpeedSkill
from .skills.self_reduce_gravity import ReduceGravitySkill

## __all__ declaration

__all__ = ("Rapscallion", )

## Rapscallion declaration

_knifeonly = set(weapon.basename for weapon in WeaponClassIter(not_filters='knife'))

class Rapscallion(Race):

    @classproperty
    def description(cls):
        return ''

    @classproperty
    def max_level(cls):
        return 99

    @classproperty
    def requirement_sort_key(cls):
        return 25

    @classmethod
    def is_available(cls, player):
        return player.total_level > 400

    @classproperty
    def requirement_string(cls):
        return "Total Level 400"

    @events('player_spawn')
    def player_spawn(self, player, **kwargs):
        player.restrict_weapons(*_knifeonly)
        for weapon in player.weapons(not_filters='knife'):
            player.drop_weapon(weapon.pointer, None, None)

    @events('player_death', 'player_suicide')
    def player_death(self, player, **kwargs):
        player.unrestrict_weapons(*_knifeonly)

@Rapscallion.add_skill
class FlickeringShadows(Skill):
    
    @classproperty
    def description(cls):
        return 'Flickering Invisibility'

    @classproperty
    def max_level(cls):
        return 6

    @classmethod
    def is_available(cls, player):
        return player.race.level > 0

    @property
    def alpha(self):
        return 255 - (30 * self.level)

    @events('player_death', 'player_suicide')
    def _on_player_death(self, player, **kwargs):
        player.render_mode = RenderMode.NORMAL
        player.render_fx = RenderEffects.NONE
        color = player.color
        color.a = 255
        player.color = color

    @events('player_spawn')
    def _on_player_spawn(self, player, **kwargs):
        player.render_mode = RenderMode.TRANS_ALPHA
        player.render_fx = RenderEffects.FLICKER_FAST
        color = player.color
        color.a = self.alpha
        player.color = color

@Rapscallion.add_skill
class Adrinaline(AddSpeedSkill):
    
    @classproperty
    def description(cls):
        return 'Speed'

    @classproperty
    def max_level(cls):
        return 6

    @classmethod
    def is_available(cls, player):
        return player.race.level > 0

    @property
    def base_speed_addition(self):
        return 0.1 * self.level


@Rapscallion.add_skill
class StealthBlade(Skill):
    
    @classproperty
    def description(cls):
        return 'Extra knife dmg'

    @classproperty
    def max_level(cls):
        return 6

    @classmethod
    def is_available(cls, player):
        return player.race.level > 0

    @property
    def chance(self):
        return 8 + self.level

    @property
    def extra_damage(self):
        return 5 + (self.level * 2)

    _msg_a = '{{RED}}Stealth Blade {{PALE_GREEN}}dealt {{DULL_RED}}{damage} {{PALE_GREEN}}extra to {{RED}}{name}{{PALE_GREEN}}.'

    @events('player_pre_attack')
    def _on_player_pre_attack(self, attacker, victim, info, **kwargs):
        if victim.dead or randint(0, 101) > self.chance or self.level == 0:
            return

        info.damage += self.extra_damage
        send_wcs_saytext_by_index(self._msg_a.format(damage=self.extra_damage, name=victim.name), attacker.index)
        self.effect.create(center=victim.origin)

@Rapscallion.add_skill
class Levitation(ReduceGravitySkill):
    
    @classproperty
    def description(cls):
        return 'Levitation'

    @classproperty
    def max_level(cls):
        return 6

    @property
    def reduction(self):
        return 0.1 * self.level

    @classmethod
    def is_available(cls, player):
        return player.race.level > 0


@Rapscallion.add_skill
class CompleteInvisibility(Skill):
    _model = Model("sprites/crosshairs.vmt")
    
    @classproperty
    def description(cls):
        return 'Become Completly invisible when not moving. Ultimate.'

    @classproperty
    def max_level(cls):
        return 6

    @classmethod
    def is_available(cls, player):
        return player.race.level > 8

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.cooldowns = CooldownDict()
        self.is_frozen = False
        self.color = None
        self.fade_color = Color(70, 40, 200)
    
    @property
    def range(self):
        return 700 + (60 + self.level)

    @property
    def time(self):
        return 12 - self.level

    _msg_b = '{{GRAY}}Complete Invisibility {{PALE_GREEN}}has froze you invisible.'
    _msg_c = '{{GRAY}}Complete Invisibility {{PALE_GREEN}}is on cooldown for {{DULL_RED}}{time:0.1f} {{PALE_GREEN}}seconds.'

    def animate(self, player):
        origin = player.origin.copy()
        origin.z += 40
        effect = TempEntity('Blood Sprite')
        effect.drop_model = self._model
        effect.spray_model = self._model
        effect.origin = origin
        effect.direction = Vector(40, 90, 0.5)
        effect.red = 50
        effect.green = 30
        effect.blue = 0
        effect.alpha = 135
        effect.size = 100
        effect.create()

    @events('player_spawn')
    def _on_player_spawn_reset(self, player, **eargs):
        self.cooldowns['ultimate'] = 4

    @clientcommands('ultimate')
    def _on_player_ultimate(self, player, **eargs):
        if self.level == 0:
            return

        _cooldown = self.cooldowns['ultimate']
        if _cooldown <= 0:
            if self.is_frozen:
                player.stuck = False
                player.color = self.color
                player.play_sound("weapons\\fx\\nearmiss\\bulletltor13.wav")
                self.is_frozen = False
                self.cooldowns['ultimate'] = self.time
            else:
                self.animate(player)
                self.color = player.color
                player.stuck = True
                player.color = self.color.with_alpha(0)
                player.play_sound("weapons\\fx\\nearmiss\\bulletltor13.wav")
                Fade(0, 1, self.fade_color).send(player.index)
                self.is_frozen = True
                self.cooldowns['ultimate'] = 1
        else:
            send_wcs_saytext_by_index(self._msg_c.format(time=_cooldown), player.index)
        
