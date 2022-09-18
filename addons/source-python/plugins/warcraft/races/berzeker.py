
"""

"""

## python imports

from random import randint

## source.python imports

from colors import Color
from effects.base import TempEntity
from engines.precache import Model
from engines.sound import Sound

## warcraft.package imports

from warcraft.commands.messages import send_wcs_saytext_by_index
from warcraft.players import player_dict
from warcraft.race import Race
from warcraft.registration import events, clientcommands
from warcraft.skill import Skill
from warcraft.utility import classproperty, CooldownDict

from .skills.enemy_shake import ShakeSkill

## __all__ declaration

__all__ = ("Berzerker", )

## Berzerker declaration

class Berzerker(Race):

    @classproperty
    def description(cls):
        return ''

    @classproperty
    def max_level(cls):
        return 99

    @classproperty
    def requirement_sort_key(cls):
        return 22

    @classmethod
    def is_available(cls, player):
        return player.total_level > 300

    @classproperty
    def requirement_string(cls):
        return "Total Level 300"

@Berzerker.add_skill
class Redemption(Skill):
    
    @classproperty
    def description(cls):
        return 'When attacked, the attacker may drop his gun. 10-22% chance.'

    @classproperty
    def max_level(cls):
        return 6

    @property
    def chance(self):
        return 10 + (self.level * 2)

    _msg_a = '{{PALE_GREEN}}Force dropped {{RED}}{name}\'s {{PALE_GREEN}}weapon!'
    _msg_b = '{{RED}}{name} {{PALE_GREEN}}made you {{RED}}drop {{PALE_GREEN}}your weapon!'

    @events('player_victim')
    def _on_player_victim(self, attacker, player, **kwargs):
        if randint(0, 101) > self.chance or self.level == 0:
            return

        attacker.drop_weapon(attacker.active_weapon.pointer, None, None)

        send_wcs_saytext_by_index(self._msg_a.format(name=attacker.name), player.index)
        send_wcs_saytext_by_index(self._msg_b.format(name=player.name), attacker.index)

@Berzerker.add_skill
class Confuser(ShakeSkill):
    
    @classproperty
    def description(cls):
        return 'When you attack someone you have a shake him.'

    @classproperty
    def max_level(cls):
        return 6


@Berzerker.add_skill
class Frenzy(Skill):
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
        return 'Deal 5-13 extra damage. 8-14% chance.'

    @classproperty
    def max_level(cls):
        return 6

    @property
    def chance(self):
        return 8 + self.level

    @property
    def extra_damage(self):
        return 5 + (self.level * 2)

    _msg_a = '{{RED}}Frenzy {{PALE_GREEN}}dealt {{DULL_RED}}{damage} {{PALE_GREEN}}extra to {{RED}}{name}{{PALE_GREEN}}.'

    @events('player_pre_attack')
    def _on_player_pre_attack(self, attacker, victim, info, **kwargs):
        if victim.dead or randint(0, 101) > self.chance or self.level == 0:
            return

        damage = randint(5, self.extra_damage)
        info.damage += damage
        send_wcs_saytext_by_index(self._msg_a.format(damage=damage, name=victim.name), attacker.index)
        self.effect.create(center=victim.origin)

@Berzerker.add_skill
class Berzerk(Skill):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.cooldowns = CooldownDict()
    
    @classproperty
    def description(cls):
        return 'You go nuts and you gain speed and health. Ultimate.'

    @classproperty
    def max_level(cls):
        return 6

    @classmethod
    def is_available(cls, player):
        return player.race.level > 8

    @property
    def time(self):
        return 40

    @property
    def duration(self):
        return 10 + (self.level)

    @property
    def health(self):
        return 30 + (5 * self.level)

    @property
    def speed(self):
        return 0.2 + (0.05 * self.level) 

    _msg_b = 'You have gone {{RED}}Berzerk!'
    _msg_c = '{{RED}}Berzerk {{PALE_GREEN}}is on cooldown for {{DULL_RED}}{time:0.1f} {{PALE_GREEN}}seconds.'

    @events('player_spawn')
    def _on_player_spawn_reset(self, player, **eargs):
        self.cooldowns['ultimate'] = 4

    def _reset(self, player):
        player.speed = self.old_speed
        health = max(1, player.health - self.health)
        player.health = health

    @clientcommands('ultimate')
    def _on_player_ultimate(self, player, **eargs):
        _cooldown = self.cooldowns['ultimate']
        if _cooldown <= 0:
            self.old_speed = player.speed
            player.health += self.health
            player.speed += self.speed
            player.delay(self.duration, self._reset, args=(player, ))
            send_wcs_saytext_by_index(self._msg_b.format(health=self.health), player.index)
            self.cooldowns['ultimate'] = self.time
        else:
            send_wcs_saytext_by_index(self._msg_c.format(time=_cooldown), player.index)