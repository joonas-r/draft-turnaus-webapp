# from sqlmodel import SQLModel, Field
# from typing import Optional


# """
# Create database models for the database.py to use.
# Each class is a new table.
# The id is created automatically.
# """
# class Team(SQLModel, table=True):
#     id: Optional[int] = Field(default=None, primary_key=True)
#     name: str
#     division: str        # "A" or "B"
#     points: int = 0
#     wins: int = 0
#     draws: int = 0
#     losses: int = 0
#     goals_for: int = 0
#     goals_against: int = 0
#     points: int = 0
#     photo: str = "profile.png"  # filename of team photo

# class Player(SQLModel, table=True):
#     id: Optional[int] = Field(default=None, primary_key=True)
#     name: str
#     number: int
#     position1: str
#     position2: str
#     stick: str
#     invited_by: str
#     years_played: int
#     age: int
#     playstyle: str
#     license: str
#     photo: str = "profile.png"  # filename of player photo

# class Match(SQLModel, table=True):
#     id: Optional[int] = Field(default=None, primary_key=True)
#     division: str       # "A" or "B" or "playoff" etc.
#     home_team: str
#     away_team: str
#     time: str           # e.g. "12.00"
#     result: Optional[str] = None  # None until played



#### KOMMENTOI TÄMÄ OSA JA UNCOMMENT YLÄOSA TARVITTAESSA

#### KOMMENTOI paljon kerralla CTRL + K + C #### UNCOMMENT CTRL + K + U

from __future__ import annotations

from typing import Optional, List
from sqlmodel import SQLModel, Field, Relationship
from sqlalchemy import CheckConstraint

## TEAMS TABLE

class Team(SQLModel, table=True):
    __tablename__ = "teams"

    team_id: Optional[int] = Field(default=None, primary_key=True)
    team_name: str = Field(index=True, max_length=64)

    # captain is a player (nullable to avoid insert-order problems)
    captain_id: Optional[int] = Field(default=None, foreign_key="draft_players.player_id", nullable=True)
    logo_url: Optional[str] = Field(default=None, max_length=200)
    group: Optional[str] = Field(default=None, max_length=1) # A TAI B

    # NOTE: derived fields; keep only if you will maintain them in code/triggers
    wins: int = Field(default=0)
    draws: int = Field(default=0)
    losses: int = Field(default=0)
    games: int = Field(default=0)
    goals_for: int = Field(default=0)
    goals_against: int = Field(default=0)

    # Relationships
    players: List["Player"] = Relationship(
        back_populates="team",
        sa_relationship_kwargs={"foreign_keys": "Player.team_id"},
    )

    captain: Optional["Player"] = Relationship(
        sa_relationship_kwargs={"foreign_keys": "Team.captain_id"}
    )

    home_matches: List["Match"] = Relationship(
        back_populates="home_team",
        sa_relationship_kwargs={"foreign_keys": "Match.home_team_id"},
    )
    away_matches: List["Match"] = Relationship(
        back_populates="away_team",
        sa_relationship_kwargs={"foreign_keys": "Match.away_team_id"},
    )


## DRAFT PLAYERS TABLE

class Player(SQLModel, table=True):
    __tablename__ = "draft_players"

    player_id: Optional[int] = Field(default=None, primary_key=True)
    team_id: int = Field(foreign_key="teams.team_id", index=True, nullable=True)
    image_url: Optional[str] = Field(default=None, max_length=200)
    name: str = Field(max_length=32, index=True)
    age: int
    shirt_number: int
    lefthanded: bool = Field(default=False)
    recruiter: Optional[str] = Field(default=None, max_length=16)
    primary_pos: Optional[str] = Field(default=None, max_length=2)
    secondary_pos: Optional[str] = Field(default=None, max_length=2)
    playstyle: Optional[str] = Field(default=None, max_length=32)
    experience: int = Field(default=0)
    licenced: bool = Field(default=False)

    # Relationships
    team: Optional[Team] = Relationship(
        back_populates="players",
        sa_relationship_kwargs={"foreign_keys": "Player.team_id"},
    )

    stats: Optional["PlayerStats"] = Relationship(
        back_populates="player",
        sa_relationship_kwargs={"uselist": False, "cascade": "all, delete-orphan"},
    )

## PLAYER STATS TABLE

class PlayerStats(SQLModel, table=True):
    __tablename__ = "player_stats"

    # 1–1: player_id is both PK and FK
    player_id: int = Field(primary_key=True, foreign_key="draft_players.player_id")
    goals: int = Field(default=0)
    assists: int = Field(default=0)
    played_games: int = Field(default=0)
    penalty_min: int = Field(default=0)

    player: Optional[Player] = Relationship(back_populates="stats")

## MATCHES TABLE

class Match(SQLModel, table=True):
    __tablename__ = "matches"
    __table_args__ = (
        CheckConstraint("home_team_id <> away_team_id", name="ck_matches_home_neq_away"),
    )

    match_id: Optional[int] = Field(default=None, primary_key=True)
    playoff: bool = Field(default=False, index=True)

    home_team_id: int = Field(foreign_key="teams.team_id", index=True)
    away_team_id: int = Field(foreign_key="teams.team_id", index=True)

    home_score: int = Field(default=0)
    away_score: int = Field(default=0)

    home_team: Optional[Team] = Relationship(
        back_populates="home_matches",
        sa_relationship_kwargs={"foreign_keys": "Match.home_team_id"},
    )
    away_team: Optional[Team] = Relationship(
        back_populates="away_matches",
        sa_relationship_kwargs={"foreign_keys": "Match.away_team_id"},
    )