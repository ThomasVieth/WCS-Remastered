"""

"""

## python imports

from datetime import datetime
from random import choice

## source.python imports

from cvars.flags import ConVarFlags
from config.manager import ConfigManager
from events import Event
from listeners import OnLevelInit
from messages import SayText2
from paths import CUSTOM_DATA_PATH
from translations.strings import LangStrings

## warcraft.package imports

from warcraft.experience import kill_reason, headshot_reason, win_reason
from warcraft.players import player_dict
from warcraft.race import Race

## __all__ declaration

__all__ = (
    "get_rotd_class",
    "get_rotd_name",
)

## config

with ConfigManager("warcraft/rotd") as manager:
    ## Add the package header.
    manager.header = "Warcraft Source - ROTD"

    experience_for_kill = manager.cvar(
        "warcraft_rotd_experience_for_kill",
        50,
        "The extra experience gained for killing another player.\n",
        ConVarFlags.NOTIFY
    )

    experience_for_headshot =  manager.cvar(
        "warcraft_rotd_experience_for_headshot",
        80,
        "The extra experience gained for killing with a headshot.",
        ConVarFlags.NOTIFY
    )

    experience_for_win =  manager.cvar(
        "warcraft_rotd_experience_for_win",
        60,
        "The extra experience gained for winning a round.",
        ConVarFlags.NOTIFY
    )

## globals

rotd_class = None ## the race class
rotd_date = None ## the date of the race class assignment
rotd_strings = LangStrings("warcraft/extensions/rotd")
rotd_broadcast_message = SayText2(message=rotd_strings["broadcast"])
rotd_experience_up = SayText2(message=rotd_strings["experience_up"])

def get_rotd_class():
    return rotd_class

def get_rotd_name():
    return rotd_class.name

def randomise_rotd_class():
    global rotd_class, rotd_date
    races = Race.subclasses
    rotd_class = choice(races)
    rotd_date = datetime.today().strftime('%Y-%m-%d')

## file store

def write_to_rotd_file(fp):
    ## reset the pointer.
    fp.seek(0)

    ## grab current date.
    date = datetime.today().strftime('%Y-%m-%d')

    ## write the data.
    fp.write(f"{date} {rotd_class.__name__}")

def load_from_rotd_file(fp):
    ## reset the pointer.
    fp.seek(0)

    ## retrieve text.
    data = fp.read()

    ## gather date.
    date = data[:10]

    ## gather race classname
    classname = data[11:]

    return date, classname

rotd_data_dir = CUSTOM_DATA_PATH / "warcraft" / "rotd"
if not rotd_data_dir.exists():
    rotd_data_dir.mkdir()
rotd_file = rotd_data_dir / "rotd.txt"

with rotd_file.open("a+") as rotd_fp:
    data = rotd_fp.read()
    if not data:
        randomise_rotd_class()
    else:
        load_from_rotd_file(fp)

date = datetime.today().strftime('%Y-%m-%d')
if rotd_date != date:
    randomise_rotd_class()

## handlers

@OnLevelInit
def _on_level_init_check_day(map_name):
    date = datetime.today().strftime('%Y-%m-%d')
    if rotd_date != date:
        randomise_rotd_class()

        with rotd_file.open("a+") as rotd_fp:
            write_to_rotd_file(rotd_fp)

## events

@Event("round_start")
def _on_round_start(event_data):
    rotd_broadcast_message.send(name=rotd_class.name)

@Event("player_death")
def _on_player_kill(event_data):
    if event_data['userid'] == event_data['attacker'] or event_data['attacker'] == 0:
        return

    attacker = player_dict.from_userid(event_data['attacker'])
    if not attacker.race.__class__ == rotd_class:
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
        if not player.race.__class__ == rotd_class:
            return

        if player.team == winner:
            player.race.experience_up(experience_for_win.cvar.get_int())
            rotd_experience_up.send(player.index, amount=experience_for_win.cvar.get_int(),
                reason=win_reason)