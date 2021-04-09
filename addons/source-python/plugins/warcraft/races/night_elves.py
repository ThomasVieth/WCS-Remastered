"""

"""

## python imports

from random import randint

## source.python imports

from effects.base import TempEntity
from engines.sound import StreamSound
from engines.precache import Model
from entities import TakeDamageInfo
from filters.players import PlayerIter

## warcraft.package imports

from warcraft.commands.messages import send_wcs_saytext_by_index
from warcraft.race import Race
from warcraft.registration import events, clientcommands
from warcraft.skill import Skill
from warcraft.utility import classproperty, CooldownDict

## __all__ declaration

__all__ = ("NightElves", )

## OrcishHorde declaration

root_sound = StreamSound('source-python/warcraft/root.mp3', download=True)

class NightElves(Race):
    
    @classproperty
    def description(cls):
        return 'Recoded Night Elves. (Kryptonite)'

    @classproperty
    def max_level(cls):
        return 99

    @classproperty
    def requirement_sort_key(cls):
        return 4

@NightElves.add_skill
class EvasionAura(Skill):

    @classproperty
    def description(cls):
        return 'Gives the Night Elves a chance to avoid attacks 5-21%.'

    @classproperty
    def max_level(cls):
        return 8

    _msg_a = '{{GREEN}}Evasion Aura {{PALE_GREEN}}evaded {{DULL_RED}}{damage:0.0f} {{PALE_GREEN}}damage.'

    @property
    def _chance(self):
        return 5 + (self.level * 2)

    @events('player_pre_victim')
    def _on_player_pre_victim(self, victim, info, **eargs):
        if randint(1, 100) > self._chance:
            return

        send_wcs_saytext_by_index(self._msg_a.format(damage=info.damage), victim.index)
        info.damage = 0


@NightElves.add_skill
class ThornsAura(Skill):

    @classproperty
    def description(cls):
        return 'Gives the Night Elves a chance to reflect attacks 0-16% dealing 6-14 damage.'

    @classproperty
    def max_level(cls):
        return 8

    @property
    def reflect_damage(self):
        return 6 + self.level

    _msg_a = '{{GREEN}}Thorns Aura {{PALE_GREEN}}reflected {{DULL_RED}}{damage} {{PALE_GREEN}}to {{RED}}{name}{{PALE_GREEN}}.'

    @events('player_victim')
    def _on_player_victim(self, attacker, victim, **kwargs):
        if attacker.dead or randint(0, 101) > (self.level * 2):
            return

        info = TakeDamageInfo()
        info.inflictor = victim.index
        info.damage = self.reflect_damage
        attacker.on_take_damage.call_trampoline(info)
        send_wcs_saytext_by_index(self._msg_a.format(damage=self.reflect_damage, name=attacker.name), victim.index)


@NightElves.add_skill
class TrueshotAura(Skill):

    @classproperty
    def description(cls):
        return 'Gives the Night Elves a chance to deal 5-21 extra damage, 7-15% chance.'

    @classproperty
    def max_level(cls):
        return 8

    _msg_a = '{{GREEN}}Trueshot Aura {{PALE_GREEN}}dealt {{DULL_RED}}{damage} {{PALE_GREEN}}extra to {{RED}}{name}{{PALE_GREEN}}.'

    @events('player_pre_attack')
    def _on_player_pre_attack(self, attacker, victim, info, **kwargs):
        if victim.dead or randint(0, 101) > (self.level + 7):
            return

        extra_damage = (5 + (self.level * 2))
        info.damage += extra_damage
        send_wcs_saytext_by_index(self._msg_a.format(damage=extra_damage, name=victim.name), attacker.index)


@NightElves.add_skill
class EntanglingRoots(Skill):
    laser = Model('sprites/blueflare1.vmt', True)

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.cooldowns = CooldownDict()
        self.beam = TempEntity('BeamPoints', alpha=255, red=0, green=200, blue=0,
            life_time=1.0, start_width=15, end_width=15, frame_rate=255)
        self.laser._precache()
        self.effect = TempEntity('BeamRingPoint', start_radius=120,
            end_radius=0, model_index=self.laser.index, halo_index=self.laser.index,
            life_time=1.5, amplitude=10, red=10, green=255, blue=10, alpha=245, flags=0,
            start_width=6, end_width=6)

    @classproperty
    def description(cls):
        return 'Roots every enemy within 225-400 range making them unable to move for 2-3 seconds.'

    @classproperty
    def max_level(cls):
        return 8

    @property
    def range(self):
        return 225 + ((self.level - 1) * 25)
    
    @property
    def duration(self):
        return 2 + (self.level * 0.125)

    _msg_a = '{GREEN}Entangling Roots rooted {RED}enemies{PALE_GREEN}!'
    _msg_c = '{{GREEN}}Entangling Roots {{PALE_GREEN}}is on cooldown for {{DULL_RED}}{time:0.1f} {{PALE_GREEN}}seconds.'
    _msg_f = '{GREEN}Entangling Roots {PALE_GREEN}found {DULL_RED}no enemies{PALE_GREEN}!'

    def _find_players_within(self, player, length=99999, exclusions=[]):
        targets = []
        team = 't' if player.team == 2 else 'ct'
        for target in PlayerIter(is_filters='alive', not_filters=team):
            distance = player.origin.get_distance(target.origin)
            if distance < length:
                targets.append(target)
        return targets

    @events('player_spawn')
    def _on_player_spawn_reset(self, player, **kwargs):
        self.cooldowns['ultimate'] = 4

    @clientcommands('ultimate')
    def _on_player_ultimate(self, player, **kwargs):
        _cooldown = self.cooldowns['ultimate']
        if _cooldown <= 0:
            last_target = player
            targets = self._find_players_within(player, self.range)

            if len(targets) == 0:
                send_wcs_saytext_by_index(self._msg_f, player.index)
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
                self.beam.create(start_point=location1, end_point=location2, halo=self.laser, model=self.laser)
                last_target = target
                self.effect.create(center=target.origin)
                self.effect.create(center=target.origin, start_radius=80)

            root_sound.index = player.index
            root_sound.origin = player.origin
            root_sound.play()

            send_wcs_saytext_by_index(self._msg_a, player.index)
            self.cooldowns['ultimate'] = 30
        else:
            send_wcs_saytext_by_index(self._msg_c.format(time=_cooldown), player.index)