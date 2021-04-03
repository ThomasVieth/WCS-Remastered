"""

"""

## warcraft.package imports

from . import main
from .admin import admin_menu
from .changerace import change_race_menu
from .main import main_menu
from .playerinfo import player_info_menu
from .raceinfo import race_info_menu
from .spendskills import spend_skills_menu

## __all__ declaration

__all__ = (
    "admin_menu",
    "change_race_menu",
    "main_menu",
    "player_info_menu",
    "race_info_menu",
    "spend_skills_menu"
)

## main menu setup

main._main_menu_selections = [
    change_race_menu,
    spend_skills_menu,
    race_info_menu,
    player_info_menu
]