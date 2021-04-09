"""

"""

## source.python imports

from menus import PagedMenu, PagedOption

## warcraft.package imports

from warcraft.database import Race as dbRace
from warcraft.race import Race

from .main import main_menu
from ..players import player_dict
from ..translations import changerace_menu_strings

## __all__ declaration

__all__ = ("change_race_menu", )

## callback declarations

def _on_change_race_build(menu, index):
    player = player_dict[index]
    menu.clear()
    menu.description = changerace_menu_strings['description']
    for race_cls in Race.sort_subclasses(key=lambda x: x.requirement_sort_key):
        if not race_cls.is_available(player):
            menu.append(
                PagedOption(
                    changerace_menu_strings['race_unavailable'].get_string(
                        name=race_cls.name,
                        requirement_string=race_cls.requirement_string
                    ),
                    race_cls,
                    highlight=False,
                    selectable=False
                )
            )
        else:
            race_data = player._dbinstance.races.filter(dbRace.name == race_cls.name).first()
            menu.append(
                PagedOption(
                    changerace_menu_strings['race_available'].get_string(
                        name=race_cls.name,
                        level=race_data.level if race_data else 0,
                        max_level=race_cls.max_level
                    ),
                    race_cls,
                    selectable=True
                )
            )

def _on_change_race_select(menu, index, choice):
    player = player_dict[index]
    race_cls = choice.value
    if race_cls.name != player.race.name and race_cls.is_available(player):
        player.change_race(race_cls)
    return

## menu declarations

change_race_menu = PagedMenu(
    title=changerace_menu_strings['header'],
    build_callback=_on_change_race_build,
    select_callback=_on_change_race_select,
    parent_menu=main_menu,
)