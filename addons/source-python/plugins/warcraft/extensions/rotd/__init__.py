"""

"""

## python imports

from datetime import datetime
from random import choice, choices

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

    rotd_count = manager.cvar(
        "warcraft_rotd_amount",
        2,
        "The amount of races to add as ROTD.\n",
        ConVarFlags.NOTIFY
    )

    should_remove_requirements = manager.cvar(
        "warcraft_rotd_remove_requirements",
        1,
        "Should the race lose its requirements to use? 1 = Yes, 0 = No\n",
        ConVarFlags.NOTIFY
    )

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

rotd_classes = [] ## the race class
rotd_requirement_funcs = []
rotd_requirement_strings = []
rotd_date = None ## the date of the race class assignment
rotd_strings = LangStrings("warcraft/extensions/rotd")
rotd_advert_message = SayText2(message=rotd_strings["advert"])
rotd_broadcast_message = SayText2(message=rotd_strings["broadcast"])
rotd_broadcast_plural_message = SayText2(message=rotd_strings["broadcast_plural"])
rotd_experience_up = SayText2(message=rotd_strings["experience_up"])

def get_rotd_classes():
    return rotd_classes

def get_rotd_names():
    return list(map(cls.name for cls in rotd_classes))

def randomise_rotd_classes():
    global rotd_date
    if len(rotd_requirement_funcs) > 0:
        for index, rotd_class in enumerate(rotd_classes):
            if rotd_requirement_funcs[index]:
                rotd_class.is_available = rotd_requirement_funcs[index]
                rotd_class.requirement_string = rotd_requirement_strings[index]

    races = Race.subclasses
    rotd_requirement_funcs.clear()
    rotd_classes.clear()
    rotd_classes.extend(choices(races, k=rotd_count.cvar.get_int()))
    rotd_date = datetime.today().strftime('%Y-%m-%d')

    update_requirement_funcs()

def update_requirement_funcs():
    should_update = should_remove_requirements.cvar.get_int()
    if should_update:
        for rotd_class in rotd_classes:
            rotd_requirement_funcs.append(rotd_class.is_available)
            rotd_requirement_strings.append(rotd_class.requirement_string)
            rotd_class.is_available = classmethod(lambda cls, player: True)
            rotd_class.requirement_string = "ROTD"

## file store

def write_to_rotd_file(fp):
    ## reset the pointer.
    fp.seek(0)

    ## grab current date.
    date = datetime.today().strftime('%Y-%m-%d')

    ## write the data.
    rotd_classnames = ','.join(cls.name for cls in rotd_classes)
    fp.write(f"{date} {rotd_classnames}")

def load_from_rotd_file(fp):
    ## reset the pointer.
    fp.seek(0)

    ## retrieve text.
    data = fp.read()

    ## gather date.
    date = data[:10]

    ## gather race classnames
    classnames = data[11:]

    return date, classnames.split(',')

rotd_data_dir = CUSTOM_DATA_PATH / "warcraft" / "rotd"
if not rotd_data_dir.exists():
    rotd_data_dir.mkdir()
rotd_file = rotd_data_dir / "rotd.txt"

with rotd_file.open("a+") as rotd_fp:
    rotd_fp.seek(0)
    data = rotd_fp.read()
    if not data:
        randomise_rotd_classes()
        write_to_rotd_file(rotd_fp)
    else:
        date, classnames = load_from_rotd_file(rotd_fp)
        rotd_date = date
        rotd_classes.extend(race_cls for race_cls in Race.subclasses if race_cls.name in classnames)
        update_requirement_funcs()

date = datetime.today().strftime('%Y-%m-%d')
if rotd_date != date:
    randomise_rotd_classes()

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
    if not attacker.race.__class__ in rotd_classes:
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
        if not player.race.__class__ in rotd_classes:
            return

        if player.team == winner:
            player.race.experience_up(experience_for_win.cvar.get_int())
            rotd_experience_up.send(player.index, amount=experience_for_win.cvar.get_int(),
                reason=win_reason)