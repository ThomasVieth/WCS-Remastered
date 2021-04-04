"""

"""

## python imports

from collections import defaultdict
from functools import wraps

## __all__ declaration

__all__ = ("clientcommands", "events", )

## callback handler

class CallbackHandler:

	def __init__(self, *args, **kwargs):
		self._events = defaultdict(set)
		self._clientcommands = defaultdict(set)

		for attr in dir(self):
			method = getattr(self, attr)

			if not callable(method):
				continue

			if hasattr(method, '_events'):
				for event in method._events:
					self._events[event].add(method)

			if hasattr(method, '_clientcommands'):
				for clientcommand in method._clientcommands:
					self._clientcommands[clientcommand].add(method)

	def call_events(self, event_name, *args, **kwargs):
		for callback in self._events[event_name]:
			callback(*args, **kwargs)

	def call_clientcommands(self, command_name, *args, **kwargs):
		for callback in self._clientcommands[command_name]:
			callback(*args, **kwargs)

## decoration objects

def clientcommands(*clientcommands):
	"""
	Client command decorator, could easily
	be replaced with a event on the
	virtual function (run_command).
	"""

	def decorator(method):
		method._clientcommands = clientcommands
		@wraps(method)
		def wrapping(*args, **kwargs):
			return method(*args, **kwargs)
		return wrapping
	return decorator

def events(*events):
	"""
	Event decorator used for managing
	methods inside skills, and allowing
	us to establish which should be
	called and when.
	"""

	def decorator(method):
		method._events = events
		@wraps(method)
		def wrapping(*args, **kwargs):
			return method(*args, **kwargs)
		return wrapping
	return decorator