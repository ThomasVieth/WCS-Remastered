"""

"""

## python imports

from random import randint

## source.python imports

from filters.weapons import WeaponClassIter
from listeners.tick import Delay
from players.constants import PlayerButtons

## warcraft.package imports

from warcraft.commands.messages import send_wcs_saytext_by_index
from warcraft.race import Race
from warcraft.registration import events, clientcommands
from warcraft.skill import Skill
from warcraft.utility import classproperty, CooldownDict

## __all__ declaration

__all__ = ("DemonHunter", )

## demonhunter declaration

_knifeonly = set(weapon.basename for weapon in WeaponClassIter(not_filters='knife'))

class DemonHunter(Race):
    image = "https://cdn.discordapp.com/attachments/829011612631302204/831967566850949170/demon_hunter.png"

    @classproperty
    def description(cls):
        return 'Dark warriors, shunned by the night elves.'

    @classproperty
    def max_level(cls):
        return 99

    @classproperty
    def requirement_sort_key(cls):
        return 14

    @classmethod
    def is_available(cls, player):
        return player.total_level > 160

    @classproperty
    def requirement_string(cls):
        return "Total Level 160"

@DemonHunter.add_skill
class DoubleJump(Skill):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.has_jumped = False

    @classproperty
    def description(cls):
        return 'Jump for a second time whilst in mid-air.'

    @classproperty
    def max_level(cls):
        return 4

    @property
    def _delay(self):
        return 1.5 - 0.1 * self.level

    @events('player_spawn', 'player_upgrade_skill')
    def _on_reset_jump(self, player, **kwargs):
        self.has_jumped = False

    @events('player_pre_run_command')
    def _on_player_run_command(self, player, usercmd, **kwargs):
        if self.level == 0:
            return

        if usercmd.buttons & PlayerButtons.JUMP and not player.buttons & PlayerButtons.JUMP and not self.has_jumped:
            if player.ground_entity == -1:
                self.has_jumped = True
                player.push(1, 300, True)
                Delay(self._delay, setattr, args=(self, 'has_jumped', False))


@DemonHunter.add_skill
class ManaBurn(Skill):

    @classproperty
    def description(cls):
        return 'Bolts of negative energy remove the enemies cash.'

    @classproperty
    def max_level(cls):
        return 8

    _msg_a = '{{GREEN}}Mana Burn {{DULL_RED}}removed {{BLUE}}${cash} {{PALE_GREEN}}from your bank.'
    _msg_b = '{{GREEN}}Mana Burn {{DULL_RED}}removed {{BLUE}}${cash} {{PALE_GREEN}}from {{RED}}{name}\'s {{PALE_GREEN}}bank.'

    @property
    def _cash(self):
        return (self.level + 5) * 20

    @events('player_attack')
    def _on_player_attack(self, attacker, victim, **kwargs):
        if randint(1, 100) > 30 or victim.cash < self._cash or self.level == 0:
            return

        victim.cash -= self._cash
        send_wcs_saytext_by_index(self._msg_a.format(cash=self._cash), victim.index)
        send_wcs_saytext_by_index(self._msg_b.format(cash=self._cash, name=victim.name), attacker.index)


@DemonHunter.add_skill
class Evasion(Skill):

    @classproperty
    def description(cls):
        return 'Gives the Demon Hunter a chance to avoid attacks.'

    @classproperty
    def max_level(cls):
        return 8

    _msg_a = '{{GREEN}}Evasion {{PALE_GREEN}}evaded {{DULL_RED}}{damage:0.0f} {{PALE_GREEN}}damage.'

    @property
    def _chance(self):
        return 20 + self.level * 2

    @events('player_pre_victim')
    def _on_player_pre_victim(self, victim, info, **eargs):
        if randint(1, 100) > self._chance or self.level == 0:
            return

        send_wcs_saytext_by_index(self._msg_a.format(damage=info.damage), victim.index)
        info.damage = 0


@DemonHunter.add_skill
class DemonicTransformation(Skill):
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.cooldowns = CooldownDict()
        self._status = True
        self._weapons = list()

    @classproperty
    def description(cls):
        return 'Transform into a demon, restricted to melee combat.'

    @classproperty
    def max_level(cls):
        return 8

    @classmethod
    def is_available(cls, player):
        return player.race.level > 8

    _msg_c = '{{RED}}Demonic Tranformation {{PALE_GREEN}}is on cooldown {{PALE_GREEN}}for {{DULL_RED}}{time:0.1f} {{PALE_GREEN}}seconds.'

    @events('player_spawn', 'player_suicide')
    def _on_player_spawn_reset(self, player, **eargs):
        if self.level == 0:
            return

        color = player.color
        color.a = 255
        player.color = color
        self._status = True
        self.cooldowns['ultimate'] = 4
        player.unrestrict_weapons(*_knifeonly)
        if len(self._weapons) > 0:
            for weapon in self._weapons:
                player.give_named_item(weapon, 0, None, True)
        self._weapons.clear()

    @clientcommands('ultimate')
    def _on_player_ultimate(self, player, **eargs):
        if self.level == 0:
            return

        _cooldown = self.cooldowns['ultimate']
        if _cooldown <= 0:
            if self._status:
                for weapon in player.weapons(not_filters='knife'):
                    self._weapons.append(weapon.class_name)
                player.restrict_weapons(*_knifeonly)
                player.speed = 1.5
                player.health += 15 * self.level
                color = player.color
                color.a = 255 - 20 * self.level
                player.color = color
                self._status = False
            else:
                player.unrestrict_weapons(*_knifeonly)
                for weapon in self._weapons:
                    player.delay(0.2, player.give_named_item, args=(weapon, 0, None, True))
                self._weapons.clear()
                player.speed = 1
                player.health = 100
                color = player.color
                color.a = 255
                player.color = color
                self._status = True
            self.cooldowns['ultimate'] = 10
        else:
            send_wcs_saytext_by_index(self._msg_c.format(time=_cooldown), player.index)