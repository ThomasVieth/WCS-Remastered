"""

"""

## source.python imports

from cvars.flags import ConVarFlags
from config.manager import ConfigManager

## __all__ declaration

__all__ = (
	"logging_level",
	"default_race",
	"race_minimum_level",
	"race_maximum_level",
	"race_bot_options",
	"experience_for_kill",
	"experience_for_headshot",
	"experience_for_level_difference",
	"experience_for_win",
	"experience_for_loss",
	"experience_punish_for_loss",
	"experience_for_plant",
	"experience_for_explode",
	"experience_for_defuse"
)

## config declaration

with ConfigManager("warcraft") as manager:
	## Add the package header.
	manager.header = "Warcraft Source - Remastered"

	## Add the package-wide CVARs.
	logging_level = manager.cvar(
		"warcraft_logging_level",
		1,
		"The maximum level of logging entries that should print to the log.\n",
		ConVarFlags.CHEAT
	)
	logging_level.Description.append("INFO = 1")
	logging_level.Description.append("DEBUG = 2")
	logging_level.Description.append("WARNING = 3")
	logging_level.Description.append("ERROR = 4")

	race_section = manager.section("Race Configuration")

	default_race = manager.cvar(
		"warcraft_race_default",
		"Undead Scourge",
		"The name of the default race to assign to a new user.\n",
		ConVarFlags.NOTIFY
	)

	race_minimum_level = manager.cvar(
		"warcraft_race_starting_level",
		0,
		"The starting level that user will start at with a race.",
		ConVarFlags.NOTIFY
	)

	race_maximum_level = manager.cvar(
		"warcraft_race_maximum_level",
		99,
		"The maximum level that user may attain with a race.",
		ConVarFlags.NOTIFY
	)

	race_bot_options = manager.cvar(
		"warcraft_race_maximum_level",
		"Undead Scourge, Human Alliance, Orcish Horde, Night Elves",
		"The races that a bot may attain.",
		ConVarFlags.NOTIFY
	)

	experience_section = manager.section("Experience Configuration")

	experience_for_kill =  manager.cvar(
		"warcraft_experience_for_kill",
		50,
		"The experience gained for killing another player.",
		ConVarFlags.NOTIFY
	)

	experience_for_headshot =  manager.cvar(
		"warcraft_experience_for_headshot",
		80,
		"The experience gained for killing with a headshot.",
		ConVarFlags.NOTIFY
	)

	experience_for_level_difference =  manager.cvar(
		"warcraft_experience_for_level_difference",
		5,
		"The experience gained for killing a higher level player (per level).",
		ConVarFlags.NOTIFY
	)

	experience_for_win =  manager.cvar(
		"warcraft_experience_for_win",
		60,
		"The experience gained for winning a round.",
		ConVarFlags.NOTIFY
	)

	experience_punish_for_loss =  manager.cvar(
		"warcraft_experience_punish_for_loss",
		False,
		"Should the losing team be punished for losing?",
		ConVarFlags.NOTIFY
	)

	experience_for_loss =  manager.cvar(
		"warcraft_experience_for_loss",
		20,
		"The experience change for losing a round.",
		ConVarFlags.NOTIFY
	)
	experience_for_loss.Description.append("Setting punish to True will remove this much experience for losing.")

	experience_for_plant =  manager.cvar(
		"warcraft_experience_for_plant",
		30,
		"The experience gained for planting the bomb.",
		ConVarFlags.NOTIFY
	)

	experience_for_explode =  manager.cvar(
		"warcraft_experience_for_explode",
		30,
		"The experience gained for exploding the bomb.",
		ConVarFlags.NOTIFY
	)

	experience_for_defuse =  manager.cvar(
		"warcraft_experience_for_defuse",
		30,
		"The experience gained for defusing the bomb.",
		ConVarFlags.NOTIFY
	)