"""

"""

## python imports

from sqlalchemy import (Boolean, Column, DateTime,
	Integer, Sequence, String, Unicode)
from sqlalchemy.orm import relationship

## warcraft.package imports

from ._base import Base
from ..logging import debug, WARCRAFT_LOG_PATH

## __all__ declaration

__all__ = ("Player", )

## logging location

databaselog_path = WARCRAFT_LOG_PATH / "database.log"

## player model declaration

class Player(Base):
    """
    """
    id = Column(Integer, Sequence('player_id_seq'), primary_key=True)
    username = Column(Unicode(64))
    steamid = Column(String(64))
    current_race = Column(String(64))
    last_active = Column(DateTime)
    is_admin = Column(Boolean, default=False)
    races = relationship("Race", back_populates="parent")