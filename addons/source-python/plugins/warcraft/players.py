"""

"""

## python imports

from collections import defaultdict
from datetime import datetime
from sqlalchemy import and_

## source.python imports

from engines.server import engine_server
from events import Event
from listeners import OnClientDisconnect, OnClientFullyConnect
from players.dictionary import PlayerDictionary
from players.entity import Player as SPPlayer

## warcraft.package imports

from warcraft.config import default_race, race_minimum_level
from warcraft.database import session, Race as dbRace, Skill as dbSkill, Player as dbPlayer
from warcraft.events import call_event
from warcraft.logging import debug, error, WARCRAFT_LOG_PATH
from warcraft.race import Race

## __all__ declaration

__all__ = ("player_dict", "Player", )


## logging definition

playerslog_path = WARCRAFT_LOG_PATH / "players.log"

## player override

class Player(SPPlayer):
	"""
	SourcePython's Player class redefinition to handle data loading for players and management of
	database object states within the plugin.

	:attribute _dbinstance: For each entity within the plugin (Player, Race, Skill), each has a
		_dbinstance attribute to manage the database object.
	"""

	def __init__(self, *args, **kwargs):
		super().__init__(*args, **kwargs)

		self.ignored_spawn_events = 0

		## Validate player data.
		player_data = session.query(dbPlayer).filter(dbPlayer.steamid == self.identifier).first()
		if not player_data:
			player_data = self.create_user_data()
			session.commit()
		self._dbinstance = player_data

		## Validate race data and load.
		race_cls = Race.find_race(player_data.current_race)
		if not race_cls:
			error(playerslog_path, f"Could not use configured value of {player_data.current_race} as default race.")
			race_cls = Race.default
		race_data = self.get_race_data(race_cls)
		self.race = self.init_race_from_data(race_cls, race_data)

		debug(playerslog_path, f"Setting up player <{self.name}> data.")

		self.items = list()

		self.call_events_when_dead = False

		self.is_slowed = False

	def create_user_data(self):
		"""
		Creates a player's initial database object and returns this object.

		:return: A new database Player object.
		:rtype: warcraft.database.Player 
		"""
		player_data = dbPlayer(
			steamid=self.identifier,
			current_race=default_race.cvar.get_string(),
			last_active=datetime.now()
		)
		session.add(player_data)
		return player_data

	def update_user_data(self):
		"""
		Updates the player's database attributes using the Player class attributes
		and then commits.
		"""
		self._dbinstance.username = self.name
		self._dbinstance.last_active = datetime.now()
		self._dbinstance.current_race = self.race.name
		session.commit()

	def create_race_data(self, race_cls):
		"""
		Creates a race database object and all skill objects, then returns the race object.

		:return: A new database Race object.
		:rtype: warcraft.database.Race 
		"""
		race_data = dbRace(
			name=race_cls.name,
			level=race_minimum_level.cvar.get_int(),
			experience=0,
			parent=self._dbinstance
		)
		for skill_cls in race_cls._skills:
			skill_data = dbSkill(
				name=skill_cls.name,
				level=skill_cls.min_level,
				player=self._dbinstance,
				parent=race_data
			)
			session.add(skill_data)
		session.add(race_data)
		return race_data

	def update_race_data(self):
		"""
		Updates the player's race database attributes using the Race class attributes
		and then commits.
		"""
		self.race._dbinstance.level = self.race.level
		self.race._dbinstance.experience = self.race.experience
		for skill in self.race.skills:
			skill_data = self.race._dbinstance.skills.filter(dbSkill.name == skill.name).first()
			skill_data.level = skill.level
		session.commit()

	def get_race_data(self, race_cls):
		"""
		Attempts to retrieve the database object for the specified race. If not found,
		creates a new Race database object for this race. Finally, this returns the
		found/new database object.
		"""
		race_data = session.query(dbRace).filter(and_(dbRace.name == race_cls.name, dbRace.parent == self._dbinstance)).first()
		if not race_data:
			race_data = self.create_race_data(race_cls)
		return race_data

	def init_race_from_data(self, race_cls, race_data):
		"""
		Initializes a Race object using the data from the race_data database object supplied.
		"""
		race = race_cls(race_data.experience, init_level=race_data.level, parent=self)
		race._dbinstance = race_data
		for skill in race.skills:
			skill_data = race_data.skills.filter(and_(dbSkill.name == skill.name, dbSkill.parent == race._dbinstance)).first()
			if not skill_data:
				skill_data = dbSkill(
					name=skill.name,
					level=skill.min_level,
					player=self._dbinstance,
					parent=race_data
				)
				session.add(skill_data)
			skill.level = skill_data.level
		return race

	def change_race(self, race_cls):
		"""
		Force changes a player's race to the newly provided Race class.

		This in-turn obtains the race data, kills the user, and then initializes the new object.
		"""
		self.update_race_data() ## save current race data
		race_data = self.get_race_data(race_cls) ## gather new race data
		self.client_command("kill", True) ## kill the user between race changes
		new_race = self.init_race_from_data(race_cls, race_data) ## build new race object
		call_event(
			"race_change",
			[],
			{
				"player": self,
				"old_race": self.race,
				"new_race": new_race
			}
		) ## call race_change event
		self.race = new_race ## assign new race to player
		self.update_user_data() ## update database to represent race change

	@property
	def total_level(self):
		"""
		Gets the total level of all races the player owns.
		"""
		return sum(data.level for data in self._dbinstance.races)

	@property
	def identifier(self):
		"""
		Gets the identifier the database should use to gather the player's data.
		"""
		if self.steamid == 'BOT':
			return 'BOT_' + self.name
		return self.steamid

	def call_events(self, event_name, *args, **kwargs):
		self.race.call_events(event_name, *args, **kwargs)
		items = self.items.copy()
		for item in items:
			item.call_events(event_name, *args, **kwargs)

	def call_clientcommands(self, command_name, *args, **kwargs):
		self.race.call_events(command_name, *args, **kwargs)
		items = self.items.copy()
		for item in items:
			item.call_clientcommands(command_name, *args, **kwargs)

## core

player_dict = PlayerDictionary(factory=Player)

@OnClientFullyConnect
def on_client_fully_connect(index):
	if index == 0:
		return
	player = player_dict[index]
	##player.is_connected = True

@OnClientDisconnect
def _player_cleanup(index):
	player = player_dict[index]
	player.call_events("player_death", player=player)
	player.update_race_data()