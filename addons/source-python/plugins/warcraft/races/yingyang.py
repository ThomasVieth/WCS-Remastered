
"""

"""

## python imports

from random import randint

## source.python imports

from messages import Fade

## warcraft.package imports

from warcraft.commands.messages import send_wcs_saytext_by_index
from warcraft.players import player_dict
from warcraft.race import Race
from warcraft.registration import events, clientcommands
from warcraft.skill import Skill
from warcraft.utility import classproperty, CooldownDict

## __all__ declaration

__all__ = ("YingYang", )

## YingYang declaration

class YingYang(Race):

    @classproperty
    def description(cls):
        return ''

    @classproperty
    def max_level(cls):
        return 99

    @classproperty
    def requirement_sort_key(cls):
        return 18

    @classmethod
    def is_available(cls, player):
        return player.total_level > 200

    @classproperty
    def requirement_string(cls):
        return "Total Level 200"
        

@YingYang.add_skill
class BalanceOfDark(Skill):
    
    @classproperty
    def description(cls):
        return 'Blinds your enemy for 2-5 seconds. 20-32% chance.'

    @classproperty
    def max_level(cls):
        return 6

    @property
    def chance(self):
        return 20 + (self.level * 2)

    @property
    def duration(self):
        return 2 + (self.level * 0.5)

    _msg_blind = "{{DARK_BLUE}}Balance of Dark {{PALE_GREEN}}has {{BLUE}}blinded {{RED}}{name}{{PALE_GREEN}}."

    @events('player_attack')
    def _on_player_attack(self, attacker, victim, **kwargs):
        if randint(0, 101) > self.chance or self.level == 0:
            return

        Fade(self.duration - 2, self.duration - (self.level * 0.5)).send(victim.index)
        send_wcs_saytext_by_index(self._msg_blind.format(name=victim.name), attacker.index)


@YingYang.add_skill
class BalanaceOfLight(Skill):
    
    @classproperty
    def description(cls):
        return 'You provide your team with 0-30 more health.'

    @classproperty
    def max_level(cls):
        return 6

    @property
    def health(self):
        return self.level * 5

    _msg_spawn = "{{WHITE}}Balance of Light {{PALE_GREEN}}has {{GREEN}}healed {{PALE_GREEN}}your team for {{GREEN}}{health}HP{{PALE_GREEN}}."

    @events('player_spawn')
    def _on_player_spawn(self, player, **kwargs):
        for target in player_dict.values():
            if target.team == player.team and not target.dead:
                target.health += self.health

        send_wcs_saytext_by_index(self._msg_spawn.format(health=self.health), player.index)

@YingYang.add_skill
class Balance(Skill):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.cooldowns = CooldownDict()
    
    @classproperty
    def description(cls):
        return 'Restores 30-60 health.'

    @classproperty
    def max_level(cls):
        return 6

    @classmethod
    def is_available(cls, player):
        return player.race.level > 8

    @property
    def time(self):
        return 40

    def calc_health(self, player):
        return 30 + (self.level * 5)

    _msg_b = '{{GREY}}Balance {{GREEN}}healed {{PALE_GREEN}}you for {{GREEN}}{health}HP{{PALE_GREEN}}.'
    _msg_c = '{{GREY}}Balance {{PALE_GREEN}}is on cooldown for {{DULL_RED}}{time:0.1f} {{PALE_GREEN}}seconds.'
    _msg_f1 = '{GREY}Balance {RED}failed {PALE_GREEN}due to you cannot gain more {GREEN}HP{PALE_GREEN}.'

    @events('player_spawn')
    def _on_player_spawn_reset(self, player, **eargs):
        self.cooldowns['ultimate'] = 4

    @clientcommands('ultimate')
    def _on_player_ultimate(self, player, **eargs):
        _cooldown = self.cooldowns['ultimate']
        if _cooldown <= 0:
            if player.health < 200:
                health = self.calc_health(player)
                player.health += health
                send_wcs_saytext_by_index(self._msg_b.format(health=health), player.index)
                self.cooldowns['ultimate'] = self.time
            else:
                send_wcs_saytext_by_index(self._msg_f1, player.index)
        else:
            send_wcs_saytext_by_index(self._msg_c.format(time=_cooldown), player.index)