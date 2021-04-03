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

from warcraft.race import Race

from .main import main_menu
from ..translations import raceinfo_menu_strings

## __all__ declaration

__all__ = ("race_info_menu", )

## callback declarations

def _on_race_info_build(menu, index):
    menu.clear()
    for race_cls in Race.sort_subclasses(key=lambda x: x.requirement_sort_key):
        menu.append(PagedOption(raceinfo_menu_strings['race'].get_string(name=race_cls.name,
            requirement=race_cls.requirement_string), race_cls, selectable=True))

def _on_race_info_select(menu, index, choice):
    race_cls = choice.value
    race_info_menu = ListMenu(title=race_cls.name, description=race_cls.description,
        parent_menu=menu)
    for skill_cls in race_cls._skills:
        race_info_menu.append(ListOption(skill_cls.name))
        race_info_menu.append(Text(skill_cls.description))
    return race_info_menu

## menu declarations

race_info_menu = PagedMenu(
    title=raceinfo_menu_strings['header'],
    build_callback=_on_race_info_build,
    select_callback=_on_race_info_select,
    parent_menu=main_menu,
)