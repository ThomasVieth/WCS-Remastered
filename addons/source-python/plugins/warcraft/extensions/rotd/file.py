"""

"""

## python imports

from datetime import datetime
from random import choice, choices

## source.python imports

from messages import SayText2
from paths import CUSTOM_DATA_PATH

## warcraft.package imports

from warcraft.race import Race

## extension imports

from .config import (
    rotd_count,
    should_remove_requirements
)

## __all__ declaration

__all__ = (
    "get_rotd_classes",
    "randomise_rotd_classes",
    "update_requirement_funcs",
    "write_to_rotd_file",
    "load_from_rotd_file",
)

## globals

rotd_classes = [] ## the race class
rotd_requirement_funcs = []
rotd_requirement_strings = []
rotd_date = None ## the date of the race class assignment

def get_rotd_classes():
    return rotd_classes

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
    fp.truncate(0)
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

    with rotd_file.open("a+") as rotd_fp:
        write_to_rotd_file(rotd_fp)