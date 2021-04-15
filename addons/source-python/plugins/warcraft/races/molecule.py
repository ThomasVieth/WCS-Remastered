"""

"""

## python imports

from random import randint

## source.python imports

from effects.base import TempEntity
from engines.precache import Model
from engines.sound import Sound
from listeners.tick import Delay

## warcraft.package imports

from warcraft.commands.messages import send_wcs_saytext_by_index
from warcraft.race import Race
from warcraft.registration import events, clientcommands
from warcraft.skill import Skill
from warcraft.utility import classproperty, CooldownDict

## warcraft.skills imports

from .skills.self_add_speed import AddSpeedSkill

## __all__ declaration

__all__ = ("Molecule", )

## molecule declaration

electric_sound = Sound("ambient/energy/electric_loop.wav")

class Molecule(Race):

    @classproperty
    def description(cls):
        return ''

    @classproperty
    def max_level(cls):
        return 99

    @classproperty
    def requirement_sort_key(cls):
        return 15


@Molecule.add_skill
class Speed(AddSpeedSkill):

    @classproperty
    def description(cls):
        return "Increase your base speed."

    @classproperty
    def max_level(cls):
        return 5

    @property
    def base_speed_addition(self):
        return self.level * 0.1


@Molecule.add_skill
class ElectricShock(Skill):
    model = Model("sprites/physring1.vmt")

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.model._precache()
        self.effect = TempEntity('GlowSprite', model=self.model,
            life_time=0.5, scale=1.3, brightness=255)

    
    @classproperty
    def description(cls):
        return 'Electricute your enemy for 2-7 extra damage. 25% chance.'

    @classproperty
    def max_level(cls):
        return 5

    @property
    def extra_damage(self):
        return 2 + self.level

    _msg_a = '{{LIGHT_BLUE}}Electric Shock {{PALE_GREEN}}dealt {{DULL_RED}}{damage} {{PALE_GREEN}}extra to {{RED}}{name}{{PALE_GREEN}}.'

    @events('player_pre_attack')
    def _on_player_pre_attack(self, attacker, victim, info, **kwargs):
        if victim.dead or randint(0, 101) > 25 or self.level == 0:
            return

        electric_sound.index = victim.index
        electric_sound.origin = victim.origin
        electric_sound.play()
        Delay(0.5, electric_sound.stop)
        damage = randint(2, self.extra_damage)
        info.damage += damage
        send_wcs_saytext_by_index(self._msg_a.format(damage=damage, name=victim.name), attacker.index)
        self.effect.create(origin=victim.origin)


@Molecule.add_skill
class Evasion(Skill):

    @classproperty
    def description(cls):
        return 'Avoid attacks. 5-20% chance.'

    @classproperty
    def max_level(cls):
        return 5

    _msg_a = '{{GREEN}}Evasion {{PALE_GREEN}}evaded {{DULL_RED}}{damage:0.0f} {{PALE_GREEN}}damage.'

    @property
    def _chance(self):
        return 5 + (self.level * 3)

    @events('player_pre_victim')
    def _on_player_pre_victim(self, victim, info, **eargs):
        if randint(1, 100) > self._chance or self.level == 0:
            return

        send_wcs_saytext_by_index(self._msg_a.format(damage=info.damage), victim.index)
        info.damage = 0


@Molecule.add_skill
class Forcefield(Skill):
    model = Model("sprites/strider_blackball.vmt", True)

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.cooldowns = CooldownDict()
        self._godmode = False
        self.model._precache()
        self.effect = TempEntity('GlowSprite', model=self.model, scale=1.5, brightness=255)

    @classproperty
    def description(cls):
        return 'Provides immortality but freezes you during. Ultimate.'

    @classproperty
    def max_level(cls):
        return 5

    @property
    def duration(self):
        return 1 + (self.level * 0.4)

    _msg_a = '{{BLUE}}Forcefield {{PALE_GREEN}}is active for {{ORANGE}}{time} {{PALE_GREEN}}seconds!'
    _msg_b = '{BLUE}Forcefield {PALE_GREEN}is deactivating in {ORANGE}0.5 {PALE_GREEN}second!'
    _msg_c = '{{BLUE}}Forcefield {{PALE_GREEN}}is on cooldown for {{DULL_RED}}{time:0.1f} seconds.'

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
        if self.level == 0:
            return
            
        _cooldown = self.cooldowns['ultimate']
        if _cooldown <= 0:
            self._godmode = True
            player.stuck = True
            Delay(self.duration, self.__setattr__, args=('_godmode', False))
            Delay(self.duration, setattr, args=(player, 'stuck', False))

            self.effect.create(life_time=self.duration + 0.5, origin=player.origin)

            send_wcs_saytext_by_index(self._msg_a.format(time=self.duration), player.index)
            Delay(self.duration - 0.5, send_wcs_saytext_by_index, args=(self._msg_b, player.index))

            self.cooldowns['ultimate'] = (30 - self.level)
        else:
            send_wcs_saytext_by_index(self._msg_c.format(time=_cooldown), player.index)