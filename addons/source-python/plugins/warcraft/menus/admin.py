"""

"""

## source.python imports

from menus import (
    ListMenu,
    ListOption,
    PagedMenu,
    PagedOption,
    Text
)

## warcraft.package imports

from ..players import player_dict
from ..translations import admin_menu_strings

## __all__ declaration

__all__ = ("admin_menu", )

## callback declarations

def _on_admin_players_build(menu, index):
    menu.clear()
    for player in player_dict.values():
        menu.append(PagedOption(player.name, player))

def _on_admin_players_select(menu, index, choice):
    player = choice.value
    player_menu.clear()
    player_menu.title = player.name + f" - ({player.userid})"
    player_menu.description = f"Playing {player.race.name} (LV {player.race.level})"
    player_menu.append(PagedOption("Give 1 Level", (player, 1)))
    player_menu.append(PagedOption("Give 5 Levels", (player, 5)))
    player_menu.append(PagedOption("Give 10 Levels", (player, 10)))
    player_menu.append(PagedOption("Take 1 Level", (player, -1)))
    player_menu.append(PagedOption("Take 5 Levels", (player, -5)))
    player_menu.append(PagedOption("Take 10 Levels", (player, -10)))
    return player_menu

def _on_admin_players_choose(menu, index, choice):
    player, amount = choice.value
    if amount > 0:
        player.race.level_up(amount)
    else:
        player.race.level_down(amount * -1)
    return menu

def _on_admin_menu_select(menu, index, choice):
    return _admin_menu_options[choice.value]

## menu declarations

admin_menu = PagedMenu(
    title=admin_menu_strings['header'],
    select_callback=_on_admin_menu_select,
    data=[
        PagedOption(admin_menu_strings['players'], 0)
    ]
)

admin_player_menu = PagedMenu(
    title=admin_menu_strings['players'],
    build_callback=_on_admin_players_build,
    select_callback=_on_admin_players_select,
    parent_menu=admin_menu,
)

player_menu = PagedMenu(
    select_callback=_on_admin_players_choose,
    parent_menu=admin_player_menu
)

_admin_menu_options = [
    admin_player_menu
]