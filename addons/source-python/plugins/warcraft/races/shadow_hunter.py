"""

"""

## python imports

from random import randint

## source.python imports

from effects.base import TempEntity
from engines.precache import Model
from engines.sound import StreamSound
from filters.players import PlayerIter
from listeners.tick import Delay, Repeat

## warcraft.package imports

from warcraft.commands.messages import send_wcs_saytext_by_index
from warcraft.players import player_dict
from warcraft.race import Race
from warcraft.registration import events, clientcommands
from warcraft.skill import Skill
from warcraft.utility import classproperty, CooldownDict

## __all__ declaration

__all__ = ("ShadowHunter", )

## shadowhunter declaration

godmode_sound = StreamSound("source-python/warcraft/divine_shield.wav", volume=1, download=True)

class ShadowHunter(Race):

    @classproperty
    def description(cls):
        return 'Recoded Shadow Hunter. (Kryptonite)'

    @classproperty
    def max_level(cls):
        return 99

    @classproperty
    def requirement_sort_key(cls):
        return 7


@ShadowHunter.add_skill
class HealingWave(Skill):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.repeater = Repeat(self.on_cycle, args=(self.parent.parent, ))

    @classproperty
    def description(cls):
        return 'Heals yourself and teammates within 250 range for up to 175 health.'

    @classproperty
    def max_level(cls):
        return 6

    @property
    def health(self):
        return 4 + self.level

    @property
    def max_health(self):
        return 175

    @property
    def duration(self):
        return 5 - (self.level / 2)

    @property
    def range(self):
        return 250

    _msg_a = '{{GREEN}}Healing Wave {{PALE_GREEN}}will heal {{BLUE}}teammates {{PALE_GREEN}}for {{GREEN}}{health} {{PALE_GREEN}}every {{GREEN}}{duration} seconds.'

    def on_cycle(self, player):
        team = 'ct' if player.team == 2 else 't'
        for target in PlayerIter(is_filters='alive', not_filters=team):
            distance = player.origin.get_distance(target.origin)
            if distance < self.range and target.health < self.max_health:
                target.health += self.health

    @events('player_spawn')
    def _on_player_spawn(self, player, **kwargs):
        self.repeater.start(self.duration)
        send_wcs_saytext_by_index(self._msg_a.format(health=self.health, duration=self.duration), player.index)

    @events('player_death')
    def _on_player_death(self, player, **kwargs):
        self.repeater.stop()


@ShadowHunter.add_skill
class Hex(Skill):

    @classproperty
    def description(cls):
        return '10% chance to slow your enemy for 1-3 seconds.'

    @classproperty
    def max_level(cls):
        return 6

    @property
    def duration(self):
        return 1 + (self.level / 3)

    _msg_a = '{{PALE_RED}}Hex {{PALE_GREEN}}has {{DULL_RED}}slowed {{RED}}{name}{{PALE_GREEN}}.'

    @events('player_attack')
    def _on_player_attack(self, attacker, victim, **kwargs):
        if victim.dead or victim.is_slowed or randint(0, 101) > 10:
            return

        current_speed = victim.speed
        victim.speed = 0.8
        victim.is_slowed = True
        victim.delay(self.duration, victim.__setattr__, args=('speed', current_speed))
        Delay(self.duration, victim.__setattr__, args=('is_slowed', False))
        send_wcs_saytext_by_index(self._msg_a.format(name=victim.name), attacker.index)


@ShadowHunter.add_skill
class SerpentWard(Skill):
    _model = Model('sprites/blueflare1.vmt', True)
    _model2 = Model('sprites/lgtning.vmt', True)

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.cooldowns = CooldownDict()
        self._player = self.parent.parent
        self._players_hit = set()
        self._repeater = Repeat(self._repeat, args=(self._player, ))
        self._wards = list()

        self.outer_ring = TempEntity('BeamRingPoint',
            model_index=self._model.index, halo_index=self._model.index,
            amplitude=10, red=250, green=200, blue=100, alpha=245, fade_length=100,
            start_width=10, end_width=10, speed=3)
        self.beam = TempEntity('BeamPoints', alpha=255, red=0, green=0, blue=255,
            model_index=self._model2.index, start_width=7, end_width=7,
            frame_rate=255, halo_index=self._model2.index)

    @classproperty
    def description(cls):
        return 'Place 1-2 serpent wards, dealing 5-10 damage per second to enemies within their range. Ability.'

    @classproperty
    def max_level(cls):
        return 6

    _msg_a = '{PALE_GREEN}You created a {BLUE}Serpent Ward {PALE_GREEN}at your {GREEN}location{PALE_GREEN}.'
    _msg_f = '{PALE_GREEN}You {DULL_RED}cannot {PALE_GREEN}create more {BLUE}Serpent Wards{PALE_GREEN}.'

    @property
    def range(self):
        return 250 + (20 * self.level)

    @property
    def damage(self):
        return 1 + self.level

    @property
    def duration(self):
        return 12 + (self.level / 2)

    @property
    def weapon_index(self):
        if not hasattr(self, '_player') or not self._player:
            return None

        for index in self._player.weapon_indexes():
            return index
        else:
            return None

    def _draw_ward(self, origin):
        start_point = origin.copy()
        start_point.z += 4
        self.outer_ring.create(center=start_point, start_radius=self.range, end_radius=self.range + 10, life_time=1)
        end_point = origin.copy()
        end_point.z += 150
        self.beam.create(start_point=start_point, end_point=end_point, life_time=1)

    def _delete_ward(self, origin):
        try:
            self._wards.remove(origin)
        except:
            pass

    def _repeat(self, player):
        for ward_origin in self._wards:
            end_point = ward_origin.copy()
            end_point.z += 150
            self._draw_ward(ward_origin)
            for target in player_dict.values():
                if target.origin.get_distance(ward_origin) < (self.range / 2) and target.team != player.team and not target.dead:
                    if target not in self._players_hit:
                        self._players_hit.add(target)
                        target_point = target.origin.copy()
                        target_point.z += 40
                        target.take_damage(self.damage, attacker_index=player.index, weapon_index=self.weapon_index)
                        self.beam.create(start_point=end_point, end_point=target_point, life_time=0.2, start_width=5, end_width=1)
                        Delay(1, self._players_hit.discard, args=(target, ))

    @clientcommands('ability')
    def _on_ability(self, player, **kwargs):
        if len(self._wards) > 1:
            send_wcs_saytext_by_index(self._msg_f, player.index)
            return

        location = player.origin.copy()
        self._wards.append(location)
        self._players_hit.clear()
        self._repeater.start(0.2)

        send_wcs_saytext_by_index(self._msg_a, player.index)

        Delay(self.duration, self._delete_ward, args=(location, ))

    @events('player_death', 'round_end')
    def _on_player_death(self, **kwargs):
        self._repeater.stop()
        self._wards.clear()


@ShadowHunter.add_skill
class BidBadVoodoo(Skill):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.cooldowns = CooldownDict()
        self._godmode = False
        self.model = Model("sprites/strider_bluebeam.vmt", True)
        self.model._precache()
        self.effect = TempEntity('BeamFollow', model=self.model, halo=self.model,
            alpha=255, red=220, blue=220, green=220, amplitude=10,
            end_width=20, start_width=20, fade_length=2)

        if not godmode_sound.is_precached:
            godmode_sound.precache()

    @classproperty
    def description(cls):
        return 'Gives you immunity to all damage for a short time. Ultimate.'

    @classproperty
    def max_level(cls):
        return 6

    @property
    def duration(self):
        return 1 + (self.level * 0.5)

    _msg_a = '{{RED}}Bid Bad Voodoo {{PALE_GREEN}}is active for {{ORANGE}}{time} {{PALE_GREEN}}seconds!'
    _msg_b = '{RED}Bid Bad Voodoo {PALE_GREEN}is deactivating in {ORANGE}1 {PALE_GREEN}second!'
    _msg_c = '{{RED}}Bid Bad Voodoo {{PALE_GREEN}}is on cooldown for {{DULL_RED}}{time:0.1f} seconds.'

    @events('player_spawn', 'player_upgrade_skill')
    def _on_player_spawn_reset(self, player, **kwargs):
        self.cooldowns['ultimate'] = 4
        self._godmode = False

    @events('player_pre_victim')
    def _on_player_pre_victim(self, info, **kwargs):
        if self._godmode:
            info.damage = 0

    @clientcommands('ultimate')
    def _on_player_ultimate(self, player, **kwargs):
        _cooldown = self.cooldowns['ultimate']
        if _cooldown <= 0:
            self._godmode = True
            Delay(self.duration, self.__setattr__, args=('_godmode', False))

            self.effect.create(life_time=self.duration, entity=player)

            send_wcs_saytext_by_index(self._msg_a.format(time=self.duration), player.index)
            Delay(self.duration - 1, send_wcs_saytext_by_index, args=(self._msg_b, player.index))

            godmode_sound.index = player.index
            godmode_sound.origin = player.origin
            godmode_sound.play()

            self.cooldowns['ultimate'] = (30 - self.level)
        else:
            send_wcs_saytext_by_index(self._msg_c.format(time=_cooldown), player.index)