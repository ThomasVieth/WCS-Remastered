"""

"""

## python imports

from sqlalchemy import Column, ForeignKey, Integer, Sequence
from sqlalchemy.orm import relationship

## warcraft.package imports

from warcraft.database import engine
from warcraft.database._base import Base
from warcraft.database.player import Player

## __all__ declaration

__all__ = ("Levelbank", )

## levelbank model declaration

class Levelbank(Base):
    """
    """
    id = Column(Integer, Sequence('levelbank_id_seq'), primary_key=True)
    levels = Column(Integer)

    parent_id = Column(
        Integer,
        ForeignKey(Player.__tablename__ + ".id", ondelete="CASCADE"),
        nullable=False
    )
    parent = relationship("Player")

## levelbank table create

Levelbank.__table__.create(bind=engine, checkfirst=True)