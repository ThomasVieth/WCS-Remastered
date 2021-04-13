"""

"""

## source.python imports

from effects.base import TempEntity
from filters.players import PlayerIter

## warcraft.package imports

from warcraft.commands.messages import send_wcs_saytext_by_index
from warcraft.registration import events
from warcraft.skill import Skill

## __all__ declaration

__all__ = ("ExplosionSkill", )

## explosionSkill declaration

class ExplosionSkill(Skill):
    _msg_a = '{{RED}}Exploded {{PALE_GREEN}}damaging {{RED}}{name}{{PALE_GREEN}}!'

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.explosion = TempEntity('Explosion',
            magnitude=100, scale=40, radius=self.range)

    @property
    def range(self):
        return 300 + 25*self.level

    @property
    def magnitude(self):
        return 50 + 5*self.level

    @events('player_death')
    def player_death(self, player, **eargs):
        if self.level == 0:
            return

        team = ['ct', 't'][player.team-2]

        for target in PlayerIter(is_filters=team):
            if player.origin.get_distance(target.origin) <= self.range:
                target.take_damage(self.magnitude, attacker_index=player.index, skip_hooks=True)
                send_wcs_saytext_by_index(self._msg_a.format(name=target.name), player.index)

        self.explosion.create(origin=player.origin)