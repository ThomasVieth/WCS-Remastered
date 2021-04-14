"""

"""

## python imports

from math import atan2, degrees
from random import randint

## source.python imports

from colors import Color
from effects.base import TempEntity
from engines.precache import Model
from engines.sound import StreamSound
from entities.constants import RenderMode
from entities.entity import Entity
from listeners.tick import Delay
from mathlib import Vector, QAngle

## warcraft.package imports

from warcraft.commands.messages import send_wcs_saytext_by_index
from warcraft.effects import attach_entity_to_player
from warcraft.players import player_dict
from warcraft.race import Race
from warcraft.registration import events, clientcommands
from warcraft.skill import Skill
from warcraft.utility import classproperty, CooldownDict

## __all__ declaration

__all__ = ("Warden", )

## warden declaration

poison_sound = StreamSound('source-python/warcraft/poison.wav', download=True)
redflare_material = Model('Effects/Redflare.vmt', True)

class Warden(Race):
    image = "https://wow.zamimg.com/modelviewer/live/webthumbs/npc/213/76245.png"

    @classproperty
    def description(cls):
        return 'Recoded Warden. (Kryptonite)'

    @classproperty
    def max_level(cls):
        return 99

    @classproperty
    def requirement_sort_key(cls):
        return 9


@Warden.add_skill
class FanOfKnives(Skill):
    _msg_a = "{ORANGE}Fan of Knives {DULL_RED}damaged {RED}enemies {PALE_GREEN}in an {BLUE}AoE {PALE_GREEN}around {RED}you."

    @classproperty
    def description(cls):
        return 'Fan of knives deals 8-19 damage to enemies within 225 range of you. 10-18% chance.'

    @classproperty
    def max_level(cls):
        return 8

    @property
    def chance(self):
        return 10 + self.level

    @property
    def damage(self):
        return randint(16, 38)

    @property
    def range(self):
        return 225

    @events('player_attack')
    def _on_player_attack(self, attacker, victim, **kwargs):
        if randint(0, 101) < self.chance:
            for index in attacker.weapon_indexes():
                break

            v1 = attacker.origin

            damaged = False

            for target in player_dict.values():
                if target.index == victim.index or target.team == attacker.team or target.dead:
                    continue

                v2 = target.origin

                if v1.get_distance(v2) < self.range:
                    ricochet = TempEntity('Armor Ricochet', position=victim.origin)
                    ricochet.create()
                    target.take_damage(self.damage, attacker_index=attacker.index, weapon_index=index, skip_hooks=True)
                    damaged = True

            if damaged:
                send_wcs_saytext_by_index(self._msg_a, attacker.index)


@Warden.add_skill
class Resistance(Skill):

    @classproperty
    def description(cls):
        return 'Gives you immunity to ultimates. 20-100% chance on spawn.'

    @classproperty
    def max_level(cls):
        return 8

    _msg_a = '{DARK_BLUE}Resistance {PALE_GREEN}provides {BLUE}you {ORANGE}ultimate immunity{PALE_GREEN}.'

    @property
    def chance(self):
        return 20 + (10 * self.level)

    @events('player_spawn')
    def _on_player_spawn(self, player, **kwargs):
        if randint(0, 101) < self.chance:
            player.ultimate_immune = True
            send_wcs_saytext_by_index(self._msg_a, player.index)

    @events('player_death', 'player_suicide')
    def _on_player_death(self, player, **kwargs):
        player.ultimate_immune = False


@Warden.add_skill
class ShadowStrike(Skill):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.poisoned = set()

        if not poison_sound.is_precached:
            poison_sound.precache()

    @classproperty
    def description(cls):
        return 'Poison your target for 4 seconds dealing damage every second. 7-15% chance.'

    @classproperty
    def max_level(cls):
        return 8

    _msg_a = '{{DARK_BLUE}}Shadow Strike {{DULL_RED}}poisoned {{RED}}{name} {{PALE_GREEN}}for {{GREEN}}4 {{PALE_GREEN}}seconds.'

    @property
    def poison_damage(self):
        return 2 + (self.level / 2)

    @property
    def poison_chance(self):
        return 7 + self.level

    def kill_effect(self, effect):
        if not effect.basehandle.is_valid():
            return
        effect.call_input('Kill')

    @events('player_attack')
    def _on_player_attack(self, attacker, victim, **eargs):
        if randint(1, 100) > self.poison_chance or victim.userid in self.poisoned:
            return
            
        self.poisoned.add(victim.userid)

        for index in attacker.weapon_indexes():
            break

        victim.delay(1, victim.take_damage, args=(self.poison_damage, ), kwargs=dict(attacker_index=attacker.index, weapon_index=index))
        victim.delay(2, victim.take_damage, args=(self.poison_damage, ), kwargs=dict(attacker_index=attacker.index, weapon_index=index))
        victim.delay(3, victim.take_damage, args=(self.poison_damage, ), kwargs=dict(attacker_index=attacker.index, weapon_index=index))
        victim.delay(4, victim.take_damage, args=(self.poison_damage, ), kwargs=dict(attacker_index=attacker.index, weapon_index=index))
        Delay(4.5, self.poisoned.discard, args=(victim.userid, ))

        send_wcs_saytext_by_index(self._msg_a.format(name=victim.name), attacker.index)

        # EFFECT

        effect = Entity.create('env_smokestack')

        location = victim.origin
        location.z += 48

        effect.teleport(location, None, None)
        effect.base_spread = 12
        effect.spread_speed = 0
        effect.start_size = 3
        effect.end_size = 2
        effect.jet_length = 10
        effect.angles = QAngle(90, 90, 90)
        effect.rate = 60
        effect.speed = 40
        effect.twist = 0
        effect.render_mode = RenderMode.TRANS_COLOR
        effect.render_amt = 100
        effect.render_color = Color(40, 40, 40)
        effect.add_output('SmokeMaterial Effects/Redflare.vmt')
        effect.turn_on()
        attach_entity_to_player(victim, effect)

        poison_sound.origin = location
        poison_sound.play()

        Delay(4, self.kill_effect, args=(effect, ))


@Warden.add_skill
class Restoration(Skill):
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.cooldowns = CooldownDict()

    @classproperty
    def description(cls):
        return 'Restore your health, the lower your health, the more you restore. Ultimate.'

    @classproperty
    def max_level(cls):
        return 8

    @property
    def time(self):
        return 36 - (2 * self.level)

    def calc_health(self, player):
        return (self.level * 5) + max(65 - player.health, 0)

    _msg_b = '{{BRIGHT_GREEN}}Restoration {{GREEN}}healed {{PALE_GREEN}}you for {{GREEN}}{health}HP{{PALE_GREEN}}.'
    _msg_c = '{{BRIGHT_GREEN}}Restoration {{PALE_GREEN}}is on cooldown for {{DULL_RED}}{time:0.1f} {{PALE_GREEN}}seconds.'
    _msg_f1 = '{BRIGHT_GREEN}Restoration {RED}failed {PALE_GREEN}due to you cannot gain more {GREEN}HP{PALE_GREEN}.'

    @events('player_spawn')
    def _on_player_spawn_reset(self, player, **eargs):
        self.cooldowns['ultimate'] = 4

    @clientcommands('ultimate')
    def _on_player_ultimate(self, player, **eargs):
        _cooldown = self.cooldowns['ultimate']
        if _cooldown <= 0:
            if player.health < 200:
                health = self.calc_health(player)
                player.health += health
                send_wcs_saytext_by_index(self._msg_b.format(health=health), player.index)
                self.cooldowns['ultimate'] = self.time
            else:
                send_wcs_saytext_by_index(self._msg_f1, player.index)
        else:
            send_wcs_saytext_by_index(self._msg_c.format(time=_cooldown), player.index)