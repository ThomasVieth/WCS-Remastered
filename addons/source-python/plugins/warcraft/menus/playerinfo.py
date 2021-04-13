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

from .main import main_menu
from ..players import player_dict
from ..translations import playerinfo_menu_strings

## __all__ declaration

__all__ = ("player_info_menu", )

## globals

player_info_dict = dict()

def speed_to_percent(speed):
    return speed * 100

def gravity_to_percent(gravity):
    return gravity * 100

def color_to_percent(color):
    alpha = color.a
    return (alpha / 255) * 100

def health_to_percent(health):
    return health

stats_attributes = [
    ("Health", "health", health_to_percent),
    ("Speed", "speed", speed_to_percent),
    ("Gravity", "gravity", gravity_to_percent),
    ("Visibility", "color", color_to_percent)
]

## callback declarations

def _on_stats_build(menu, index):
    player = player_info_dict[index]
    menu.clear()
    menu.title = player.name + f" - ({player.userid})"
    for entry, attr, format_func in stats_attributes:
        percentage = format_func(getattr(player, attr))
        menu.append(Text("{} - {:.1f}%".format(entry, percentage)))

def _on_info_build(menu, index):
    player = player_info_dict[index]
    menu.clear()
    menu.title = player.name + f" - ({player.userid})"
    menu.append(PagedOption("Goto Attributes", 1))
    menu.append(Text(" "))
    menu.append(Text(f"Playing {player.race.name}"))
    menu.append(Text(" "))
    for skill in player.race.skills:
        menu.append(Text("{} ({}/{})".format(skill.name, skill.level,
            skill.max_level)))

def _on_info_select(menu, index, choice):
    if choice.value == 1:
        return stats_menu

def _on_player_info_build(menu, index):
    menu.clear()
    for player in player_dict.values():
        menu.append(PagedOption(player.name, player))

def _on_player_info_select(menu, index, choice):
    player = choice.value
    player_info_dict[index] = player
    return info_menu

## menu declarations

player_info_menu = PagedMenu(
    title=playerinfo_menu_strings['header'],
    build_callback=_on_player_info_build,
    select_callback=_on_player_info_select,
    parent_menu=main_menu,
)

info_menu = ListMenu(
    build_callback=_on_info_build,
    select_callback=_on_info_select,
    parent_menu=player_info_menu,
)

stats_menu = PagedMenu(
    build_callback=_on_stats_build,
    parent_menu=info_menu,
)