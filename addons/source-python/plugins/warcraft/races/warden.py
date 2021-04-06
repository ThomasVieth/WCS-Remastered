"""

"""

## python imports

from random import choice, randint

## source.python imports

from entities import TakeDamageInfo
from messages import Shake

## warcraft.package imports

from warcraft.commands.messages import send_wcs_saytext_by_index
from warcraft.players import player_dict
from warcraft.race import Race
from warcraft.registration import events, clientcommands
from warcraft.skill import Skill
from warcraft.utility import classproperty, CooldownDict

## __all__ declaration

__all__ = ("Warden", )

## warden declaration

class Warden(Race):

    @classproperty
    def description(cls):
        return 'Recoded Warden. (Kryptonite)'

    @classproperty
    def max_level(cls):
        return 99

    @classproperty
    def requirement_sort_key(cls):
        return 8


@Warden.add_skill
class Impale(Skill):

    @classproperty
    def description(cls):
        return 'Upon attacking, knock your enemy up and shake. 7-15% chance.'

    @classproperty
    def max_level(cls):
        return 8

    _msg_a = '{{PALE_GREEN}}You {{DULL_RED}}impaled {{RED}}{name}{{GREEN}}!'

    @events('player_pre_attack')
    def _on_player_pre_attack_impale(self, attacker, victim, **kwargs):
        if randint(1, 100) <= 7 + self.level and not victim.dead:
            victim.push(1, 200, True)
            Shake(100, 1.5).send(victim.index)
            send_wcs_saytext_by_index(self._msg_a.format(name=victim.name), attacker.index)


@Warden.add_skill
class SpikedCarapace(Skill):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.total_damage_prevented = 0

    @classproperty
    def description(cls):
        return 'Reduces incoming damage by 5-20% and deal 3-7 reflected damage when being attacked.'

    @classproperty
    def max_level(cls):
        return 8

    @property
    def reduction(self):
        return min(5 + (2 * self.level), 20)

    @property
    def reflect_damage(self):
        return 3 + (self.level / 2)

    _msg_a = '{{GREEN}}Spiked Carapace {{PALE_GREEN}}prevented {{DULL_RED}}{damage} {{PALE_GREEN}}last round.'

    @events('player_spawn')
    def _on_player_spawn(self, player, **kwargs):
        send_wcs_saytext_by_index(self._msg_a.format(damage=int(self.total_damage_prevented)), player.index)
        self.total_damage_prevented = 0

    @events('player_pre_victim')
    def _on_player_pre_victim(self, attacker, victim, info, **kwargs):
        multiplier = 1 - (self.reduction / 100)
        old_damage = info.damage
        info.damage *= multiplier
        reduced_damage = old_damage - info.damage
        self.total_damage_prevented += reduced_damage

    @events('player_victim')
    def _on_player_victim(self, attacker, victim, **kwargs):
        if attacker.dead:
            return

        info = TakeDamageInfo()
        info.inflictor = victim.index
        info.damage = self.reflect_damage
        attacker.on_take_damage.call_trampoline(info)


@Warden.add_skill
class ShadowStrike(Skill):

    @classproperty
    def description(cls):
        return 'Grants you 7-15% chance to deal an additional 9-17 damage when attacking.'

    @classproperty
    def max_level(cls):
        return 8

    @property
    def extra_damage(self):
        return 9 + self.level
    
    @property
    def chance(self):
        return 7 + self.level

    _msg_a = '{{DARK_BLUE}}Shadow Strike {{PALE_GREEN}}dealt {{DULL_RED}}{damage} {{PALE_GREEN}}extra to {{RED}}{name}{{PALE_GREEN}}.'

    @events('player_pre_attack')
    def _on_player_pre_attack(self, attacker, victim, info, **kwargs):
        if randint(0, 101) <= self.chance and not victim.dead:
            info.damage += self.extra_damage
            send_wcs_saytext_by_index(self._msg_a.format(damage=self.extra_damage, name=victim.name), attacker.index)


@Warden.add_skill
class LocustSwarm(Skill):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.cooldowns = CooldownDict()

    @classproperty
    def description(cls):
        return 'Leech 35 health and 5-40 armour from a random enemy.'

    @classproperty
    def max_level(cls):
        return 8

    @property
    def health(self):
        return 35
    
    @property
    def armour(self):
        return min(5 + (5 * self.level), 40)

    @property
    def cooldown(self):
        return max(35 - (2 * self.level), 20)
    

    _msg_a = '{{BRIGHT_GREEN}}Locust Swarm {{PALE_GREEN}}leeched {{DULL_RED}}{health} {{PALE_GREEN}}health and {{DULL_RED}}{armour} {{PALE_GREEN}}armour from {{RED}}{name}{{PALE_GREEN}}.'
    _msg_c = '{{BRIGHT_GREEN}}Locust Swarm {{PALE_GREEN}}is on {{DULL_RED}}cooldown {{PALE_GREEN}}for {time:0.1f} seconds.'
    _msg_f = '{BRIGHT_GREEN}Locust Swarm {DULL_RED}cannot find a target.'

    @clientcommands('ultimate')
    def _on_player_ultimate(self, player, **kwargs):
        _cooldown = self.cooldowns['ultimate']
        if _cooldown <= 0:
            enemy_team = 5 - player.team
            all_players = player_dict.values()
            possible_players = list(filter(lambda x: x.team == enemy_team and not x.dead, all_players))
            if len(possible_players) > 0:
                target = choice(possible_players)
                target.armor -= self.armour
                target.take_damage(self.health, attacker_index=player.index, skip_hooks=True)
                player.health += self.health
                player.armor += self.armour
                send_wcs_saytext_by_index(self._msg_a.format(health=self.health, armour=self.armour, name=target.name), player.index)
                self.cooldowns['ultimate'] = self.cooldown
            else:
                send_wcs_saytext_by_index(self._msg_f, player.index)
        else:
            send_wcs_saytext_by_index(self._msg_c.format(time=_cooldown), player.index)