from datetime import datetime, timezone
from database.db_setup import Base
from sqlalchemy import Column, Integer, String, Boolean, Float, DateTime


class Player(Base):
    """A player that participates in the discord league
    A player is described with the following attributes:
    - id: the unique identifier of the player (discord id)
    - display_name: the name that the player uses in the discord server
    - verified: a boolean indicating if the player has been verified
    - active: a boolean indicating if the player is active in the league
    - mmr: the matchmaking rating of the player
    """

    __tablename__ = 'players'

    id = Column(Integer, primary_key=True)  # discord id
    display_name = Column(String)
    active = Column(Boolean, default=False)
    mmr = Column(Float, default=0.0)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))

    def set_mmr(self, mmr: float) -> None:
        if mmr < 0:
            raise ValueError("MMR cannot be negative")
        self.mmr = mmr  # type: ignore

    def __repr__(self):
        return f"Player(id={self.id}, display_name={self.display_name}, active={self.active}, mmr={self.mmr})"

    def __str__(self):
        return self.__repr__()

    def __gt__(self, other: 'Player') -> bool:
        if not isinstance(other, Player):
            raise TypeError("Cannot compare Player with non-Player object")
        return self.mmr > other.mmr

    def __lt__(self, other: 'Player') -> bool:
        if not isinstance(other, Player):
            raise TypeError("Cannot compare Player with non-Player object")
        return self.mmr < other.mmr

    def __eq__(self, other) -> bool:
        if not isinstance(other, Player):
            raise TypeError("Cannot compare Player with non-Player object")
        return self.mmr == other.mmr

    def __ne__(self, other) -> bool:
        if not isinstance(other, Player):
            raise TypeError("Cannot compare Player with non-Player object")
        return self.mmr != other.mmr

    def __ge__(self, other: 'Player') -> bool:
        if not isinstance(other, Player):
            raise TypeError("Cannot compare Player with non-Player object")
        return self.mmr >= other.mmr

    def __le__(self, other: 'Player') -> bool:
        if not isinstance(other, Player):
            raise TypeError("Cannot compare Player with non-Player object")
        return self.mmr <= other.mmr

    def __hash__(self):
        return hash(self.id)

    def __bool__(self) -> bool:
        return self.active

    def __getitem__(self, key):
        return getattr(self, key)

    def __setitem__(self, key, value):
        setattr(self, key, value)
