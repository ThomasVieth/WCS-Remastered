"""

"""

## python imports

from collections import defaultdict
from functools import wraps
from typing import Any, Callable, Dict, List, Optional

## warcraft.package imports

from .logging import debug, WARCRAFT_LOG_PATH

## logging definition

eventlog_path = WARCRAFT_LOG_PATH / "events.log"

## __all__ declaration

__all__ = ("Event", "call_event")

## events class declaration

_events = defaultdict(set)

def Event(name: str):
	"""Decorator for wrapping a function into the warcraft events system.
	
	:param name: The name of the event to wrap into.
	:type name: str
	"""
	def outside(func: Callable):
		@wraps(func)
		def inside(*args, **kwargs):
			func(*args, **kwargs)
			debug(eventlog_path, f"Called {func} by warcraft event \"{name}\".")
		debug(eventlog_path, f"Wrapping {func} in warcraft event \"{name}\".")
		_events[name].add(func)
		return inside
	return outside

def call_event(name: str, event_args: List[Any], event_kwargs: Dict[str, Any]):
	"""Calls all functions mapped to the named event with the args and kwargs supplied.

	:param name: The name of the event to call wrapped functions for.
	:type name: str
	:param event_args: A list of arguments to supply to the function.
	:type event_args: list
	:param event_kwargs: A keyword dict to supply to the function.
	:type event_kwargs: dict
	:return: None
	:rtype: null
	"""
	for func in _events[name]:
		debug(eventlog_path, f"Calling {func} by warcraft event \"{name}\".")
		func(*event_args, **event_kwargs)