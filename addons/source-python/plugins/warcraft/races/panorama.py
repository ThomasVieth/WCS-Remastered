"""

"""

## python imports

from random import randint

## source.python imports

from effects.base import TempEntity
from engines.precache import Model
from engines.sound import Sound
from entities.entity import Entity

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

## panorama declaration

zoom_in_sound = Sound("items/nvg_on.wav")
zoom_out_sound = Sound("items/nvg_off.wav")

class Panorama(Race):

    @classproperty
    def description(cls):
        return ''

    @classproperty
    def max_level(cls):
        return 99

    @classproperty
    def requirement_sort_key(cls):
        return 16

    @classmethod
    def is_available(cls, player):
        return player.total_level > 200

    @classproperty
    def requirement_string(cls):
        return "Total Level 200"


@Panorama.add_skill
class WallClimb(Skill):

    @classproperty
    def description(cls):
        return 'Walk over walls in 1 step.'

    @classproperty
    def max_level(cls):
        return 4

    @property
    def range(self):
        return min(45 + (self.level * 30), 150)

    _msg_spawn = "{BLUE}Wall Climb {PALE_GREEN}has {ORANGE}enabled {PALE_GREEN}you to walk over {ORANGE}obstacles{PALE_GREEN}."

    @events('player_spawn')
    def _on_player_spawn(self, player, **kwargs):
        if self.level == 0:
            return

        player.set_property_float("localdata.m_Local.m_flStepSize", float(self.range))
        send_wcs_saytext_by_index(self._msg_spawn, player.index)


@Panorama.add_skill
class ViewFlip(Skill):

    @classproperty
    def description(cls):
        return 'Flip the enemies view upside down. 0-8% chance.'

    @classproperty
    def max_level(cls):
        return 4

    @property
    def chance(self):
        return self.level * 2

    _msg_flip = "{BLUE}View Flip {PALE_GREEN}has {ORANGE}flipped {PALE_GREEN}the {DULL_RED}enemies {ORANGE}view{PALE_GREEN}."

    @events('player_attack')
    def _on_player_spawn(self, attacker, victim, **kwargs):
        if self.level == 0 or randint(0, 101) > self.chance:
            return

        victim.set_property_int("m_iFOV", 500)
        victim.delay(0.5, attacker.set_property_int, args=("m_iFOV", 0))
        send_wcs_saytext_by_index(self._msg_flip, attacker.index)


@Panorama.add_skill
class Rematch(Skill):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.weapons = []
        self.location = None
        self.location2 = None

    @classproperty
    def description(cls):
        return 'Go back in time and rematch your enemy, 14-30% chance.'

    @classproperty
    def max_level(cls):
        return 4

    @property
    def chance(self):
        return 14 + (self.level * 4)

    _msg_a = '{ORANGE}Rematch {PALE_GREEN}in {GREEN}1 {PALE_GREEN}second.'
    _msg_b = '{ORANGE}Panorama {PALE_GREEN}called for a {ORANGE}rematch {PALE_GREEN}in {GREEN}1 {PALE_GREEN}second.'

    def _force_drop_weapons(self, player):
        for index in player.weapon_indexes(not_filters='knife'):
            entity = Entity(index)
            player.drop_weapon(entity.pointer, None, None)

    @events('player_pre_victim')
    def _on_pre_death_obtain_weapons(self, attacker, victim, **kwargs):
        self.weapons = [Entity(index).class_name for index in victim.weapon_indexes(
                not_filters='knife')
            ]
        self.location = victim.origin.copy()
        self.location.z += 1
        self.location2 = attacker.origin.copy()
        self.location2.z += 1

    @events('player_death')
    def _on_death_respawn(self, player, attacker, **kwargs):
        if self.level == 0:
            return
            
        if randint(1, 101) <= 100:##self.chance:
            player.delay(1, player.spawn)
            player.delay(1.5, self._force_drop_weapons, args=(player, ))
            for weapon in self.weapons:
                player.delay(2.5, player.give_named_item, args=(weapon, ))
            if self.location:
                player.delay(1.7, player.teleport, args=(self.location, ))
                attacker.delay(2, attacker.teleport, args=(self.location2, ))

            send_wcs_saytext_by_index(self._msg_a, player.index)
            send_wcs_saytext_by_index(self._msg_b, attacker.index)


@Panorama.add_skill
class Zoom(Skill):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.cooldowns = CooldownDict()
        self.in_zoom = False

    @classproperty
    def description(cls):
        return 'Use a scope on any weapon. Ultimate.'

    @classproperty
    def max_level(cls):
        return 4

    @classmethod
    def is_available(cls, player):
        return player.race.level > 8

    @property
    def fov(self):
        return 45 - (self.level * 9)

    _msg_a = '{GREEN}Zoomed in{PALE_GREEN}!'
    _msg_b = '{GREEN}Zoomed out{PALE_GREEN}!'
    _msg_c = '{{GREEN}}Zoom {{PALE_GREEN}}is on cooldown for {{DULL_RED}}{time:0.1f} {{PALE_GREEN}}seconds.'

    @clientcommands('ultimate')
    def _on_player_ultimate(self, player, **kwargs):
        if self.level == 0:
            return
            
        _cooldown = self.cooldowns['ultimate']
        if _cooldown <= 0:
            if self.in_zoom:
                player.set_property_int("m_iFOV", self.fov)
                player.client_command("r_screenoverlay sprites/reticle.vmt", True)
                send_wcs_saytext_by_index(self._msg_a, player.index)
                self.in_zoom = False
            else:
                player.set_property_int("m_iFOV", 0)
                player.client_command("r_screenoverlay 0", True)
                send_wcs_saytext_by_index(self._msg_b, player.index)
                self.in_zoom = True
        else:
            send_wcs_saytext_by_index(self._msg_c.format(time=_cooldown), player.index)