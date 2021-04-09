"""

"""

## python imports

from collections import defaultdict
from random import choice

## source.python imports

from commands import CommandReturn
from commands.client import ClientCommand
from commands.say import SayCommand
from engines.sound import StreamSound
from entities.entity import Entity
from entities.helpers import index_from_pointer
from events import Event
from messages import SayText2, ShowMenu

## warcraft.package imports

from warcraft.config import race_bot_options
from warcraft.database import session
from warcraft.events import Event as WCEvent
from warcraft.race import Race

## import items first, to load ini data.
from .items import *
##load_ini_items()

## import races first, to load ini data.
from .races import *
load_ini_races()

## import after to construct prior to race loading.
from .calling import *
from .commands import send_wcs_saytext_by_index
from .effects import attach_entity_to_player
from .experience import *
from .extensions import *
from .menus import *
from .players import player_dict
from .translations import admin_strings

## constants

ADMINS = ["STEAM_1:0:120220385"]

## saving data

def unload():
    """
    On unload, ensure that the database is updated with all cached data.
    """
    for player in player_dict.values():
        player.update_user_data()
        player.update_race_data()
    session.commit()

@Event("round_end")
def _save_round_end(game_event):
    for player in player_dict.values():
        player.update_race_data()
    session.commit()

## handle say commands

admin_failed_message = SayText2(message=admin_strings["failed"])

@ClientCommand("showxp")
@SayCommand("showxp")
def _showxp_say_command(command, index, team_only=None):
    player = player_dict[index]
    show_level_message.send(index,
        racename=player.race.name,
        level=player.race.level,
        xp=player.race.experience,
        req_xp=player.race.required_experience
    )
    return CommandReturn.BLOCK

@ClientCommand("playerinfo")
@SayCommand("playerinfo")
def _player_info_say_command(command, index, team_only=None):
    player_info_menu.send(index)
    return CommandReturn.BLOCK

@ClientCommand("shopmenu")
@SayCommand("shopmenu")
def _shop_menu_say_command(command, index, team_only=None):
    shop_menu.send(index)
    return CommandReturn.BLOCK

@ClientCommand("raceinfo")
@SayCommand("raceinfo")
def _race_info_say_command(command, index, team_only=None):
    race_info_menu.send(index)
    return CommandReturn.BLOCK

@ClientCommand("spendskills")
@SayCommand("spendskills")
def _spend_skills_say_command(command, index, team_only=None):
    spend_skills_menu.send(index)
    return CommandReturn.BLOCK

@ClientCommand("changerace")
@SayCommand("changerace")
def _change_race_say_command(command, index, team_only=None):
    change_race_menu.send(index)
    return CommandReturn.BLOCK

@ClientCommand(["warcraft", "wcs"])
@SayCommand(["warcraft", "wcs"])
def _main_menu_say_command(command, index, team_only=None):
    main_menu.send(index)
    return CommandReturn.BLOCK

@ClientCommand("wcsadmin")
@SayCommand("wcsadmin")
def _admin_menu_say_command(command, index, team_only=None):
    player = player_dict[index]
    if player.steamid in ADMINS:
        admin_menu.send(index)
    else:
        admin_failed_message.send(index)
    return CommandReturn.BLOCK

## handle level up

levelup_sound = StreamSound('source-python/warcraft/levelup.mp3', download=True)

def find_upgradable_skill(race):
    """
    Chooses a single available upgradable skill. Used for auto-upgrading bot skills.

    :param race: The Race object to scan through.
    :type race: Race

    :return: A single Skill object.
    :rtype: Skill
    """
    _skills = [skill for skill in race.skills if not skill.is_max_level]
    return choice(_skills) if len(_skills) > 0 else None

@WCEvent("race_level_up")
def _spend_skills_on_level_up(player, race, amount):
    """
    Callback for the race_level_up event to handle menu sending,
    bot auto-upgrades and level up effects.
    """
    if (race.level > sum(skill.max_level for skill in race.skills) or
        race.level > race.max_level):
        return
    
    spend_skills_menu.send(player.index)

    if player.steamid == 'BOT':
        while race.unused_points > 0:
            skill = find_upgradable_skill(race)
            if skill:
                skill.level_up(1)

    levelup_sound.origin = player.origin
    levelup_sound.play(player.index)
    pointer = player.give_named_item('env_smokestack', 0, None, False)
    entity = Entity(index_from_pointer(pointer))

    for output in ('basespread 10', 'spreadspeed 60', 'initial 0', 'speed 105',
        'rate 50', 'startsize 7', 'endsize 2', 'twist 0', 'jetlength 100',
        'angles 0 0 0', 'rendermode 18', 'renderamt 100',
        'rendercolor 255 255 3', 'SmokeMaterial effects/yellowflare.vmt'):
        entity.add_output(output)

    entity.turn_on()
    attach_entity_to_player(player, entity)
    entity.delay(0.5, entity.turn_off)

## handle bot race changes

_bot_death_count = defaultdict(int)

def split_race_list_and_choose(string):
    """
    Split up the bot available race list and randomly choose one.

    :param string: The string of available races. Split by a comma.
    :type string: str

    :return: A single Race subclass.
    :rtype: Race
    """
    split_string = string.split(',')
    race_classes = list(map(lambda x: Race.find_race(x.lstrip(' ')), split_string))
    ## Remove any false race classes. Todo: Fix None appearing in list.
    while None in race_classes:
        race_classes.remove(None)
    return choice(race_classes)

@Event("player_death")
def _on_death_change_race(event_data):
    """
    Callback to handle bots change of race during gameplay.
    """
    userid = event_data["userid"]
    player = player_dict.from_userid(userid)
    
    if player.steamid == 'BOT':
        deaths = _bot_death_count[userid]
        if deaths + 1 > 10:
            race_cls = split_race_list_and_choose(race_bot_options.cvar.get_string())
            player.change_race(race_cls)
            _bot_death_count[userid] = 0
        else:
            _bot_death_count[userid] = deaths + 1