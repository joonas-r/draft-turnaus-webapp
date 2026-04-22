from sqlmodel import SQLModel, Field
from typing import Optional


"""
Create database models for the database.py to use.
Each class is a new table.
The id is created automatically.
"""
class Team(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    name: str
    division: str        # "A" or "B"
    points: int = 0
    wins: int = 0
    draws: int = 0
    losses: int = 0
    goals_for: int = 0
    goals_against: int = 0
    points: int = 0
    photo: str = "profile.png"  # filename of team photo

class Player(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    name: str
    number: int
    position1: str
    position2: str
    stick: str
    invited_by: str
    years_played: int
    age: int
    playstyle: str
    license: str
    photo: str = "profile.png"  # filename of player photo

class Match(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    division: str       # "A" or "B" or "playoff" etc.
    home_team: str
    away_team: str
    time: str           # e.g. "12.00"
    result: Optional[str] = None  # None until played