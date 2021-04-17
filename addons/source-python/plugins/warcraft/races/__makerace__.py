## -- CONFIG --

racename = "Terminator"
level_req = 0

skills = "Laser Bullets|Metallic Skin|Organic Skin|Short Curt"
skill_descriptions = "You gun coming in future and bullets are laser(Extra damage)|Regenation some you healt back.|You skin change a enemy skin.|When you die you body explosion."
skill_cfg = "player_attack|player_spawn|player_spawn|player_death"
skill_needed = "0|0|0|8"

## -- DO NOT EDIT --

from os.path import abspath, dirname, join

this_dir = dirname(abspath(__file__))

def name_to_formatted_name(name):
    return ''.join(name.split(' '))

filename = ''.join(racename.lower().split(' ')) + '.py'

race_path = join(this_dir, filename)

race_text = """
\"\"\"

\"\"\"

## python imports

from random import randint

## source.python imports

## warcraft.package imports

from warcraft.commands.messages import send_wcs_saytext_by_index
from warcraft.players import player_dict
from warcraft.race import Race
from warcraft.registration import events, clientcommands
from warcraft.skill import Skill
from warcraft.utility import classproperty, CooldownDict

## __all__ declaration

__all__ = ("{race_name}", )

## {race_name} declaration

class {race_name}(Race):

    @classproperty
    def description(cls):
        return ''

    @classproperty
    def max_level(cls):
        return 99

    @classproperty
    def requirement_sort_key(cls):
        return 1
"""

skill_text = """
@{race_name}.add_skill
class {skill_name}(Skill):
    
    @classproperty
    def description(cls):
        return '{skill_descr}'

    @classproperty
    def max_level(cls):
        return 4
"""

available_text = """
    @classmethod
    def is_available(cls, player):
        return player.{is_race}level > {level}
"""

event_text = """
    @events('{event_name}')
    def _on_player_{event_partial}(self, player, **kwargs):
        ## Code goes here...
"""

with open(race_path, "w+") as race_file_pointer:
    print(f"Writing new race file: {filename}")
    race_name = name_to_formatted_name(racename)
    race_file_pointer.write(
        race_text.format(race_name=race_name)
    )
    race_file_pointer.write(
        available_text.format(
            is_race='total_',
            level=level_req
        )
    )
    descriptions = skill_descriptions.split('|')
    cfgs = skill_cfg.split('|')
    needs = skill_needed.split('|')
    for index, skill in enumerate(skills.split('|')):
        race_file_pointer.write(
            skill_text.format(
                race_name=race_name,
                skill_name=name_to_formatted_name(skill),
                skill_descr=descriptions[index]
            )
        )
        if index < len(needs) and len(needs[index]) != 0:
            race_file_pointer.write(
                available_text.format(
                    is_race='race.',
                    level=needs[index]
                )
            )
        if index < len(cfgs) and len(cfgs[index]) != 0:
            race_file_pointer.write(
                event_text.format(
                    event_name=cfgs[index],
                    event_partial=cfgs[index].split('_')[-1]
                )
            )