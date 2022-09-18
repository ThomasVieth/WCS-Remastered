
"""

"""

## python imports

from random import choice, randint

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

## __all__ declaration

__all__ = ("MarineClass", )

## MarineClass declaration

blip_sound = Sound('buttons/blip1.wav')

class MarineClass(Race):

    @classproperty
    def description(cls):
        return ''

    @classproperty
    def max_level(cls):
        return 99

    @classproperty
    def requirement_sort_key(cls):
        return 21

    @classproperty
    def requirement_string(cls):
        return "Total Level 300"

    @classmethod
    def is_available(cls, player):
        return player.total_level > 300


@MarineClass.add_skill
class Gun(Skill):
    weapons = ['weapon_mp7', 'weapon_famas', 'weapon_m4a1', 'weapon_m249']
    
    @classproperty
    def description(cls):
        return 'You got 50%-75% of spawning with a MP5Navy/Famas/M4A1/M249'

    @classproperty
    def max_level(cls):
        return 5

    @classmethod
    def is_available(cls, player):
        return player.race.level > 0

    @property
    def chance(self):
        return 50 + (self.level * 5)

    @events('player_spawn')
    def _on_player_spawn(self, player, **kwargs):
        if randint(1, 101) > self.chance:
            return

        weapon = choice(self.weapons)
        player.give_named_item(weapon)
        

@MarineClass.add_skill
class AimTraining(Skill):
    
    @classproperty
    def description(cls):
        return 'You know where to aim, causing 15-120% increased damage. 15%-40% chance.'

    @classproperty
    def max_level(cls):
        return 5

    @classmethod
    def is_available(cls, player):
        return player.race.level > 0

    _msg_a = '{{PALE_GREEN}}Superior aim {{DULL_RED}}caused {{PALE_GREEN}}you to deal {{DULL_RED}}{damage} {{PALE_GREEN}}extra to {{RED}}{name}{{PALE_GREEN}}.'

    @property
    def chance(self):
        return 15 + (self.level * 5)
    
    @property
    def multiplier(self):
        return 1 + (randint(15, 120) / 100)

    @events('player_pre_attack')
    def _on_player_pre_attack(self, attacker, info, victim, **kwargs):
        if randint(1, 101) > self.chance:
            return

        damage = info.damage
        info.damage *= self.multiplier
        send_wcs_saytext_by_index(self._msg_a.format(damage=int(info.damage-damage), name=victim.name), attacker.index)


@MarineClass.add_skill
class HotSpot(Skill):
    model = Model("sprites/lgtning.vmt")
    colors = [
        Color(50, 50, 255),
        Color(255, 50, 50)
    ]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.effect = TempEntity('BeamRingPoint', model=self.model,
            start_radius=20, end_radius=500, life_time=1, start_width=8,
            end_width=8, spread=1, amplitude=0, alpha=255, speed=50
        )
    
    @classproperty
    def description(cls):
        return 'You got 10%-70% of makeing a beacon around enemy'

    @classproperty
    def max_level(cls):
        return 5

    @classmethod
    def is_available(cls, player):
        return player.race.level > 0

    @property
    def chance(self):
        return 10 + (self.level * 12)

    @events('player_attack')
    def _on_player_attack(self, victim, **kwargs):
        if randint(1, 101) > self.chance:
            return

        victim.emit_sound('buttons/blip1.wav', update_positions=True)
        self.effect.create(color=self.colors[3 - victim.team], center=victim.origin)


@MarineClass.add_skill
class Mines(Skill):
    
    @classproperty
    def description(cls):
        return 'You got 20-100% of spawning with a bump mine.'

    @classproperty
    def max_level(cls):
        return 5

    @classmethod
    def is_available(cls, player):
        return player.race.level > 0

    @property
    def chance(self):
        return 20 + (self.level * 16)

    @events('player_spawn')
    def _on_player_spawn(self, player, **kwargs):
        if randint(1, 101) > self.chance:
            return

        player.give_named_item('weapon_bumpmine')

@MarineClass.add_skill
class Artillery(Skill):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.cooldowns = CooldownDict()
    
    @classproperty
    def description(cls):
        return 'You can hit an enemy from everywhere with a artillery cannon and restore 30 HP.'

    @classproperty
    def max_level(cls):
        return 5

    @classmethod
    def is_available(cls, player):
        return player.race.level > 8

    @property
    def health(self):
        return 35

    @property
    def cooldown(self):
        return max(35 - (2 * self.level), 20)

    _msg_a = '{{DARK_BLUE}}Artillery {{PALE_GREEN}}leeched {{DULL_RED}}{health} health {{PALE_GREEN}}from {{RED}}{name}{{PALE_GREEN}}.'
    _msg_c = '{{DARK_BLUE}}Artillery {{PALE_GREEN}}is on {{DULL_RED}}cooldown {{PALE_GREEN}}for {time:0.1f} seconds.'
    _msg_f = '{DARK_BLUE}Artillery {DULL_RED}cannot find a target.'

    @clientcommands('ultimate')
    def _on_player_ultimate(self, player, **kwargs):
        if self.level == 0:
            return
            
        _cooldown = self.cooldowns['ultimate']
        if _cooldown <= 0:
            enemy_team = 5 - player.team
            all_players = player_dict.values()
            possible_players = list(filter(lambda x: x.team == enemy_team and not x.ultimate_immune and not x.dead, all_players))
            if len(possible_players) > 0:
                target = choice(possible_players)
                target.take_damage(self.health, attacker_index=player.index, skip_hooks=True)
                player.health += self.health
                send_wcs_saytext_by_index(self._msg_a.format(health=self.health, name=target.name), player.index)
                self.cooldowns['ultimate'] = self.cooldown
            else:
                send_wcs_saytext_by_index(self._msg_f, player.index)
        else:
            send_wcs_saytext_by_index(self._msg_c.format(time=_cooldown), player.index)