"""

"""

## python imports

from random import randint

## source.python imports

from effects.base import TempEntity
from engines.precache import Model
from engines.sound import StreamSound
from entities.entity import Entity
from listeners.tick import Delay

## warcraft.package imports

from warcraft.commands.messages import send_wcs_saytext_by_index
from warcraft.effects import attach_entity_to_player
from warcraft.race import Race
from warcraft.registration import events, clientcommands
from warcraft.skill import Skill
from warcraft.utility import classproperty, CooldownDict

## __all__ declaration

__all__ = ("DwarfPaladin", )

## dwarfpaladin declaration

godmode_sound = StreamSound("source-python/warcraft/divine_shield.wav", volume=1, download=True)
heal_sound = StreamSound("source-python/warcraft/heal.wav", volume=1, download=True)
stun_sound = StreamSound("source-python/warcraft/hammer.wav", volume=1, download=True)

class DwarfPaladin(Race):

    @classproperty
    def description(cls):
        return 'Dwarfs control the mountains, being highly trained engineers.'

    @classproperty
    def max_level(cls):
        return 99

    @classmethod
    def is_available(cls, player):
        return player.total_level > 100

    @classproperty
    def requirement_string(cls):
        return "Total Level 100"

    @classproperty
    def requirement_sort_key(cls):
        return 102


@DwarfPaladin.add_skill
class Stoneskin(Skill):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.total_damage_prevented = 0

    @classproperty
    def description(cls):
        return 'Decreases all damage to you, 6 - 16%.'

    @classproperty
    def max_level(cls):
        return 6

    _msg_a = '{{GREEN}}Stoneskin {{PALE_GREEN}}prevented {{DULL_RED}}{damage} {{PALE_GREEN}}last round.'

    @events('player_spawn')
    def _on_player_spawn(self, player, **kwargs):
        send_wcs_saytext_by_index(self._msg_a.format(damage=int(self.total_damage_prevented)), player.index)
        self.total_damage_prevented = 0

    @events('player_pre_victim')
    def _on_player_pre_victim(self, attacker, victim, info, **kwargs):
        reduction = (6 + (2 * self.level)) / 100
        multiplier = 1 - reduction
        old_damage = info.damage
        info.damage *= multiplier
        self.total_damage_prevented += (old_damage - info.damage)


@DwarfPaladin.add_skill
class HammerOfJustice(Skill):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._model = Model("sprites/lgtning.vmt", True)
        self._model._precache()

        if not stun_sound.is_precached:
            stun_sound.precache()

    @classproperty
    def description(cls):
        return 'Slam your hammer into the ground, to knock up and enemy and stun them.'

    @classproperty
    def max_level(cls):
        return 6

    @events('player_pre_attack')
    def _on_player_pre_attack(self, attacker, victim, **kwargs):
        if randint(1, 100) < 10 + self.level and not victim.stuck:
            victim.push(1, 200, False)
            victim.delay(0.8, victim.__setattr__, args=('stuck', True))
            victim.delay(1.8, victim.__setattr__, args=('stuck', False))

            bottom_vector = victim.origin
            top_vector = victim.origin
            top_vector.z += 100
            _effect = TempEntity('BeamPoints', alpha=255, red=100, blue=255, green=100, amplitude=10,
                end_width=20, start_width=20, life_time=2, fade_length=2, halo_index=self._model.index,
                model_index=self._model.index, start_point=top_vector, end_point=bottom_vector)
            _effect.create()

            stun_sound.index = victim.index
            stun_sound.origin = victim.origin
            stun_sound.play()

@DwarfPaladin.add_skill
class HolyLight(Skill):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.cooldowns = CooldownDict()
        self._model = Model("sprites/lgtning.vmt", True)
        self._model._precache()

        if not heal_sound.is_precached:
            heal_sound.precache()

    @classproperty
    def description(cls):
        return 'Heal yourself for a small amount. Max 250HP. Ability.'

    @classproperty
    def max_level(cls):
        return 6

    @property
    def health(self):
        return 10 + (4 * self.level)

    _msg_a = '{{YELLOW}}Holy Light {{PALE_GREEN}}healed you for {{GREEN}}{amount}'
    _msg_c = '{{YELLOW}}Holy Light {{PALE_GREEN}}is on cooldown for {{DULL_RED}}{time} {{PALE_GREEN}}seconds.'

    @events('player_spawn', 'player_upgrade_skill')
    def _on_player_spawn(self, player, **kwargs):
        self.cooldowns['ability'] = 4

    @clientcommands('ability')
    def _on_player_ability(self, player, **kwargs):
        _cooldown = self.cooldowns['ability']
        if _cooldown <= 0:
            player.health = min(player.health + self.health, 250)
            send_wcs_saytext_by_index(self._msg_a.format(amount=self.health), player.index)

            location = player.origin
            location.z += 40
            self._effect = TempEntity('GlowSprite', model_index=self._model.index,
                life_time=0.8, amplitude=6, origin=location, scale=1.5, brightness=255)
            self._effect.create()

            heal_sound.index = player.index
            heal_sound.origin = location
            heal_sound.play()

            self.cooldowns['ability'] = 10

        else:
            send_wcs_saytext_by_index(self._msg_c.format(time=int(_cooldown)), player.index)


@DwarfPaladin.add_skill
class DivineShield(Skill):

    @classproperty
    def description(cls):
        return 'Gives you immunity to all damage for a short time. Ultimate.'

    @classproperty
    def max_level(cls):
        return 4

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.cooldowns = CooldownDict()
        self._godmode = False
        self._model = Model("sprites/halo.vmt", True)
        self._model._precache()

        if not godmode_sound.is_precached:
            godmode_sound.precache()

    def kill_effect(self, effect):
        if not effect.basehandle.is_valid():
            return
        effect.call_input('Kill')

    _msg_a = '{{ORANGE}}Divine Shield {{PALE_GREEN}}is active for {{ORANGE}}{time} {{PALE_GREEN}}seconds!'
    _msg_c = '{{ORANGE}}Divine Shield {{PALE_GREEN}}is on {{DULL_RED}}cooldown {{PALE_GREEN}}for {time:0.1f} seconds.'

    @events('player_spawn', 'player_upgrade_skill')
    def _on_player_spawn_reset(self, player, **eargs):
        self.cooldowns['ultimate'] = 4
        self._godmode = False

    @events('player_pre_victim')
    def _on_player_pre_victim(self, info, **eargs):
        if self._godmode:
            info.damage = 0

    @clientcommands('ultimate')
    def _on_player_ultimate(self, player, **eargs):
        _cooldown = self.cooldowns['ultimate']
        if _cooldown <= 0:
            duration = (self.level * 0.5) + 1
            self._godmode = True
            Delay(duration, self.__setattr__, args=('_godmode', False))

            effect = Entity.create('env_sprite')

            location = player.origin
            location.z += 40
            effect.teleport(location, None, None)
            effect.add_output('model sprites/halo.vmt')
            effect.add_output('scale 10')
            effect.call_input('ShowSprite')
            attach_entity_to_player(player, effect)
            Delay(duration, self.kill_effect, args=(effect, ))

            send_wcs_saytext_by_index(self._msg_a.format(time=duration), player.index)

            godmode_sound.index = player.index
            godmode_sound.origin = player.origin
            godmode_sound.play()

            self.cooldowns['ultimate'] = 20
        else:
            send_wcs_saytext_by_index(self._msg_c.format(time=_cooldown), player.index)