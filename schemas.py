from sqlmodel import SQLModel
from typing import Optional

class PlayerCreate(SQLModel):
    team_id: int
    name: str
    age: int
    shirt_number: int
    image_url: Optional[str] = None
    lefthanded: bool = False
    recruiter: Optional[str] = None
    primary_pos: Optional[str] = None
    secondary_pos: Optional[str] = None
    playstyle: Optional[str] = None
    experience: int = 0
    licenced: bool = False
