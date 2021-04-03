"""

"""

## source.python imports

from menus import PagedMenu, PagedOption

## warcraft.package imports

from .main import main_menu
from ..players import player_dict
from ..translations import spendskills_menu_strings

## __all__ declaration

__all__ = ("spend_skills_menu", )

## callback declarations

def _on_spend_skills_build(menu, index):
    player = player_dict[index]
    menu.clear()
    menu.description = spendskills_menu_strings['description'].get_string(
        amount=player.race.unused_points)
    for skill in player.race.skills:
        selectable = (skill.level < skill.max_level) and skill.is_available(player)
        menu.append(
            PagedOption(
                spendskills_menu_strings['skill'].get_string(name=skill.name,
                    level=skill.level, max_level=skill.max_level),
                skill,
                selectable=selectable
            )
        )
    menu.append(
        PagedOption(
            spendskills_menu_strings['reset'].get_string(),
            None,
            selectable=True
        )
    )

def _on_spend_skills_select(menu, index, choice):
    player = player_dict[index]
    skill = choice.value
    if not skill:
        ## Reset Skills
        for race_skill in player.race.skills:
            race_skill.level = race_skill.min_level
    elif player.race.unused_points and skill.level < skill.max_level:
        ## Increment Skill by 1
        skill.level_up(1)
    if player.race.unused_points > 0:
        ## Repeat menu...
        return menu

## menu declarations

spend_skills_menu = PagedMenu(
    title=spendskills_menu_strings['header'],
    build_callback=_on_spend_skills_build,
    select_callback=_on_spend_skills_select,
    parent_menu=main_menu,
)