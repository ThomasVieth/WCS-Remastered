"""

"""

## source.python imports

from translations.strings import LangStrings

## __all__ declaration

__all__ = (
    "admin_menu_strings",
    "categories_strings",
	"changerace_menu_strings",
	"experience_strings",
	"home_menu_strings",
	"playerinfo_menu_strings",
    "shop_menu_strings",
	"raceinfo_menu_strings",
	"spendskills_menu_strings"
)

## translation loading

experience_strings = LangStrings("warcraft/experience")

admin_menu_strings = LangStrings("warcraft/menus/admin")
categories_strings = LangStrings("warcraft/menus/categories")
changerace_menu_strings = LangStrings("warcraft/menus/changerace")
home_menu_strings = LangStrings("warcraft/menus/home")
playerinfo_menu_strings = LangStrings("warcraft/menus/playerinfo")
shop_menu_strings = LangStrings("warcraft/menus/shop")
spendskills_menu_strings = LangStrings("warcraft/menus/spendskills")
raceinfo_menu_strings = LangStrings("warcraft/menus/raceinfo")