"""

"""

## warcraft.package imports

from .helpers import operator_options

## __all__ declaration

__all__ = ("setfx_options", )

## setfx base functions

def invis_change(player, operator_str, value):
    if not operator_str in operator_options:
        raise ValueError(f"Cannot run setfx with operator {operator_str}. Please read the docs.")
    operator = operator_options[operator_str]
    color = player.color
    color.a = operator(color.a, int(value))
    player.color = color

def invis_percentage(player, operator_str, value):
    if not operator_str in operator_options:
        raise ValueError(f"Cannot run setfx with operator {operator_str}. Please read the docs.")
    operator = operator_options[operator_str]
    color = player.color
    current_percent = (color.a / 255) * 100
    percent = operator(current_percent, int(value))
    percent = min(100, max(0, percent)) ## Disallowing unreal alpha percentages.
    color.a = int((percent / 100) * 255)
    player.color = color

def health_change(player, operator_str, value):
    if not operator_str in operator_options:
        raise ValueError(f"Cannot run setfx with operator {operator_str}. Please read the docs.")
    operator = operator_options[operator_str]
    player.health = operator(player.health, int(value))

def speed_change(player, operator_str, value):
    if not operator_str in operator_options:
        raise ValueError(f"Cannot run setfx with operator {operator_str}. Please read the docs.")
    operator = operator_options[operator_str]
    player.speed = operator(player.speed, int(value))

setfx_options = {
    "invis": invis_change,
    "invis_percent": invis_percentage,
    "health": health_change,
    "speed": speed_change,
}