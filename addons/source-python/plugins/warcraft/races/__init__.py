"""

"""

## python imports

from configobj import ConfigObj
from glob import glob
from os.path import dirname, basename, isfile

## source.python imports

from engines.server import insert_command_string
from paths import CUSTOM_DATA_PATH
from messages import SayText2

## warcraft.package imports

from warcraft.race import Race
from warcraft.skill import Skill
from warcraft.utility import classproperty

## __all__ declaration

modules = glob(dirname(__file__) + '/*')
__all__ = ["ini_races", "load_ini_races"]

for f in modules:
    f_basename = basename(f)
    if isfile(f):
        __all__.append(f_basename[:-3])
    elif f_basename != "races":
        __all__.append(f_basename)

## generate functions

def name_to_classname(name):
    return "INI_" + name.replace(" ", "").replace("-", "_")

def generate_is_available(required_level):
    def _func(cls, player):
        return player.total_level >= required_level
    return _func

def generate_description(description):
    def _func(cls):
        return description
    return _func

def generate_requirement_string(required_level):
    def _func(cls):
        return f"TL {required_level}"
    return _func

def generate_requirement_sort_key(required_level):
    def _func(cls):
        return required_level
    return _func

## load ini races

with open(CUSTOM_DATA_PATH / "warcraft" / "events.txt", "r") as fo:
    _event_options = list(
        filter(lambda x: not x.startswith(' '),
            map(lambda x: x.rstrip("\n"),
                fo.readlines()
            )
        )
    )

def make_skill_callback(fire_targets, fire_object):
    targets = fire_targets.split(",")
    events = list()
    clientcommands = list()
    for target in targets:
        fire_type, name = target.split(':')
        if fire_type == "clientcommand":
            clientcommands.append(name)
        elif fire_type == "event" and not name in _event_options:
            raise ValueError(f"Cannot register skill callback for event ({name}). Please read the docs.")
        elif fire_type == "event":
            events.append(name)
        else:
            raise ValueError(f"Unsupported fire_type supplied in INI race ({fire_type}).")

    def _func(self, *args, **kwargs):
        if self.level == 0:
            return

        if _func._chance and _func._chance > randint(0, 101):
            return

        kwargs["value"] = self.values[self.level - 1]
        for command in _func._commands:
            insert_command_string(command.format(**kwargs))

    _func._chance = fire_object.get("chance", None)
    _func._commands = fire_object["cmd"].split(";")
    _func._events = events
    _func._clientcommands = clientcommands
    return _func

def make_skill_class(skillname, skill_object):
    ## Gather information.
    required_level = skill_object.as_int("required_level")
    maximum_level = skill_object.as_int("maximum_level")
    description = skill_object["description"]
    values = skill_object["values"]

    keyvalues = {
        "max_level": maximum_level,
        "is_available":
            classmethod(generate_is_available(required_level)),
        "description":
            classproperty(generate_description(description)),
        "name":
            classproperty(lambda cls: skillname),
        "values": values
    }
    for num, fire_targets in enumerate(skill_object.sections):
        skill_method = make_skill_callback(fire_targets, skill_object[fire_targets])
        ini_funcs.append(skill_method)
        keyvalues[f"func{num}"] = skill_method

    ## Construct the skill class.
    new_skill_class = type(
        name_to_classname(skillname), ## Classname.
        (Skill, ), ## Skill class to inherit from.
        keyvalues
    )

    ini_skills.append(new_skill_class)
    return new_skill_class

def make_race_class(racename, race_object):
    ## Gather information.
    required_level = race_object.as_int("required_level")
    maximum_level = race_object.as_int("maximum_level")
    author = race_object["author"]
    description = race_object["description"]

    ## Construct the race class.
    new_race_class = type(
        name_to_classname(racename), ## Classname.
        (Race, ), ## Race class to inherit from.
        {
            "max_level": maximum_level,
            "is_available":
                classmethod(generate_is_available(required_level)),
            "description":
                classproperty(generate_description(description)),
            "requirement_string":
                classproperty(generate_requirement_string(required_level)),
            "requirement_sort_key":
                classproperty(generate_requirement_sort_key(required_level)),
            "name":
                classproperty(lambda cls: racename)
        }
    )

    for skillname in race_object.sections:
        new_skill_class = make_skill_class(skillname, race_object[skillname])
        new_race_class.add_skill(new_skill_class)

    ini_races.append(new_race_class)
    return new_race_class

def create_race_classes(races_object):
    for racename, race_object in races_object.items():
        race_class = make_race_class(racename, race_object)

ini_races = list()
ini_skills = list()
ini_funcs = list()

def load_ini_races():
    create_race_classes(
        ConfigObj(CUSTOM_DATA_PATH / "warcraft" / "races.ini")
    )