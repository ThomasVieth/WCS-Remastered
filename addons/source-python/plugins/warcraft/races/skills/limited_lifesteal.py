"""

"""

## source.python imports

from effects.base import TempEntity
from engines.precache import Model
from weapons.manager import weapon_manager

## warcraft.package imports

from warcraft.commands.messages import send_wcs_saytext_by_index
from warcraft.registration import events
from warcraft.skill import Skill

## __all__ declaration

__all__ = ("LifestealSkill", )

## lifestealskill declaration

class LifestealSkill(Skill):
    _msg_a = '{{PALE_GREEN}}Healed {{GREEN}}{heal} {{PALE_GREEN}}HP by {{DULL_RED}}stealing {{PALE_GREEN}}life from {{RED}}{name}.'

    laser = Model("sprites/lgtning.vmt", True)
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.max_health = self.parent.parent.health + 100
        self.beam = TempEntity('BeamPoints', alpha=255, red=255, green=0, blue=0,
            life_time=1.0, model_index=self.laser.index, start_width=7, end_width=7,
            frame_rate=255, halo_index=self.laser.index)

    @property
    def chance(self):
        return self.level * 8
    
    @property
    def leech_multiplier(self):
        return 0.6

    @events('player_spawn')
    def _on_player_spawn(self, player, **kwargs):
        self.max_health = player.health + 100

    @events('player_pre_attack')
    def _on_player_pre_attack(self, attacker, victim, info, **kwargs):
        if self.level == 0:
            return

        heal = int(info.damage * self.leech_multiplier)
        can_heal = self.max_health > attacker.health + heal

        if self.chance > randint(0, 100) or not can_heal:
            return

        attacker.health += heal

        send_wcs_saytext_by_index(self._msg_a.format(heal=heal, name=victim.name), attacker.index)

        weapon = attacker.active_weapon
        if weapon and weapon.weapon_name.split("_")[-1] not in weapon_manager.projectiles:
            start_location = weapon.origin.copy()
            start_location.z += 40
            end_location = attacker.get_view_coordinates()

            self.beam.create(start_point=start_location, end_point=end_location)