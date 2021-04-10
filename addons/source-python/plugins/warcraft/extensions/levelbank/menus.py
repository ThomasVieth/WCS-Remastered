"""

"""

## source.python imports

from menus import PagedMenu, PagedOption
from translations.strings import LangStrings

## warcraft.package imports

from warcraft.database import session
from warcraft.players import player_dict

## extension imports

from .config import levelbank_menu_values
from .database import Levelbank

## __all__ declaration

__all__ = (
    "levelbank_menu",
    "levelbank_strings",
)

## globals

levelbank_strings = LangStrings("warcraft/extensions/levelbank")

## build/select declarations

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
                highlight=player_levelbank.levels > option,
                selectable=player_levelbank.levels > option
            )
        )

def _on_levelbank_menu_select(menu, index, choice):
    player = player_dict[index]
    player_levelbank, amount = choice.value
    player.race.level_up(amount)
    player_levelbank.levels -= amount

## menu declarations

levelbank_menu = PagedMenu(
    title=levelbank_strings['header'],
    select_callback=_on_levelbank_menu_select,
    build_callback=_on_levelbank_menu_build
)