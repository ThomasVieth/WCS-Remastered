"""

"""

## python imports

from random import randint

## source.python imports

from effects.base import TempEntity
from engines.sound import StreamSound
from engines.precache import Model
from entities.entity import Entity
from filters.players import PlayerIter
from listeners.tick import Repeat
from weapons.manager import weapon_manager

## warcraft.package imports

from warcraft.commands.messages import send_wcs_saytext_by_index
from warcraft.race import Race
from warcraft.registration import events, clientcommands
from warcraft.skill import Skill
from warcraft.utility import classproperty, CooldownDict

## __all__ declaration

__all__ = ("OrcishHorde", )

## OrcishHorde declaration

chain_sound = StreamSound('source-python/warcraft/chain_lightning.wav', download=True)
root_sound = StreamSound('source-python/warcraft/root.mp3', download=True)

class OrcishHorde(Race):
    
    @classproperty
    def description(cls):
        return 'Recoded Orcish Horde. (Kryptonite)'

    @classproperty
    def max_level(cls):
        return 99

    @classproperty
    def requirement_sort_key(cls):
        return 3


@OrcishHorde.add_skill
class BloodFury(Skill):
    laser = Model('sprites/lgtning.vmt', True)

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.can_crit = False
        self.counter = 0
        self.repeater = None
        self.beam = TempEntity('BeamPoints', alpha=255, red=0, green=255, blue=0,
            life_time=1.0, model_index=self.laser.index,
            start_width=3, end_width=3, frame_rate=255,
            halo_index=self.laser.index)

    @classproperty
    def description(cls):
        return 'You are able to hit vital points, causing major damage.'

    @classproperty
    def max_level(cls):
        return 8

    _msg_a = '{{GREEN}}Critical strike {{PALE_GREEN}}on {{RED}}{name} {{PALE_GREEN}}caused {{DULL_RED}}vital damage!'

    @events('player_spawn', 'skill_level_up')
    def _on_spawn_start_repeat(self, player, **kwargs):
        self.can_crit = True
        self.counter = 0

        self.repeater = Repeat(self._on_game_tick, kwargs={}, cancel_on_level_end=True)
        self.repeater.start(0.1)

    @events('player_death')
    def _on_death_stop_repeat(self, player, **kwargs):
        if self.repeater:
            self.repeater.stop()

    @events('player_pre_attack')
    def _on_player_pre_attack(self, attacker, victim, info, **kwargs):
        if self.can_crit:
            info.damage *= 1 + 0.2 * self.level
            send_wcs_saytext_by_index(self._msg_a.format(name=victim.name), attacker.index)
            
            weapon = attacker.active_weapon
            if weapon and weapon.weapon_name.split("_")[-1] not in weapon_manager.projectiles:
                start_location = weapon.origin.copy()
                start_location.z += 40
                end_location = attacker.get_view_coordinates()

                self.beam.create(start_point=start_location, end_point=end_location)

            self.can_crit = False
            self.counter = 0

    def _on_game_tick(self):
        self.counter += 1
        if self.counter == 256 - (self.level * 2):
            self.can_crit = True

@OrcishHorde.add_skill
class EarthgrabTotem(Skill):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.model = Model('sprites/blueflare1.vmt', True)
        self.model._precache()
        self.effect = TempEntity('BeamRingPoint', start_radius=120,
            end_radius=0, model_index=self.model.index, halo_index=self.model.index,
            life_time=1.5, amplitude=10, red=10, green=255, blue=10, alpha=245, flags=0,
            start_width=6, end_width=6)

        if not root_sound.is_precached:
            root_sound.precache()

    @classproperty
    def description(cls):
        return 'Root your enemies to the ground, 16-24% chance.'

    @classproperty
    def max_level(cls):
        return 8

    _msg_a = '{{GREEN}}Rooted {{RED}}{name} {{PALE_GREEN}}to the ground.'
    _msg_b = '{{PALE_GREEN}}You have been {{GREEN}}rooted {{PALE_GREEN}}to the ground by {{RED}}{name}.'

    @events('player_pre_attack')
    def _on_player_pre_attack(self, attacker, victim, **kwargs):
        if randint(1, 100) <= 16 + self.level and not victim.stuck:
            victim.stuck = True
            victim.delay(1.5, victim.__setattr__, args=('stuck', False))

            send_wcs_saytext_by_index(self._msg_a.format(name=victim.name), attacker.index)
            send_wcs_saytext_by_index(self._msg_b.format(name=attacker.name), victim.index)

            root_sound.index = victim.index
            root_sound.origin = victim.origin
            root_sound.play()
            
            self.effect.create(center=victim.origin)
            self.effect.create(center=victim.origin, start_radius=80)

@OrcishHorde.add_skill
class Reincarnation(Skill):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.weapons = []

    @classproperty
    def description(cls):
        return 'Upon death, the shamans will ressurect you in your old location, 25-33% chance.'

    @classproperty
    def max_level(cls):
        return 8

    _msg_a = '{ORANGE}Respawning {PALE_GREEN}in {GREEN}1 {PALE_GREEN}second.'

    @events('player_pre_victim')
    def _on_pre_death_obtain_weapons(self, victim, **kwargs):
        self.weapons = [Entity(index).class_name for index in victim.weapon_indexes(
                not_filters='knife')
            ]
        self.location = victim.origin.copy()
        self.location.z += 1

    @events('player_death')
    def _on_death_respawn(self, player, **kwargs):
        if randint(1, 101) <= 25 + self.level:
            player.delay(1.5, player.spawn)
            for index in player.weapon_indexes(not_filters='knife'):
                entity = Entity(index)
                player.delay(1.7, player.drop_weapon, args=(entity.pointer, None, None))
            for weapon in self.weapons:
                player.delay(2.2, player.give_named_item, args=(weapon, ))
            player.delay(2.3, player.teleport, args=(self.location, ))

            send_wcs_saytext_by_index(self._msg_a, player.index)


@OrcishHorde.add_skill
class ChainLightning(Skill):
    laser = Model('sprites/lgtning.vmt', True)

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.cooldowns = CooldownDict()
        self.beam = TempEntity('BeamPoints', alpha=255, red=255, green=200, blue=200,
            life_time=1.0, start_width=15, end_width=15, frame_rate=255)
        self.laser = Model('sprites/lgtning.vmt')
        self.laser._precache()

    @classproperty
    def description(cls):
        return 'You channel a lightning rod which ricochets from player to player.'

    @classproperty
    def max_level(cls):
        return 8

    _msg_a = '{GREEN}Chain Lightning {RED}hit enemies{PALE_GREEN}!'
    _msg_c = '{{GREEN}}Chain Lightning {{PALE_GREEN}}is on cooldown for {{DULL_RED}}{time:0.1f} {{PALE_GREEN}}seconds.'
    _msg_f = '{GREEN}Chain Lightning {PALE_GREEN}found {DULL_RED}no enemies{PALE_GREEN}!'

    def _find_closest_player(self, player, team, length=99999, exclusions=[]):
        _target = None
        for target in PlayerIter(is_filters='alive', not_filters=team):
            _distance = player.origin.get_distance(target.origin)
            if _distance < length and not target in exclusions:
                _target = target
                length = _distance
        return _target

    def _find_chain_players(self, player, length, count):
        _last_target = player
        team = ['t', 'ct'][player.team-2]
        _targets = []
        while count > 0:
            if not _last_target:
                break
            _target = self._find_closest_player(_last_target, team, length, _targets)
            _targets.append(_target)
            _last_target = _target
            count -= 1
        return _targets

    @events('player_spawn')
    def _on_player_spawn_reset(self, player, **kwargs):
        self.cooldowns['ultimate'] = 4

    @clientcommands('ultimate')
    def _on_player_ultimate(self, player, **kwargs):
        _cooldown = self.cooldowns['ultimate']
        if _cooldown <= 0:
            last_target = player
            targets = self._find_chain_players(player, 500, 3)

            if targets[0] == None:
                send_wcs_saytext_by_index(self._msg_f, player.index)
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

            send_wcs_saytext_by_index(self._msg_a, player.index)
            self.cooldowns['ultimate'] = 20
        else:
            send_wcs_saytext_by_index(self._msg_c.format(time=_cooldown), player.index)