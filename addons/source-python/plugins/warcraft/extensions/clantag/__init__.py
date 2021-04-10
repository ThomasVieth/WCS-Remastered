"""

"""

## source.python imports

from core import GAME_NAME
from events import Event
from listeners import OnClientFullyConnect

## warcraft.package imports

from warcraft.events import Event as WCEvent
from warcraft.players import player_dict

## globals

clan_tag_prefix = "    " if GAME_NAME == "csgo" else ''

##

@OnClientFullyConnect
def _on_client_full_connect_setup_clantag(index):
    player = player_dict[index]
    player.clan_tag = clan_tag_prefix + player.race.name

@WCEvent("race_change")
def _on_player_race_change(player, old_race, new_race):
    player.clan_tag = clan_tag_prefix + new_race.name

@Event("player_spawn")
def _on_player_spawn(event_data):
    player = player_dict.from_userid(event_data["userid"])
    if not player.race.name.startswith(player.clan_tag) or player.clan_tag == '':
        player.clan_tag = clan_tag_prefix + player.race.name