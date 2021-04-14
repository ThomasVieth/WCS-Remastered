"""

"""

## warcraft.package imports

from warcraft.skill import Skill

## __all__ declaration

__all__ = ("IsInFOVSkill", )

## isinfovskill declaration

class IsInFOVSkill(Skill):

    @property
    def fov(self):
        return 100

    def is_in_fov(self, origin, target):
        angle_radians = atan2(v2.y - v1.y, v2.x - v1.x)
        angle_degrees = degrees(angle_radians)
        angle_diff = attacker.view_angle.y - angle_degrees
        if angle_diff > 180:
            angle_diff -= 360

        if angle_diff < (self.fov / 2) and angle_diff > -(self.fov / 2):
            return True
        return False