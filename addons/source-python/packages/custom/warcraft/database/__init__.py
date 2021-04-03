"""

"""

## python imports

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

## source.python imports

from paths import CUSTOM_DATA_PATH

## warcraft.package imports

from ._base import Base
from .player import Player
from .race import Race
from .skill import Skill

## __all__ declaration

__all__ = (
	"engine",
	"session",
	"Player",
	"Race",
	"Skill",
)

## database session opening

sqlite_path = CUSTOM_DATA_PATH / "warcraft" / "players.db"

engine = create_engine(f"sqlite:///{sqlite_path}")

Base.metadata.create_all(engine)

Session = sessionmaker(bind=engine)
session = Session()