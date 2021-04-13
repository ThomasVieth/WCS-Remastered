"""

"""

## python imports

from random import randint

## source.python imports

from filters.weapons import WeaponClassIter

## warcraft.package imports

from warcraft.commands.messages import send_wcs_saytext_by_index
from warcraft.race import Race
from warcraft.registration import events
from warcraft.skill import Skill
from warcraft.utility import classproperty

## __all__ declaration

__all__ = ("FlamePredator", )

## flamepredator declaration

_knifeonly = set(weapon.basename for weapon in WeaponClassIter(not_filters='knife'))

class FlamePredator(Race):

    @classproperty
    def description(cls):
        return 'Recoded Flame Predator. (Kryptonite)'

    @classproperty
    def max_level(cls):
        return 99

    @classproperty
    def requirement_sort_key(cls):
        return 11

    @events('player_spawn')
    def player_spawn(self, player, **kwargs):
        player.restrict_weapons(*_knifeonly)
        for weapon in player.weapons(not_filters='knife'):
            player.drop_weapon(weapon.pointer, None, None)

    @events('player_death')
    def player_death(self, player, **kwargs):
        player.unrestrict_weapons(*_knifeonly)

@FlamePredator.add_skill
class Berserk(Skill):

    @classproperty
    def description(cls):
        return 'Gain health and speed on spawn.'

    @classproperty
    def max_level(cls):
        return 8

    @events('player_spawn')
    def _on_player_spawn(self, player, **eargs):
        player.health += 10 * self.level
        player.speed = 1.4 + (0.05 * self.level)

@FlamePredator.add_skill
class CloakOfInvisibility(Skill):
    
    @classproperty
    def description(cls):
        return 'Put on your cloak to be 20-90% invisible.'

    @classproperty
    def max_level(cls):
        return 8

    @events('player_spawn', 'player_upgrade_skill')
    def _on_player_spawn_give_invis(self, player, **eargs):
        color = player.color
        color.a = 255 - (30 * self.level)
        player.color = color

@FlamePredator.add_skill
class Levitation(Skill):

    @classproperty
    def description(cls):
        return 'Reduce your current gravity and damage taken when jumping.'

    @classproperty
    def max_level(cls):
        return 8

    _msg_a = '{{PALE_GREEN}}Reduced {{DULL_RED}}damage taken {{PALE_GREEN}}from {{RED}}{name}.'

    @events('player_spawn')
    def _on_player_spawn(self, player, **eargs):
        player.gravity = 1 - (0.08 * self.level)

    @events('player_pre_victim')
    def _on_player_pre_victim(self, attacker, victim, info, **eargs):
        if victim.ground_entity == -1:
            info.damage *= 1 - (0.06 * self.level)
            send_wcs_saytext_by_index(self._msg_a.format(name=attacker.name), victim.index)
            ricochet = TempEntity('Armor Ricochet', position=victim.origin)
            ricochet.create()

@FlamePredator.add_skill
class ClawAttack(Skill):
    
    @classproperty
    def description(cls):
        return 'Force an enemy to drop his weapon when you attack him. 45 - 61%'

    @classproperty
    def max_level(cls):
        return 8

    _msg_a = '{{PALE_GREEN}}Force dropped {{RED}}{name}\'s {{PALE_GREEN}}weapon!'
    _msg_b = '{{RED}}{name} {{PALE_GREEN}}made you {{RED}}drop {{PALE_GREEN}}your weapon!'

    @events('player_attack')
    def _on_player_attack(self, player, victim, **eargs):
        if randint(1, 100) > (45 + (2 * self.level)):
            return

        victim.drop_weapon(victim.active_weapon.pointer, None, None)

        send_wcs_saytext_by_index(self._msg_a.format(name=victim.name), player.index)
        send_wcs_saytext_by_index(self._msg_b.format(name=player.name), victim.index)

@FlamePredator.add_skill
class BurningBlade(Skill):
    
    @classproperty
    def description(cls):
        return 'Set an enemy on fire when attacking him. 30%'

    @classproperty
    def max_level(cls):
        return 8

    _msg_a = '{{PALE_GREEN}}You have lit {{RED}}{name} {{PALE_GREEN}}on {{RED}}FIRE!'
    _msg_b = '{{RED}}{name} {{PALE_GREEN}}has lit you on {{RED}}FIRE!'

    @events('player_attack')
    def _on_player_attack(self, player, victim, **eargs):
        if randint(1, 100) > 30:
            return

        victim.ignite_lifetime(self.level)

        send_wcs_saytext_by_index(self._msg_a.format(name=victim.name), player.index)
        send_wcs_saytext_by_index(self._msg_b.format(name=player.name), victim.index)