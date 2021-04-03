"""

"""

## python imports

from sqlalchemy import Column, ForeignKey, Integer, Sequence, String
from sqlalchemy.orm import backref, relationship

## warcraft.package imports

from ._base import Base
from .player import Player
from ..logging import debug, WARCRAFT_LOG_PATH

## __all__ declaration

__all__ = ("Race", )

## logging location

databaselog_path = WARCRAFT_LOG_PATH / "database.log"

## race model declaration

class Race(Base):
	"""
	"""
	id = Column(Integer, Sequence('race_id_seq'), primary_key=True)
	name = Column(String(64))
	level = Column(Integer)
	experience = Column(Integer)

	parent_id = Column(
		Integer,
		ForeignKey(Player.__tablename__ + ".id", ondelete="CASCADE"),
		nullable=False
	)
	parent = relationship("Player", backref=backref("races", lazy="dynamic"))