"""

"""

## source.python imports

from players.helpers import index_from_userid
from messages import SayText2
from messages.colors.saytext2 import *

## __all__ declaration

__all__ = (
    "prepare_wcs_saytext",
    "send_wcs_saytext_by_index",
    "send_wcs_saytext_by_userid"
)

## color dictionary

COLORS = {
    "WHITE": WHITE,
    "RED": RED,
    "BRIGHT_GREEN": BRIGHT_GREEN,
    "PALE_GREEN": PALE_GREEN,
    "GREEN": GREEN,
    "PALE_RED": PALE_RED,
    "GRAY": GRAY,
    "YELLOW": YELLOW,
    "LIGHT_BLUE": LIGHT_BLUE,
    "BLUE": BLUE,
    "DARK_BLUE": DARK_BLUE,
    "PINK": PINK,
    "DULL_RED": DULL_RED,
    "ORANGE": ORANGE
}

## prepare functions

def prepare_wcs_saytext(text):
    message = "{GREEN}[WCS]{PALE_GREEN}: ".format(**COLORS) + text.format(**COLORS)
    return SayText2(message)

## quicksend functions

def send_wcs_saytext_by_index(text, index):
    message = "{GREEN}[WCS]{PALE_GREEN}: ".format(**COLORS) + text.format(**COLORS)
    return SayText2(message).send(index)

def send_wcs_saytext_by_userid(text, userid):
    message = "{GREEN}[WCS]{PALE_GREEN}: ".format(**COLORS) + text.format(**COLORS)
    index = index_from_userid(userid)
    return SayText2(message).send(index)