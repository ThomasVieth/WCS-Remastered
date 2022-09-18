
"""

"""

## python imports

from random import randint

## source.python imports

from colors import Color
from entities.constants import RenderMode, RenderEffects
from filters.weapons import WeaponClassIter
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

__all__ = ("Vagabond", )

## Vagabond declaration

_scoutonly = set(weapon.basename for weapon in WeaponClassIter()) - {'ssg08', }

class Vagabond(Race):

    @classproperty
    def description(cls):
        return 'Scout Only.'

    @classproperty
    def max_level(cls):
        return 99

    @classproperty
    def requirement_sort_key(cls):
        return 23

    @classmethod
    def is_available(cls, player):
        return player.total_level > 300

    @events('player_spawn')
    def player_spawn(self, player, **kwargs):
        player.restrict_weapons(*_scoutonly)
        for weapon in player.weapons(not_filters='ssg08'):
            player.drop_weapon(weapon.pointer, None, None)
        player.give_named_item('weapon_ssg08')

    @events('player_death', 'player_suicide')
    def player_death(self, player, **kwargs):
        player.unrestrict_weapons(*_scoutonly)


@Vagabond.add_skill
class FlickeringShadows(Skill):
    
    @classproperty
    def description(cls):
        return 'Flickering Invisibility'

    @classproperty
    def max_level(cls):
        return 4

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


@Vagabond.add_skill
class Adrinaline(AddSpeedSkill):
    
    @classproperty
    def description(cls):
        return 'Speed.'

    @classproperty
    def max_level(cls):
        return 4

    @classmethod
    def is_available(cls, player):
        return player.race.level > 0


@Vagabond.add_skill
class Scout(Skill):
    
    @classproperty
    def description(cls):
        return 'Extra Scout Damage.'

    @classproperty
    def max_level(cls):
        return 4

    @classmethod
    def is_available(cls, player):
        return player.race.level > 0

    @property
    def multiplier(self):
        return 1 + (0.15 * self.level)
    
    @events('player_pre_attack')
    def _on_player_attack(self, info, **kwargs):
        info.damage *= self.multiplier


@Vagabond.add_skill
class Levitation(ReduceGravitySkill):
    
    @classproperty
    def description(cls):
        return 'Levitation'

    @classproperty
    def max_level(cls):
        return 4

    @classmethod
    def is_available(cls, player):
        return player.race.level > 0


@Vagabond.add_skill
class CompleteInvisibility(Skill):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.cooldowns = CooldownDict()
        self.is_frozen = False
        self.color = None
        self.fade_color = Color(70, 40, 200)
    
    @classproperty
    def description(cls):
        return 'Teleport and become completly invisible and stuck.'

    @classproperty
    def max_level(cls):
        return 4

    @classmethod
    def is_available(cls, player):
        return player.race.level > 8

    @property
    def range(self):
        return 700 + (60 + self.level)

    @property
    def time(self):
        return 20 - self.level

    _msg_b = '{GRAY}Complete Invisibility {GREEN}teleported {PALE_GREEN}you and will be {LIGHT_BLUE}frozen {PALE_GREEN}in 1 second.'
    _msg_c = '{{GRAY}}Complete Invisibility {{PALE_GREEN}}is on cooldown for {{DULL_RED}}{time:0.1f} {{PALE_GREEN}}seconds.'

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
                self.is_frozen = False
                self.cooldowns['ultimate'] = self.time
            else:
                self.color = player.color
                player.push(self.range, self.range)
                player.delay(1, setattr, args=(player, 'stuck', True))
                player.delay(1, setattr, args=(player, 'color', self.color.with_alpha(0)))
                Fade(0, 1, self.fade_color).send(player.index)
                send_wcs_saytext_by_index(self._msg_b, player.index)
                self.is_frozen = True
                self.cooldowns['ultimate'] = 1
        else:
            send_wcs_saytext_by_index(self._msg_c.format(time=_cooldown), player.index)
        