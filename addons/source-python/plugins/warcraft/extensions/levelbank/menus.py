"""

"""

## source.python imports

from menus import PagedMenu, PagedOption
from translations.strings import LangStrings

## warcraft.package imports

from warcraft.commands.messages import send_wcs_saytext_by_index
from warcraft.database import session
from warcraft.menus.admin import admin_menu, _admin_menu_options
from warcraft.players import player_dict

## extension imports

from .config import levelbank_menu_values, levelbank_admin_menu_values
from .database import Levelbank

## __all__ declaration

__all__ = (
    "levelbank_menu",
    "levelbank_strings",
)

## globals

levelbank_strings = LangStrings("warcraft/extensions/levelbank")

## build/select declarations

def _on_levelbank_players_menu_build(menu, index):
    menu.clear()
    for player in player_dict.values():
        menu.append(PagedOption(player.name, player))

def _on_levelbank_players_menu_select(menu, index, choice):
    player = choice.value
    player_levelbank = session.query(Levelbank).filter(Levelbank.parent == player._dbinstance).first()
    levelbank_player_menu.clear()
    levelbank_player_menu.title = player.name + f" - ({player.userid})"
    levelbank_player_menu.description = f"Bank Levels: {player_levelbank.levels}"
    options_string = levelbank_admin_menu_values.cvar.get_string()
    options = list(map(lambda x: int(x.strip(' ')), options_string.split(',')))
    for option in options:
        levelbank_player_menu.append(
            PagedOption(
                f"Give {option} Levels",
                (player_levelbank, option)
            )
        )
    return levelbank_player_menu

def _on_levelbank_players_choose(menu, index, choice):
    player_levelbank, amount = choice.value
    player_levelbank.levels += amount
    session.commit()

    send_wcs_saytext_by_index(f"{{PALE_GREEN}}You have given the user {amount} levels.", index)

    menu.description = f"Bank Levels: {player_levelbank.levels}"
    return menu

def _on_levelbank_menu_build(menu, index):
    player = player_dict[index]
    player_levelbank = session.query(Levelbank).filter(Levelbank.parent == player._dbinstance).first()
    menu.clear()
    menu.description = levelbank_strings["description"].get_string(levels=player_levelbank.levels)
    options_string = levelbank_menu_values.cvar.get_string()
    options = list(map(lambda x: int(x.strip(' ')), options_string.split(',')))
    for option in options:
        menu.append(
            PagedOption(
                f"{option} Levels",
                (player_levelbank, option),
                highlight=player_levelbank.levels >= option,
                selectable=player_levelbank.levels >= option
            )
        )

def _on_levelbank_menu_select(menu, index, choice):
    player = player_dict[index]
    player_levelbank, amount = choice.value
    player.race.level_up(amount)
    player_levelbank.levels -= amount
    return menu

## menu declarations

levelbank_menu = PagedMenu(
    title=levelbank_strings['header'],
    select_callback=_on_levelbank_menu_select,
    build_callback=_on_levelbank_menu_build
)

levelbank_admin_menu = PagedMenu(
    title=levelbank_strings['header'],
    select_callback=_on_levelbank_players_menu_select,
    build_callback=_on_levelbank_players_menu_build,
    parent_menu=admin_menu
)

levelbank_player_menu = PagedMenu(
    select_callback=_on_levelbank_players_choose,
    parent_menu=levelbank_admin_menu
)

_admin_menu_options.append(levelbank_admin_menu)
admin_menu.append(PagedOption(levelbank_strings['header'], 1))