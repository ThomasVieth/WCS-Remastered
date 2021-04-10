"""

"""

## source.python imports

from config.manager import ConfigManager
from cvars.flags import ConVarFlags


## __all__ declaration

__all__ = (
    "levelbank_start_amount",
    "levelbank_menu_values",
)

## config

with ConfigManager("warcraft/levelbank") as manager:
    ## Add the package header.
    manager.header = "Warcraft Source - Level Bank"

    levelbank_start_amount = manager.cvar(
        "warcraft_levelbank_start_amount",
        100,
        "The amount of levels a user should start with.\n",
        ConVarFlags.NOTIFY
    )

    levelbank_menu_values = manager.cvar(
        "warcraft_levelbank_menu_values",
        "1,5,10,25,40",
        "The level options available in the levelbank menu.\n",
        ConVarFlags.NOTIFY
    )