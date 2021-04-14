"""

"""

## python imports

from random import randint

## source.python imports

from events.manager import game_event_manager
from players.entity import Player
from events import Event

## warcraft.package imports

from warcraft.events import Event

##

html = '''
<head>
    <p font-size=30px><b><font color="#FF0000" size="20">Changing to {race}</font></b></p>
</head
<body>
    <img background-color="transparent" src="{url}"></img>
</body>
'''

@Event('race_change')
def _on_race_change(player, old_race, new_race):
    url = ""
    if hasattr(new_race, 'image'):
        url = new_race.image
    send_win_message(
        message=html.format(url=url, race=new_race.name),
        recipients=(player.index,)
    )
    duration = 4
    player.delay(duration,send_win_message, ("", (player.index,)))
    
def send_win_message(message='', recipients=None):
    """Creates and sends the 'cs_win_panel_round' event.

    Args:
        message (str): Message to send, supports some HTML tags.
        recipients: List/tuple of player indexes that should receive the
            message.
    """
    event = game_event_manager.create_event('cs_win_panel_round')
    event.set_string('funfact_token', message)

    # Should the message be sent to everyone on the server?
    if recipients is None:
        game_event_manager.fire_event(event)

    # Or have the recipients been specified?
    else:
        for index in recipients:
            try:
                # Try to get a Player instance.
                Player(index).base_client.fire_game_event(event)
            except ValueError:
                continue

        # When firing events to players/clients directly, we need to free it
        # once we're done with it.
        game_event_manager.free_event(event)