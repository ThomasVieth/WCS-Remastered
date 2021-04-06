"""

"""

## python imports

from random import randint

## source.python imports

from colors import Color
from effects.base import TempEntity
from engines.sound import StreamSound
from engines.precache import Model
from engines.trace import engine_trace
from engines.trace import ContentMasks
from engines.trace import GameTrace
from engines.trace import Ray
from engines.trace import TraceFilterSimple
from entities.constants import RenderMode
from entities.entity import Entity
from filters.players import PlayerIter
from listeners.tick import Delay, Repeat
from mathlib import QAngle
from players.constants import PlayerButtons

## warcraft.package imports

from warcraft.commands.messages import send_wcs_saytext_by_index
from warcraft.players import player_dict
from warcraft.race import Race
from warcraft.registration import events, clientcommands
from warcraft.skill import Skill
from warcraft.utility import classproperty, CooldownDict

## __all__ declaration

__all__ = ("BloodElfArchmage", )

## bloodelfarchmage declaration

ice_sound = StreamSound('source-python/wcgo/icehit.mp3', download=True)

class BloodElfArchmage(Race):

    @classproperty
    def description(cls):
        return "Recoded Blood Mage. (Kryptonite)"

    @classproperty
    def max_level(cls):
        return 40

    @classproperty
    def requirement_sort_key(cls):
        return 5

@BloodElfArchmage.add_skill
class Phoenix(Skill):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self._should_respawn = True

    @classproperty
    def description(cls):
        return 'Respawn the first teammate that dies.'

    @classproperty
    def min_level(cls):
        return 0

    @classproperty
    def max_level(cls):
        return 1

    _msg_a = '{DULL_RED}Your teammate, Blood Elf Archmage, forced you to respawn.'

    @events('round_start')
    def _on_round_start(self, player, **kwargs):
        self._should_respawn = True

    @events('any_death')
    def _on_any_death(self, player, **kwargs):
        if self._should_respawn:
            send_wcs_saytext_by_index(self._msg_a, player.index)
            Delay(1, player.spawn)
        self._should_respawn = False

@BloodElfArchmage.add_skill
class ArcaneBrilliance(Skill):

    @classproperty
    def description(cls):
        return 'Give your entire friendly team increased $ upon spawning.'

    @classproperty
    def max_level(cls):
        return 6

    _msg_a = '{BLUE}You have boosted your teams economy.'
    _msg_b = '{{GREEN}}{name} {{PALE_GREEN}}increased your {{BLUE}}$ {{PALE_GREEN}}by {{GREEN}}{percent:0.0f}%'

    @property
    def multiplier(self):
        return 1 + (0.05 * self.level)

    @events('player_spawn')
    def _on_player_spawn(self, player, **kwargs):
        for ally in PlayerIter():
            if ally.team == player.team:
                ally.cash = int(ally.cash * self.multiplier)
                send_wcs_saytext_by_index(self._msg_b.format(name=player.name, percent=100*self.multiplier), ally.index)

        send_wcs_saytext_by_index(self._msg_a, player.index)

@BloodElfArchmage.add_skill
class IceBarrier(Skill):
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.cooldowns = CooldownDict()
        self._effect = None
        self._absorb = 0

        if not ice_sound.is_precached:
            ice_sound.precache()

    @classproperty
    def description(cls):
        return 'Absorb 10 - 45 damage over 10 seconds. Ability.'

    @classproperty
    def max_level(cls):
        return 6

    _msg_a = '{BLUE}Activated Ice Barrier shield.'
    _msg_b = '{DULL_RED}Your Ice Barrier has been broken.'
    _msg_c = '{{BLUE}}Ice Barrier {{PALE_GREEN}}is on cooldown for {{DULL_RED}}{time} seconds.'

    _absorb = 0

    @property
    def shield(self):
        return 10 + (5 * self.level)

    @events('player_spawn', 'player_upgrade_skill')
    def _on_player_spawn(self, player, **kwargs):
        self._effect = None
        self._absorb = 0
        self.cooldowns['ability'] = 4

    @events('round_end')
    def _on_round_end(self, player, **kwargs):
        self._effect = None
        self._absorb = 0

    @events('player_pre_victim')
    def _on_player_pre_victim(self, victim, info, **kwargs):
        if self._absorb >= info.damage:
            self._absorb -= info.damage
            info.damage = 0
        elif self._absorb > 0:
            info.damage -= self._absorb
            self._absorb = 0
            victim.color = Color(255, 255, 255)
            send_wcs_saytext_by_index(self._msg_b, victim.index)
            ice_sound.origin = victim.origin
            ice_sound.play()

            self._effect.call_input('Kill')
            self._effect = None

    @clientcommands('ability')
    def _on_player_ability(self, player, **kwargs):
        _cooldown = self.cooldowns['ability']
        if _cooldown <= 0:
            self._absorb += self.shield
            player.color = Color(0, 0, 255)
            send_wcs_saytext_by_index(self._msg_a, player.index)

            self.cooldowns['ability'] = 10

            if self._effect:
                return

            self._effect = effect = Entity.create('env_smokestack')

            location = player.origin
            location.z += 48

            effect.teleport(location, None, None)
            effect.base_spread = 12
            effect.spread_speed = 40
            effect.start_size = 1
            effect.end_size = 32
            effect.jet_length = 10
            effect.angles = QAngle(90, 90, 90)
            effect.rate = 60
            effect.speed = 40
            effect.twist = 0
            effect.render_mode = RenderMode.TRANS_COLOR
            effect.render_amt = 100
            effect.render_color = Color(0, 0, 255)
            effect.add_output('SmokeMaterial Effects/Redflare.vmt')
            effect.turn_on()
            effect.set_parent(player.pointer, -1)

        else:
            send_wcs_saytext_by_index(self._msg_c.format(time=int(_cooldown)), player.index)


@BloodElfArchmage.add_skill
class Blizzard(Skill):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.cooldowns = CooldownDict()
        self._player = self.parent.parent
        self._repeater = None
        self._players_hit = set()

        if not ice_sound.is_precached:
            ice_sound.precache()

    @classproperty
    def description(cls):
        return 'Create a blizzard at an enemy. Slows and damages enemies who walk through it.'

    @classproperty
    def max_level(cls):
        return 4

    _model = Model('sprites/blueflare1.vmt', True)
    _msg_a = '{{PALE_GREEN}}You created a {{BLUE}}Blizzard {{PALE_GREEN}}under {{GREEN}}{name}{{PALE_GREEN}}.'

    @property
    def range(self):
        return 400 + (40 * self.level)

    @property
    def damage(self):
        return 1 + self.level

    @property
    def slow(self):
        return 1 - (0.04 * self.level)

    @property
    def weapon_index(self):
        if not hasattr(self, '_player') or not self._player:
            return None

        for index in self._player.weapon_indexes():
            return index
        else:
            return None

    @events('round_end')
    def _on_round_end(self, player, **kwargs):
        if self._repeater:
            self._repeater.stop()

    @events('player_spawn', 'player_upgrade_skill')
    def _on_player_spawn(self, player, **kwargs):
        self._repeater = None

    def _repeat(self):
        for player in player_dict.values():
            if player.origin.get_distance(self._center) < (self.range / 2) and player.team != self._player.team and not player.playerinfo.is_dead():
                if player not in self._players_hit:
                    player.take_damage(self.damage, attacker_index=self._player.index, weapon_index=self.weapon_index, skip_hooks=True)
                    speed = player.speed
                    player.speed *= self.slow
                    self._players_hit.add(player)
                    Delay(1, setattr, args=(player, 'speed', speed))
                    Delay(1, self._players_hit.discard, args=(player, ))
                    ice_sound.origin = player.origin
                    ice_sound.play()

    @events('player_pre_attack')
    def _on_player_pre_attack(self, attacker, victim, **kwargs):
        if randint(1, 100) > 20 or self.cooldowns['blizzard'] > 0:
            return

        self._center = victim.origin
        self._player = attacker
        self._players_hit.clear()
        self._repeater = Repeat(self._repeat)
        self._repeater.start(0.1)

        self._effect = TempEntity('BeamRingPoint', center=self._center, start_radius=self.range,
            end_radius=self.range+1, model_index=self._model.index, halo_index=self._model.index,
            life_time=7, amplitude=10, red=200, green=200, blue=255, alpha=245, flags=0,
            start_width=10, end_width=10)
        self._effect.create()

        self._stack = Entity.create('env_smokestack')

        self._stack.teleport(self._center, QAngle(0, 180, 0), None)
        self._stack.base_spread = self.range / 2
        self._stack.spread_speed = 10
        self._stack.start_size = 2
        self._stack.end_size = 1
        self._stack.jet_length = 100
        self._stack.angles = QAngle(0, 0, 0)
        self._stack.rate = 600
        self._stack.speed = 100
        self._stack.twist = 180
        self._stack.render_mode = RenderMode.TRANS_COLOR
        self._stack.render_amt = 100
        self._stack.render_color = Color(200, 200, 255)
        self._stack.add_output('SmokeMaterial particle/rain.vmt')
        self._stack.turn_on()

        self._stack2 = Entity.create('env_smokestack')

        self._stack2.teleport(self._center, None, QAngle(0, 180, 0))
        self._stack2.base_spread = self.range / 4
        self._stack2.spread_speed = self.range / 2
        self._stack2.start_size = 2
        self._stack2.end_size = 1
        self._stack2.jet_length = 100
        self._stack2.angles = QAngle(0, 180, 0)
        self._stack2.rate = 600
        self._stack2.speed = 100
        self._stack2.twist = 120
        self._stack2.render_mode = RenderMode.TRANS_COLOR
        self._stack2.render_amt = 100
        self._stack2.render_color = Color(200, 200, 255)
        self._stack2.add_output('SmokeMaterial particle/rain.vmt')
        self._stack2.turn_on()

        send_wcs_saytext_by_index(self._msg_a.format(name=victim.name), attacker.index)

        self._stack.delay(7, self._stack.turn_off)
        self._stack2.delay(7, self._stack2.turn_off)
        Delay(7, self._repeater.stop)

        self.cooldowns['blizzard'] = 10



@BloodElfArchmage.add_skill
class CuringRitual(Skill):
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.cooldowns = CooldownDict()

    @classproperty
    def description(cls):
        return 'Sacrifice $100 to heal yourself. Ultimate.'

    @classproperty
    def max_level(cls):
        return 6

    @property
    def time(self):
        return 15 - (0.5 * self.level)

    @property
    def health(self):
        return 15 + (self.level * 2)

    _msg_b = '{{DULL_RED}}Curing Ritual {{GREEN}}healed {{PALE_GREEN}}you for {{GREEN}}{health}HP{{PALE_GREEN}}.'
    _msg_c = '{{DULL_RED}}Curing Ritual {{PALE_GREEN}}is on cooldown for {{DULL_RED}}{time:0.1f} {{PALE_GREEN}}seconds.'
    _msg_f1 = '{DULL_RED}Curing Ritual {RED}failed {PALE_GREEN}due to you cannot gain more {GREEN}HP{PALE_GREEN}.'
    _msg_f2 = '{DULL_RED}Curing Ritual {RED}failed {PALE_GREEN}due to a lack of {GREEN}${PALE_GREEN}.'

    @events('player_spawn')
    def _on_player_spawn_reset(self, player, **eargs):
        self.cooldowns['ultimate'] = 4

    @clientcommands('ultimate')
    def _on_player_ultimate(self, player, **eargs):
        _cooldown = self.cooldowns['ultimate']
        if _cooldown <= 0:
            if player.cash >= 100:
                if player.health < 200:
                    player.health += self.health
                    player.cash -= 100
                    send_wcs_saytext_by_index(self._msg_b.format(health=self.health), player.index)
                    self.cooldowns['ultimate'] = self.time
                else:
                    send_wcs_saytext_by_index(self._msg_f1, player.index)
            else:
                send_wcs_saytext_by_index(self._msg_f2, player.index)
        else:
            send_wcs_saytext_by_index(self._msg_c.format(time=_cooldown), player.index)