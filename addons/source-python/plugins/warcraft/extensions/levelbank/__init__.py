"""

"""

## source.python imports

from commands import CommandReturn
from commands.client import ClientCommand
from commands.say import SayCommand
from listeners import OnClientFullyConnect

## warcraft.package imports

from warcraft.database import session
from warcraft.players import player_dict

## extension imports

from .config import *
from .database import *
from .menus import *

## __all__ declaration

__all__ = (
    "levelbank_menu",
)

## handling new players

@OnClientFullyConnect
def _on_client_full_connect_setup_levelbank(index):
    player = player_dict[index]
    player_levelbank = session.query(Levelbank).filter(Levelbank.parent == player._dbinstance).first()
    if not player_levelbank:
        start_levels = levelbank_start_amount.cvar.get_int()
        player_levelbank = Levelbank(levels=start_levels, parent=player._dbinstance)
        session.add(player_levelbank)
        session.commit()

## handling client/say commands

@ClientCommand(["levelbank", "wcsbank"])
@SayCommand(["levelbank", "wcsbank"])
def _levelbank_say_command(command, index, team_only=None):
    levelbank_menu.send(index)
    return CommandReturn.BLOCK