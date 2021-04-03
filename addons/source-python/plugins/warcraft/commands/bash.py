"""

"""

## source.python imports

from messages import Shake

## __all__ declaration

__all__ = ("bash", )

## bash declaration

def bash(player, magnitude, duration):
    shake_message = Shake(magnitude, duration)
    shake_message.send(player.index)