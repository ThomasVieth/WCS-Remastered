
"""

"""

## python imports

from random import randint

## source.python imports

from effects.base import TempEntity
from engines.precache import Model
from listeners.tick import Repeat

## warcraft.package imports

from warcraft.commands.messages import send_wcs_saytext_by_index
from warcraft.players import player_dict
from warcraft.race import Race
from warcraft.registration import events, clientcommands
from warcraft.skill import Skill
from warcraft.utility import classproperty, CooldownDict

## warcraft.skills imports

from .skills.self_explode import ExplosionSkill

## __all__ declaration

__all__ = ("Terminator", )

## Terminator declaration

class Terminator(Race):

    @classproperty
    def description(cls):
        return 'Cyborg Assassin sent back in time.'

    @classproperty
    def max_level(cls):
        return 99

    @classproperty
    def requirement_sort_key(cls):
        return 19

    @classproperty
    def requirement_string(cls):
        return "Total Level 200"

    @classmethod
    def is_available(cls, player):
        return player.total_level > 200

@Terminator.add_skill
class LaserBullets(Skill):
    model = Model("sprites/lgtning.vmt")

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.model._precache()
        self.effect = TempEntity('BeamRingPoint', model=self.model,
            start_radius=20, end_radius=50, life_time=1, start_width=10,
            end_width=10, spread=10, amplitude=0, red=255, green=0, blue=0,
            alpha=255, speed=50)
    
    @classproperty
    def description(cls):
        return 'You weapons come from the future (extra damage). 8-16% chance.'

    @classproperty
    def max_level(cls):
        return 4

    @property
    def chance(self):
        return 8 + (self.level * 2)

    @property
    def extra_damage(self):
        return 5 + (self.level * 2)

    @property
    def weapon(self):
        return "weapon_deagle"

    _msg_a = '{{DULL_RED}}Laser Bullets {{PALE_GREEN}}dealt {{DULL_RED}}{damage} {{PALE_GREEN}}extra to {{RED}}{name}{{PALE_GREEN}}.'
    
    @events('player_spawn')
    def _on_player_spawn(self, player, **kwargs):
        if self.level == 0:
            return

        if player.secondary:
            player.drop_weapon(player.secondary.pointer)
        player.delay(0.2, player.give_named_item, args=(self.weapon, ))

    @events('player_pre_attack')
    def _on_player_pre_attack(self, attacker, victim, info, **kwargs):
        if victim.dead or randint(0, 101) > self.chance or self.level == 0:
            return

        damage = randint(5, self.extra_damage)
        info.damage += damage
        send_wcs_saytext_by_index(self._msg_a.format(damage=damage, name=victim.name), attacker.index)
        location = victim.origin.copy()
        location.z += 40
        self.effect.create(center=location)

@Terminator.add_skill
class MetallicSkin(Skill):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.repeater = Repeat(self.on_cycle, args=(self.parent.parent, ))
    
    @classproperty
    def description(cls):
        return 'Regenerate health over time. Max 175HP.'

    @classproperty
    def max_level(cls):
        return 4

    @property
    def health(self):
        return 2 + self.level

    def on_cycle(self, player):
        if player.health < 175:
            player.health += self.health

    @events('player_death', 'player_suicide')
    def _on_player_death(self, player, **kwargs):
        self.repeater.stop()

    @events('player_spawn')
    def _on_player_spawn(self, player, **kwargs):
        if self.level == 0:
            return

        self.repeater.start(1)

@Terminator.add_skill
class OrganicSkin(Skill):

    @classproperty
    def description(cls):
        return 'You skin changes to mimic the enemy. 30-70% chance.'

    @classproperty
    def max_level(cls):
        return 4

    @property
    def chance(self):
        return 30 + (self.level * 10)

    _msg_disguise = '{ORANGE}Organic Skin {PALE_GREEN}has provided you the {RED}enemy\'s {ORANGE}model.'

    def _find_first_player_model(self, team):
        for target in player_dict.values():
            if team == target.team_index:
                return target.model

    @events('player_spawn')
    def _on_player_spawn(self, player, **kwargs):
        if randint(0, 101) > self.chance or self.level == 0:
            return

        if player.team_index == 2: ## Is Terrorist
            player.model = self._find_first_player_model(3)
        elif player.team_index == 3: ## Is Counter-Terrorist
            player.model = self._find_first_player_model(2)
        send_wcs_saytext_by_index(self._msg_disguise, player.index)

@Terminator.add_skill
class ShortCurt(ExplosionSkill):
    
    @classproperty
    def description(cls):
        return 'When you die you body explodes.'

    @classproperty
    def max_level(cls):
        return 4

    @classmethod
    def is_available(cls, player):
        return player.race.level > 8
