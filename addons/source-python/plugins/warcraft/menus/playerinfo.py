"""

"""

## source.python imports

from menus import (
    ListMenu,
    PagedMenu,
    PagedOption,
    Text
)

## warcraft.package imports

from .main import main_menu
from ..players import player_dict
from ..translations import playerinfo_menu_strings

## __all__ declaration

__all__ = ("player_info_menu", )

## callback declarations

def _on_player_info_build(menu, index):
    menu.clear()
    for player in player_dict.values():
        menu.append(PagedOption(player.name, player))

def _on_player_info_select(menu, index, choice):
    player = choice.value
    player_info_menu = ListMenu(title=player.name + f" - ({player.userid})", parent_menu=menu)
    player_info_menu.append(Text(f"Playing {player.race.name}"))
    player_info_menu.append(Text(" "))
    for skill in player.race.skills:
        player_info_menu.append(Text("{} ({}/{})".format(skill.name, skill.level,
            skill.max_level)))
    return player_info_menu

## menu declarations

player_info_menu = PagedMenu(
    title=playerinfo_menu_strings['header'],
    build_callback=_on_player_info_build,
    select_callback=_on_player_info_select,
    parent_menu=main_menu,
)