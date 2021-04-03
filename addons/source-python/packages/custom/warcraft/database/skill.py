"""

"""

## python imports

from sqlalchemy import Column, ForeignKey, Integer, Sequence, String
from sqlalchemy.orm import backref, relationship

## warcraft.package imports

from ._base import Base
from .player import Player
from .race import Race
from ..logging import debug, WARCRAFT_LOG_PATH

## __all__ declaration

__all__ = ("Skill", )

## logging location

databaselog_path = WARCRAFT_LOG_PATH / "database.log"

## skill model declaration

class Skill(Base):
	"""
	"""
	id = Column(Integer, Sequence('skill_id_seq'), primary_key=True)
	name = Column(String(64))
	level = Column(Integer)

	player_id = Column(
		Integer,
		ForeignKey(Player.__tablename__ + ".id", ondelete="CASCADE"),
		nullable=False
	)
	player = relationship("Player")

	parent_id = Column(
		Integer,
		ForeignKey(Race.__tablename__ + ".id", ondelete="CASCADE"),
		nullable=False
	)
	parent = relationship("Race", backref=backref("skills", lazy="dynamic"))