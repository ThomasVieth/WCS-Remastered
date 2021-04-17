"""
"""

## python imports

from random import randint

## source.python imports

from effects.base import TempEntity
from engines.precache import Model
from engines.sound import StreamSound
from engines.trace import engine_trace
from engines.trace import ContentMasks
from engines.trace import GameTrace
from engines.trace import Ray
from engines.trace import TraceFilterSimple
from entities.constants import MoveType
from entities.entity import Entity
from filters.players import PlayerIter
from listeners.tick import Delay, Repeat
from mathlib import Vector
from messages import Shake
from players.constants import PlayerButtons

## warcraft.package imports

from warcraft.commands.messages import send_wcs_saytext_by_index
from warcraft.players import player_dict
from warcraft.race import Race
from warcraft.registration import events, clientcommands
from warcraft.skill import Skill
from warcraft.utility import classproperty, CooldownDict

## __all__ declaration

__all__ = ("Chameleon", )

## chameleon declaration

chain_sound = StreamSound('source-python/warcraft/chain_lightning.wav', download=True)
root_sound = StreamSound('source-python/warcraft/root.mp3', download=True)
teleport_sound = StreamSound('source-python/warcraft/timeleap.mp3', download=True)

class Chameleon(Race):

    @classproperty
    def description(cls):
        return 'Recoded Chameleon, random skills every round!. (Kryptonite/soundn3ko)'

    @classproperty
    def max_level(cls):
        return 99

    @classproperty
    def requirement_sort_key(cls):
        return 11

    @classmethod
    def is_available(cls, player):
        return player.total_level > 100

    @classproperty
    def requirement_string(cls):
        return "Total Level 100"


@Chameleon.add_skill
class SpawnPowers(Skill):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.longjump = False
        self.repeater = Repeat(self.on_cycle, args=(self.parent.parent, ))
        self.state = None
        self.reduction = 0

    @classproperty
    def description(cls):
        return 'Spawn with either HP, Speed, Longjump, Reduced Gravity or Regeneration. 50-90% chance.'

    @classproperty
    def max_level(cls):
        return 8

    @property
    def chance(self):
        return 50 + (self.level * 5)

    _msg_health = "{GREEN}Spawn Powers {PALE_GREEN}granted you {GREEN}80 health."
    _msg_speed = "{GREEN}Spawn Powers {PALE_GREEN}increased your {BLUE}speed {PALE_GREEN}by {GREEN}35%."
    _msg_longjump = "{GREEN}Spawn Powers {PALE_GREEN}granted you {GREEN}longjump."
    _msg_gravity = "{GREEN}Spawn Powers {PALE_GREEN}granted you {GREEN}reduced gravity."
    _msg_regen = "{GREEN}Spawn Powers {PALE_GREEN}granted you {GREEN}regeneration."

    @property
    def min_gravity(self):
        return 0.1

    @property
    def health(self):
        return 4 + self.level

    @property
    def max_health(self):
        return 175

    @property
    def duration(self):
        return 10 - (self.level / 2)

    @property
    def range(self):
        return 250

    def on_cycle(self, player):
        player.health += self.health

    def reduce_gravity(self, player, value):
        if player.gravity < self.min_gravity:
            player.gravity = max(1 - value, self.min_gravity)
            return
        player.gravity = max(player.gravity - value, self.min_gravity)

    @events('player_pre_run_command')
    def _on_player_run_command(self, player, usercmd, **kwargs):
        if (usercmd.buttons & PlayerButtons.FORWARD
            or usercmd.buttons & PlayerButtons.BACK
            or usercmd.buttons & PlayerButtons.MOVELEFT
            or usercmd.buttons & PlayerButtons.MOVERIGHT
            or usercmd.buttons & PlayerButtons.JUMP):
            if self.state == player.move_type or self.reduction == 0:
                return

            if self.state == MoveType.LADDER:
                Delay(0.5, self.reduce_gravity, args=(player, self.reduction))
            self.state = player.move_type

    @events('player_jump')
    def _on_player_jump(self, player, **kwargs):
        if self.longjump:
            velocity = Vector()
            player.get_velocity(velocity, None)
            velocity.x *= 2
            velocity.y *= 2
            velocity.z = 10
            player.base_velocity = velocity

    @events('player_death', 'player_suicide')
    def _on_player_death(self, *args, **kwargs):
        if self.level == 0:
            return

        self.longjump = False
        self.reduction = 0
        self.repeater.stop()

    @events('player_spawn')
    def _on_player_spawn(self, player, **kwargs):
        if randint(0, 101) > self.chance or self.level == 0:
            return

        num = randint(0, 4)
        if num == 0: ## Health
            send_wcs_saytext_by_index(self._msg_health, player.index)
            player.health += 80
        elif num == 1: ## Speed
            send_wcs_saytext_by_index(self._msg_speed, player.index)
            player.speed += 0.35
        elif num == 2: ## Longjump
            send_wcs_saytext_by_index(self._msg_longjump, player.index)
            self.longjump = True
        elif num == 3: ## Gravity
            send_wcs_saytext_by_index(self._msg_gravity, player.index)
            self.reduction = 0.4
            Delay(0.5, self.reduce_gravity, args=(player, self.reduction))
        else:
            send_wcs_saytext_by_index(self._msg_regen, player.index)
            self.repeater.start(self.duration)


@Chameleon.add_skill
class AttackingPowers(Skill):

    @classproperty
    def description(cls):
        return 'Attack with either extra damage, burning, freeze, shaking or lifesteal. 33% chance.'

    @classproperty
    def max_level(cls):
        return 8

    @property
    def damage(self):
        return 2 + self.level

    @property
    def duration(self):
        return self.level / 4

    @property
    def leech_multiplier(self):
        return self.level * 0.05

    _msg_damage = "{GREEN}Attacking Powers {PALE_GREEN}dealt {DULL_RED}extra damage{PALE_GREEN}."
    _msg_burn = "{GREEN}Attacking Powers {RED}burned {PALE_GREEN}your {RED}enemy{PALE_GREEN}."
    _msg_freeze = "{GREEN}Attacking Powers {BLUE}froze {PALE_GREEN}your {RED}enemy{PALE_GREEN}."
    _msg_shake = "{GREEN}Attacking Powers {ORANGE}shook {PALE_GREEN}your {RED}enemy{PALE_GREEN}."
    _msg_lifesteal = "{GREEN}Attacking Powers {PALE_GREEN}stole {DULL_RED}life {PALE_GREEN}from your {RED}enemy{PALE_GREEN}."

    @events('player_pre_attack')
    def _on_player_pre_attack(self, attacker, victim, info, **kwargs):
        if victim.dead or self.level == 0 or randint(0, 101) > 33:
            return

        num = randint(0, 4)
        if num == 0: ## Extra Damage
            info.damage += self.damage
            send_wcs_saytext_by_index(self._msg_damage, attacker.index)
        elif num == 1: ## Burn
            victim.ignite_lifetime(self.duration)
            send_wcs_saytext_by_index(self._msg_burn, attacker.index)
        elif num == 2: ## Freeze
            if not victim.stuck:
                victim.stuck = True
                victim.delay(self.duration, setattr, args=(victim, 'stuck', False))
            send_wcs_saytext_by_index(self._msg_freeze, attacker.index)
        elif num == 3: ## Shake
            Shake(100, self.duration).send(victim.index)
            send_wcs_saytext_by_index(self._msg_shake, attacker.index)
        else:
            attacker.health += int(info.damage * self.leech_multiplier)
            send_wcs_saytext_by_index(self._msg_lifesteal, attacker.index)


@Chameleon.add_skill
class VictimPowers(Skill):

    @classproperty
    def description(cls):
        return 'Attackers are either evaded, damage reduced, slowed, or you gain invisbility. 33% chance.'

    @classproperty
    def max_level(cls):
        return 8

    @property
    def reduction_multiplier(self):
        return 1 - (self.level * 0.05)

    @property
    def duration(self):
        return self.level / 4

    _msg_evade = "{GREEN}Victim Powers {PALE_GREEN}has {GREEN}evaded {PALE_GREEN}the {RED}damage{PALE_GREEN}."
    _msg_reduce = "{GREEN}Victim Powers {PALE_GREEN}has {GREEN}reduced {PALE_GREEN}the {RED}damage{PALE_GREEN}."
    _msg_slow = "{GREEN}Victim Powers {PALE_GREEN}has {BLUE}slowed {PALE_GREEN}the {RED}attacker{PALE_GREEN}."
    _msg_invis = "{GREEN}Victim Powers {PALE_GREEN}has {GREEN}provided {PALE_GREEN}you greater {BLUE}invisbility{PALE_GREEN}."

    @events('player_death', 'player_suicide')
    def _on_player_death(self, player, **kwargs):
        color = player.color
        color.a = 255
        player.color = color

    @events('player_pre_victim')
    def _on_player_pre_victim(self, attacker, victim, info, **kwargs):
        if victim.dead or self.level == 0 or randint(0, 101) > 33:
            return

        num = randint(0, 3)
        if num == 0: ## Evade
            info.damage = 0
            send_wcs_saytext_by_index(self._msg_evade, victim.index)
        elif num == 1: ## Reduce
            info.damage *= self.reduction_multiplier
            send_wcs_saytext_by_index(self._msg_reduce, victim.index)
        elif num == 2: ## Slow
            if not attacker.is_slowed:
                attacker.is_slowed = True
                speed = attacker.speed
                attacker.speed -= 0.6
                Delay(self.duration, setattr, args=(attacker, 'speed', speed))
                Delay(self.duration, setattr, args=(attacker, 'is_slowed', False))
                send_wcs_saytext_by_index(self._msg_slow, victim.index)
        else: ## Invis
            color = victim.color
            color.a = max(color.a - 50, 100)
            victim.color = color
            send_wcs_saytext_by_index(self._msg_invis, victim.index)


@Chameleon.add_skill
class DeathPowers(Skill):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.weapons = []
        self.location = None
        self.explosion = TempEntity('Explosion',
            magnitude=100, scale=40, radius=self.range)

    @classproperty
    def description(cls):
        return 'Dying either respawns you, explodes you, or gives your team health/cash. 30-70% chance.'

    @classproperty
    def max_level(cls):
        return 8

    @property
    def chance(self):
        return 30 + (self.level * 5)

    @property
    def range(self):
        return 300 + (25 * self.level)

    @property
    def magnitude(self):
        return 50 + (5 * self.level)

    @property
    def health(self):
        return 20 + (2 * self.level)

    @property
    def cash(self):
        return 500 + (200 * self.level)
    
    _msg_respawn = '{GREEN}Death Powers {PALE_GREEN}is {ORANGE}respawning {PALE_GREEN}you in {GREEN}1 {PALE_GREEN}second.'
    _msg_explode = '{{GREEN}}Death Powers {{RED}}exploded {{PALE_GREEN}}damaging {{RED}}{name}{{PALE_GREEN}}!'
    _msg_health = '{GREEN}Death Powers {PALE_GREEN}has {GREEN}healed {PALE_GREEN}your team.'
    _msg_cash = '{GREEN}Death Powers {PALE_GREEN}has {GREEN}provided {PALE_GREEN}your team cash.'

    def _force_drop_weapons(self, player):
        for index in player.weapon_indexes(not_filters='knife'):
            entity = Entity(index)
            player.drop_weapon(entity.pointer, None, None)

    @events('player_pre_victim')
    def _on_pre_death_obtain_weapons(self, victim, **kwargs):
        self.weapons = [Entity(index).class_name for index in victim.weapon_indexes(
                not_filters='knife')
            ]
        self.location = victim.origin.copy()
        self.location.z += 1

    @events('player_death')
    def _on_player_death(self, player, **kwargs):
        if self.level == 0 or randint(0, 101) > self.chance:
            return

        num = randint(0, 3)
        if num == 0: ## Respawn
            player.delay(1.5, player.spawn)
            player.delay(2, self._force_drop_weapons, args=(player, ))
            for weapon in self.weapons:
                player.delay(3, player.give_named_item, args=(weapon, ))
            if self.location:
                player.delay(2.2, player.teleport, args=(self.location, ))
            send_wcs_saytext_by_index(self._msg_respawn, player.index)
        elif num == 1: ## Explode
            for target in player_dict.values():
                if player.origin.get_distance(target.origin) <= self.range and player.team != target.team:
                    target.take_damage(self.magnitude, attacker_index=player.index, skip_hooks=True)
                    send_wcs_saytext_by_index(self._msg_explode.format(name=target.name), player.index)

            self.explosion.create(origin=player.origin)
        elif num == 2: ## Health Give
            for target in player_dict.values():
                if not target.dead and target.team == player.team:
                    target.health += self.health
            send_wcs_saytext_by_index(self._msg_health, player.index)
        else: ## Cash Give
            for target in player_dict.values():
                if not target.dead and target.team == player.team:
                    target.cash += self.cash
            send_wcs_saytext_by_index(self._msg_cash, player.index)


@Chameleon.add_skill
class UltimatePowers(Skill):
    laser = Model('sprites/lgtning.vmt', True)
    ultimate_names = ["Teleport", "Entangling Roots", "Chain Lightning", "Restoration"]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.ultimate_index = -1
        self.ultimates = [self.teleport, self.roots, self.chain_lightning, self.health_boost]
        self.cooldowns = CooldownDict()

        ## Chain Lightning
        self.beam = TempEntity('BeamPoints', alpha=255, red=255, green=200, blue=200,
            life_time=1.0, start_width=15, end_width=15, frame_rate=255)
        self.laser = Model('sprites/lgtning.vmt')
        self.laser._precache()

        ## Entangling Roots
        self.beam2 = TempEntity('BeamPoints', alpha=255, red=0, green=200, blue=0,
            life_time=1.0, start_width=15, end_width=15, frame_rate=255)
        self.laser._precache()
        self.effect = TempEntity('BeamRingPoint', start_radius=120,
            end_radius=0, model_index=self.laser.index, halo_index=self.laser.index,
            life_time=1.5, amplitude=10, red=10, green=255, blue=10, alpha=245, flags=0,
            start_width=6, end_width=6)

    @classproperty
    def description(cls):
        return 'On spawn, your ultimate with be teleport, roots, chain lightning or health boost. Ultimate. 80% chance.'

    @classproperty
    def max_level(cls):
        return 8

    @property
    def distance(self):
        return 300 + 75 * self.level

    @property
    def range(self):
        return 225 + ((self.level - 1) * 25)
    
    @property
    def duration(self):
        return 2 + (self.level * 0.125)

    def calc_health(self, player):
        return (self.level * 5) + max(65 - player.health, 0)

    _msg_spawn = '{{GREEN}}Ultimate Powers {{PALE_GREEN}}has provided you {{ORANGE}}{ultimate}{{PALE_GREEN}}.'
    _msg_none = '{GREEN}Ultimate Powers {PALE_GREEN}has not provided you an {ORANGE}ultimate{PALE_GREEN}.'

    _msg_chain = '{GREEN}Ultimate Powers {RED}hit enemies{PALE_GREEN}!'
    _msg_healed = '{{GREEN}}Ultimate Powers healed {{PALE_GREEN}}you for {{GREEN}}{health}HP{{PALE_GREEN}}.'
    _msg_c = '{{GREEN}}Ultimate Powers {{PALE_GREEN}}is on cooldown for {{DULL_RED}}{time:0.1f} {{PALE_GREEN}}seconds.'
    _msg_failed = '{GREEN}Ultimate Powers {DULL_RED}failed{PALE_GREEN}!'

    def _find_closest_player(self, player, team_index, length=99999, exclusions=[]):
        _target = None
        for target in player_dict.values():
            if target.dead or target.team_index == team_index or target in exclusions or target.ultimate_immune:
                continue

            _distance = player.origin.get_distance(target.origin)
            if _distance < length:
                _target = target
                length = _distance
        return _target

    def _find_chain_players(self, player, length, count):
        _last_target = player
        team_index = player.team_index
        _targets = []
        while count > 0:
            if not _last_target:
                break
            _target = self._find_closest_player(_last_target, team_index, length, _targets)
            _targets.append(_target)
            _last_target = _target
            count -= 1
        return _targets

    def _find_players_within(self, player, length=99999, exclusions=[]):
        targets = []
        for target in player_dict.values():
            if target.dead or target.team == player.team or target in exclusions or target.ultimate_immune:
                continue

            distance = player.origin.get_distance(target.origin)
            if distance < length:
                targets.append(target)
        return targets

    def _get_trace(self, start, end, mask, player, trace):
        engine_trace.trace_ray(Ray(start, end),
            ContentMasks.ALL, TraceFilterSimple((player, )), trace)
        return trace

    def validate_teleport(self, player, origin, teleport_vector):
        ## These vectors should create a line diagonally through the player model,
        ## allowing us to see if the teleport is safe.
        trace_vector1 = teleport_vector.copy()
        trace_vector2 = teleport_vector.copy()
        trace_vector1.z += 72
        trace_vector1.x += 26
        trace_vector1.y -= 26
        trace_vector2.x -= 26
        trace_vector2.y += 26

        check1 = self._get_trace(
                    origin, teleport_vector, ContentMasks.PLAYER_SOLID, player,
                    GameTrace()
                    )

        check2 = self._get_trace(
                    trace_vector1, trace_vector2, ContentMasks.PLAYER_SOLID, player,
                    GameTrace()
                    )

        return check1, check2

    def teleport(self, player):
        view_vector = player.view_vector
        origin = player.origin.copy()
        teleport_vector = origin + (view_vector * self.distance)
        origin.z += 50

        check1, check2 = self.validate_teleport(player, origin, teleport_vector)

        if check1.did_hit() or check2.did_hit():
            teleport_vector = check1.end_position - (view_vector * 50)
            check3, check4 = self.validate_teleport(player, origin, teleport_vector)
            if check3.did_hit() or check4.did_hit():
                send_wcs_saytext_by_index(self._msg_failed, player.index)
                return
            else:
                player.teleport(teleport_vector, None, None)
                teleport_sound.play(player.index)
                self.cooldowns['ultimate'] = 5
        else:
            player.teleport(teleport_vector, None, None)
            teleport_sound.play(player.index)
            self.cooldowns['ultimate'] = 6

    def roots(self, player):
        last_target = player
        targets = self._find_players_within(player, self.range)

        if len(targets) == 0:
            send_wcs_saytext_by_index(self._msg_failed, player.index)
            return

        for target in targets:
            if not target:
                continue
            target.stuck = True
            target.delay(self.duration, target.__setattr__, args=('stuck', False))
            location1 = last_target.origin.copy()
            location2 = target.origin.copy()
            location1.z += 40
            location2.z += 40
            self.beam2.create(start_point=location1, end_point=location2, halo=self.laser, model=self.laser)
            last_target = target
            self.effect.create(center=target.origin)
            self.effect.create(center=target.origin, start_radius=80)

        root_sound.index = player.index
        root_sound.origin = player.origin
        root_sound.play()

        self.cooldowns['ultimate'] = 20

        send_wcs_saytext_by_index(self._msg_chain, player.index)

    def chain_lightning(self, player):
        last_target = player
        targets = self._find_chain_players(player, 500, 3)

        if targets[0] == None:
            send_wcs_saytext_by_index(self._msg_failed, player.index)
            return

        for target in targets:
            if not target:
                continue
            target.take_damage(20+5*self.level, attacker_index=player.index, skip_hooks=True)
            location1 = last_target.origin.copy()
            location2 = target.origin.copy()
            location1.z += 40
            location2.z += 40
            self.beam.create(start_point=location1, end_point=location2, halo=self.laser, model=self.laser)
            last_target = target

        chain_sound.index = player.index
        chain_sound.origin = player.origin
        chain_sound.play()

        self.cooldowns['ultimate'] = 30

        send_wcs_saytext_by_index(self._msg_chain, player.index)

    def health_boost(self, player):
        if player.health < 200:
            health = self.calc_health(player)
            player.health += health
            send_wcs_saytext_by_index(self._msg_healed.format(health=health), player.index)
            self.cooldowns['ultimate'] = 20

    @events('player_spawn')
    def _on_player_spawn(self, player, **kwargs):
        if self.level == 0 or randint(0, 101) > 80:
            self.ultimate_index = -1
            return

        self.ultimate_index = randint(0, 3)
        self.cooldowns['ultimate'] = 4
        send_wcs_saytext_by_index(self._msg_spawn.format(ultimate=self.ultimate_names[self.ultimate_index]), player.index)

    @clientcommands('ultimate')
    def _on_player_ultimate(self, player, **kwargs):
        if self.level == 0 or self.ultimate_index == -1:
            send_wcs_saytext_by_index(self._msg_none, player.index)
            return
            
        _cooldown = self.cooldowns['ultimate']
        if _cooldown <= 0:
            self.ultimates[self.ultimate_index](player)
        else:
            send_wcs_saytext_by_index(self._msg_c.format(time=_cooldown), player.index)