"""

"""

## source.python imports

from cvars.flags import ConVarFlags
from config.manager import ConfigManager

## __all__ declaration

__all__ = (
    "rotd_count",
    "should_remove_requirements",
    "experience_for_kill",
    "experience_for_headshot",
    "experience_for_win",
)

## config

with ConfigManager("warcraft/rotd") as manager:
    ## Add the package header.
    manager.header = "Warcraft Source - ROTD"

    rotd_count = manager.cvar(
        "warcraft_rotd_amount",
        2,
        "The amount of races to add as ROTD.\n",
        ConVarFlags.NOTIFY
    )

    should_remove_requirements = manager.cvar(
        "warcraft_rotd_remove_requirements",
        1,
        "Should the race lose its requirements to use? 1 = Yes, 0 = No\n",
        ConVarFlags.NOTIFY
    )

    experience_for_kill = manager.cvar(
        "warcraft_rotd_experience_for_kill",
        50,
        "The extra experience gained for killing another player.\n",
        ConVarFlags.NOTIFY
    )

    experience_for_headshot =  manager.cvar(
        "warcraft_rotd_experience_for_headshot",
        80,
        "The extra experience gained for killing with a headshot.",
        ConVarFlags.NOTIFY
    )

    experience_for_win =  manager.cvar(
        "warcraft_rotd_experience_for_win",
        60,
        "The extra experience gained for winning a round.",
        ConVarFlags.NOTIFY
    )