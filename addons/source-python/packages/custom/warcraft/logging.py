"""

"""

## python imports

from functools import partial
from typing import Optional

## source.python imports

from engines.server import engine_server
from paths import LOG_PATH

## warcraft.package imports

from .config import logging_level

## __all__ declaration

__all__ = (
	"debug",
	"error",
	"info",
	"warning",
	"WARCRAFT_LOG_PATH",
)

## logging configuration

DEBUG_PREFIX 	= "[DEBUG] "
ERROR_PREFIX 	= "[ERROR] "
INFO_PREFIX 	= "[INFO] "
WARNING_PREFIX 	= "[WARNING] "

WARCRAFT_LOG_PATH = LOG_PATH / "warcraft"

## logging func declarations

def print_wrapper(prefix: str, level: int, file_path: str, message: str) -> bool:
	"""Prints a line to the file_path with the prefix only if the logging level
	of the warcraft package is more than this level.

	:param file_path: The path to the file to print too.
	:type file_path: str
	:param message: The message to print to the file.
	:type message: str
	:param logging_level: The current logging level, use purpose is to override
	current status.
	:type logging_level: int

	:return: Whether the print to file was successful.
	:rtype: bool
	"""
	try:
		if level <= logging_level.cvar.get_int():
			with open(file_path, "a") as file_obj:
				file_obj.write(prefix + message + "\n")
			engine_server.log_print(prefix + message + "\n")
		return True
	except:
		engine_server.log_print(f"Failed to log to {file_path}!\n")
		return False

debug = partial(print_wrapper, DEBUG_PREFIX, 2)
error = partial(print_wrapper, ERROR_PREFIX, 4)
info = partial(print_wrapper, INFO_PREFIX, 1)
warning = partial(print_wrapper, WARNING_PREFIX, 3)