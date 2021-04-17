"""

"""

## python imports

from math import atan2, degrees

## warcraft.package imports

from warcraft.skill import Skill

## __all__ declaration

__all__ = ("IsInFOVSkill", )

## isinfovskill declaration

class IsInFOVSkill(Skill):

    @property
    def fov(self):
        return 100

    def is_in_fov(self, player, target):
        angle_radians = atan2(target.origin.y - player.origin.y, target.origin.x - player.origin.x)
        angle_degrees = degrees(angle_radians)
        angle_diff = player.view_angle.y - angle_degrees
        if angle_diff > 180:
            angle_diff -= 360

        if angle_diff < (self.fov / 2) and angle_diff > -(self.fov / 2):
            return True
        return False