"""

"""

## python imports

from random import randint

## source.python imports

from entities.constants import MoveType
from entities.helpers import pointer_from_index
from messages import Shake

## warcraft.package imports

from warcraft.commands.messages import send_wcs_saytext_by_index
from warcraft.race import Race
from warcraft.registration import events, clientcommands
from warcraft.skill import Skill
from warcraft.utility import classproperty, CooldownDict

## __all__ declaration

__all__ = ("ArchmageProudmore", )

## archmageproudmore declaration

class ArchmageProudmore(Race):

    @classproperty
    def description(cls):
        return 'Recoded Archmage Proudmore. (Kryptonite)'

    @classproperty
    def max_level(cls):
        return 99

    @classproperty
    def requirement_sort_key(cls):
        return 6


@ArchmageProudmore.add_skill
class Earthquake(Skill):

    @classproperty
    def description(cls):
        return '0 - 12% chance upon damaging an enemy to shake them.'

    @classproperty
    def max_level(cls):
        return 6

    _msg_a = '{{ORANGE}}Earthquake {{PALE_GREEN}}has shaken {{RED}}{name}{{PALE_GREEN}}!'

    @events('player_attack')
    def _on_player_hurt_shake(self, attacker, victim, **eargs):
        if randint(0, 101) <= self.level * 2:
            Shake(100, 1.5).send(victim.index)
            send_wcs_saytext_by_index(self._msg_a.format(name=victim.name), attacker.index)


@ArchmageProudmore.add_skill
class BroomOfVelocity(Skill):

    @classproperty
    def description(cls):
        return "Grants you 10-34% more movement speed."

    @classproperty
    def max_level(cls):
        return 6

    @events('player_spawn')
    def _on_player_spawn(self, player, **kwargs):
        if self.level == 0:
            return

        player.speed += 0.1 + (0.04 * self.level)


@ArchmageProudmore.add_skill
class WeaponOfTheSorcerer(Skill):
    _weapon_list = (
        "weapon_deagle",
        "weapon_deagle",
        "weapon_deagle",
        "weapon_m4a1",
        "weapon_m4a1",
        "weapon_m4a1"
    )

    @classproperty
    def description(cls):
        return "30-60% Chance to receive a Deagle and M4A4."

    @classproperty
    def max_level(cls):
        return 6

    @property
    def chance(self):
        return 30 + (self.level * 5)

    @property
    def weapon(self):
        return self._weapon_list[self.level - 1]
    
    @events('player_spawn')
    def _on_player_spawn(self, player, **kwargs):
        if self.level == 0:
            return

        if randint(0, 101) <= self.chance:
            for index in player.weapon_indexes(not_filters='knife'):
                player.drop_weapon(pointer_from_index(index))
            player.delay(0.2, player.give_named_item, args=(self.weapon, ))
            if self.level > 4:
                player.delay(0.2, player.give_named_item, args=(self._weapon_list[0], ))


@ArchmageProudmore.add_skill
class LiftOff(Skill):
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.cooldowns = CooldownDict()

    @classproperty
    def description(cls):
        return 'You can fly, while flying you\'ll recieve 8 - 20 extra health.'

    @classproperty
    def max_level(cls):
        return 6

    @classmethod
    def is_available(cls, player):
        return player.race.level > 8

    @property
    def health(self):
        return 8 + (self.level * 2)

    _msg_c = '{{BLUE}}Lift Off {{PALE_GREEN}}is on cooldown for {{DULL_RED}}{time:0.1f} {{PALE_GREEN}}seconds.'

    @clientcommands('ultimate')
    def _on_player_ultimate(self, player, **eargs):
        _cooldown = self.cooldowns['ultimate']
        if _cooldown <= 0:
            player.move_type = MoveType.WALK if player.move_type == MoveType.FLY else MoveType.FLY
            player.health += self.health
            self.cooldowns['ultimate'] = (7 - self.level)
        else:
            send_wcs_saytext_by_index(self._msg_c.format(time=_cooldown), player.index)