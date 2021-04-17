"""

"""

## python imports

from random import randint

## source.python imports

from engines.sound import StreamSound
from engines.trace import engine_trace
from engines.trace import ContentMasks
from engines.trace import GameTrace
from engines.trace import Ray
from engines.trace import TraceFilterSimple
from filters.players import PlayerIter
from messages import Shake
from paths import CUSTOM_DATA_PATH

## warcraft.package imports

from warcraft.commands.messages import send_wcs_saytext_by_index
from warcraft.race import Race
from warcraft.registration import events, clientcommands
from warcraft.skill import Skill
from warcraft.utility import classproperty, CooldownDict

## warcraft.skills imports

from ..skills.self_set_invisibility import InvisibilitySkill as _InvisibilitySkill
from ..skills.enemy_remove_invisibility import RemoveInvisibilitySkill
from ..skills.team_add_health import TeamAddHealthSkill
from ..skills.enemy_shake import ShakeSkill
from ..skills.self_teleport import TeleportSkill

## __all__ declaration

__all__ = ("HumanAlliance", )

## HumanAlliance declaration

class HumanAlliance(Race):
    image = "https://liquipedia.net/commons/images/thumb/2/2c/Humanrace.png/240px-Humanrace.png"

    @classproperty
    def description(cls):
        return 'Recoded Human Alliance. (Kryptonite)'

    @classproperty
    def max_level(cls):
        return 99

    @classproperty
    def requirement_sort_key(cls):
        return 2

@HumanAlliance.add_skill
class Invisibility(_InvisibilitySkill, RemoveInvisibilitySkill):

    @classproperty
    def description(cls):
        return "Gain control of Invisibility by the Kirin Tor."

    @classproperty
    def max_level(cls):
        return 8

@HumanAlliance.add_skill
class CauterizeWounds(TeamAddHealthSkill):

    @classproperty
    def description(cls):
        return 'You and your allies gain increased health.'

    @classproperty
    def max_level(cls):
        return 8


@HumanAlliance.add_skill
class FrostBomb(ShakeSkill):

    @classproperty
    def description(cls):
        return 'Upon damaging an enemy, shake them, 20-28% chance.'

    @classproperty
    def max_level(cls):
        return 8

@HumanAlliance.add_skill
class Teleport(TeleportSkill):
    
    @classproperty
    def description(cls):
        return 'Teleport a distance infront of yourself, if not obstructed. Ultimate.'

    @classmethod
    def is_available(cls, player):
        return player.race.level > 8

    @classproperty
    def max_level(cls):
        return 8