"""

"""

## source.python imports

from commands.server import ServerCommand

## warcraft.package imports

from .bash import bash
from .helpers import retrieve_extra_args
from .messages import send_wcs_saytext_by_index, send_wcs_saytext_by_userid
from .setfx import setfx_options
from ..players import player_dict

## command registration

@ServerCommand("wcs_bash")
def _bash_command(command):
    player = player_dict.from_userid(int(command[1]))
    args = retrieve_extra_args(command, 1)
    bash(player, *args)

@ServerCommand("wcs_setfx")
def _setfx_command(command):
    option = command[1]
    if not option in setfx_options:
        raise ValueError(f"Cannot run setfx with value {option}. Please read the docs.")

    func = setfx_options[option]
    player = player_dict.from_userid(int(command[2]))
    args = retrieve_extra_args(command, 2)
    func(player, *args)

@ServerCommand("wcs_tell")
def _tell_command(command):
    userid = int(command[1])
    text = ""
    max_index = len(command) - 1
    for i in range(2, max_index + 1):
        text += command[i]
        if i < max_index:
            text += ' '
    send_wcs_saytext_by_userid(text, userid)

@ServerCommand("wcs_tell_index")
def _tell_command_index(command):
    index = int(command[1])
    text = ""
    max_index = len(command) - 1
    for i in range(2, max_index + 1):
        text += command[i]
        if i < max_index:
            text += ' '
    send_wcs_saytext_by_index(text, index)