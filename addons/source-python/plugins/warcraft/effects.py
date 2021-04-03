"""

"""

## python imports

from collections import defaultdict

## source.python imports

from entities.helpers import pointer_from_index
from events import Event

## warcraft.package imports

from .players import player_dict

## __all__ declaration

__all__ = ("attach_entity_to_player", "attached_entities", )

##

attached_entities = defaultdict(list)

def attach_entity_to_player(player, entity):
    """
    Attaches an entity directly to the player. This entity is then
        managed inside the `attached_entities` list for the player.
    """
    entity.set_parent(player.pointer, -1)
    attached_entities[player.userid].append(entity)

@Event("player_death")
def _detach_on_death(event_data):
    """
    Callback for automatically removing the attached entities for
        a player upon death.
    """
    userid = event_data["userid"]
    attached_entities[userid].clear()