"""

"""

## python imports

from datetime import datetime
from random import choice

## source.python imports

from events import Event
from listeners import OnLevelInit
from messages import SayText2
from translations.strings import LangStrings

## warcraft.package imports

from warcraft.experience import kill_reason, headshot_reason, win_reason
from warcraft.players import player_dict

## extension imports

from .config import (
    experience_for_kill,
    experience_for_headshot,
    experience_for_win
)
from .file import get_rotd_classes, randomise_rotd_classes, write_to_rotd_file

## globals

rotd_strings = LangStrings("warcraft/extensions/rotd")
rotd_advert_message = SayText2(message=rotd_strings["advert"])
rotd_broadcast_message = SayText2(message=rotd_strings["broadcast"])
rotd_broadcast_plural_message = SayText2(message=rotd_strings["broadcast_plural"])
rotd_experience_up = SayText2(message=rotd_strings["experience_up"])

## handlers

@OnLevelInit
def _on_level_init_check_day(map_name):
    date = datetime.today().strftime('%Y-%m-%d')
    if rotd_date != date:
        randomise_rotd_classes()

        with rotd_file.open("a+") as rotd_fp:
            write_to_rotd_file(rotd_fp)

## events

@Event("round_start")
def _on_round_start(event_data):
    rotd_classes = get_rotd_classes()
    kwargs = {}
    if len(rotd_classes) > 1:
        broadcast_message = rotd_broadcast_plural_message
        kwargs['names'] = ', '.join(cls.name for cls in rotd_classes)
    else:
        broadcast_message = rotd_broadcast_message
        kwargs['name'] = ','.join(cls.name for cls in rotd_classes)

    message = choice([broadcast_message, rotd_advert_message])
    if len(kwargs):
        message.send(**kwargs)
    else:
        message.send()

@Event("player_death")
def _on_player_kill(event_data):
    if event_data['userid'] == event_data['attacker'] or event_data['attacker'] == 0:
        return

    attacker = player_dict.from_userid(event_data['attacker'])
    if not attacker.race.__class__ in get_rotd_classes():
        return

    if not event_data["headshot"]:
        attacker.race.experience_up(experience_for_kill.cvar.get_int())
        rotd_experience_up.send(attacker.index, amount=experience_for_kill.cvar.get_int(),
            reason=kill_reason)
    else:
        attacker.race.experience_up(experience_for_headshot.cvar.get_int())
        rotd_experience_up.send(attacker.index, amount=experience_for_headshot.cvar.get_int(),
            reason=headshot_reason)

@Event("round_end")
def _on_round_end(event_data):
    winner = event_data['winner']
    for player in player_dict.values():
        if not player.race.__class__ in get_rotd_classes():
            return

        if player.team == winner:
            player.race.experience_up(experience_for_win.cvar.get_int())
            rotd_experience_up.send(player.index, amount=experience_for_win.cvar.get_int(),
                reason=win_reason)