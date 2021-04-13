"""

"""

## source.python imports

from filters.players import PlayerIter

## warcraft.package imports

from warcraft.registration import events
from warcraft.skill import Skill

## __all__ declaration

__all__ = ("TeamAddHealthSkill", )

## teamhealthskill declaration

class TeamAddHealthSkill(Skill):

    @property
    def base_health_addition(self):
        return self.level * 5
    

    @events('player_spawn')
    def _on_player_spawn_give_team_health(self, player, **kwargs):
        team = ['t', 'ct'][player.team-2]
        for ally in PlayerIter(is_filters=team):
            ally.health += self.base_health_addition