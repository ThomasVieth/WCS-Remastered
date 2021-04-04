"""

"""

## source.python imports

from menus import PagedMenu, PagedOption

## warcraft.package imports

from ..translations import (
    changerace_menu_strings,
    home_menu_strings,
    shop_menu_strings,
    spendskills_menu_strings,
    raceinfo_menu_strings,
    playerinfo_menu_strings
)

## __all__ declaration

__all__ = ("main_menu", )

## callback declarations

_main_menu_selections = []

def _on_main_menu_select(menu, index, choice):
    if choice.value < len(_main_menu_selections):
        return _main_menu_selections[choice.value]

## menu declarations

main_menu = PagedMenu(
    title=home_menu_strings['header'],
    select_callback=_on_main_menu_select,
    data=[
        PagedOption(shop_menu_strings['header'], 0),
        PagedOption(spendskills_menu_strings['header'], 1),
        PagedOption(changerace_menu_strings['header'], 2),
        PagedOption(raceinfo_menu_strings['header'], 3),
        PagedOption(playerinfo_menu_strings['header'], 4),
    ]
)
