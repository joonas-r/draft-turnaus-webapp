import os
from sqlmodel import SQLModel, create_engine, Session, select
from models import Team
from models import Player
from models import Match

# Switch DATABASE_URL to the actual database in production
DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///test.db")
# Creates a connection to the database
engine = create_engine(DATABASE_URL)

# Creates database tables based on models.py where table=True
def create_db_and_tables():
    SQLModel.metadata.create_all(engine)

# Creates data for our test.db
def seed_mock_data():
    with Session(engine) as session:
        # Check if data exists, if true exit
        # Prevents duplication of data on restart
        existing = session.exec(select(Team)).first()
        if existing:
            return

        """
        Adds all items to session and commits at the end for
        database consistancy 
        """
        # leaderboard.html
        teams = [
            Team(name="Kiekkokingit", division="A", wins=10, draws=4, losses=0, goals_for=5, goals_against=1, points=6),
            Team(name="Jääkarhut", division="A", wins=1, draws=1, losses=0, goals_for=4, goals_against=2, points=4),
            Team(name="HC Metsurit", division="A", wins=0, draws=0, losses=2, goals_for=1, goals_against=5, points=0),
            Team(name="Kiekkokingit B", division="B", wins=2, draws=0, losses=0, goals_for=6, goals_against=2, points=6),
            Team(name="Jääkarhut B", division="B", wins=1, draws=0, losses=1, goals_for=3, goals_against=3, points=3),
            Team(name="HC Metsurit B", division="B", wins=0, draws=0, losses=2, goals_for=2, goals_against=6, points=0),
        ]
        for team in teams:
            session.add(team)

        # player.html
        players = [
            Player(name="Jan-Emil Sillanpaa", number=87, position1="H", position2="K", stick="L", invited_by="Matias Santapakka", years_played=3, age=24, playstyle="Kahden suunnan hyökkääjä", license="Yes"),
            Player(name="Sydney Crosby", number=87, position1="K", position2="P", stick="L", invited_by="Roope Lahti", years_played=3, age=24, playstyle="Graindaaja", license="X"),
            Player(name="Jan-Emil Sillanpaa", number=87, position1="H", position2="K", stick="L", invited_by="Matias Santapakka", years_played=3, age=24, playstyle="Kahden suunnan hyökkääjä", license="Yes"),
            Player(name="Sydney Crosby", number=87, position1="K", position2="P", stick="L", invited_by="Roope Lahti", years_played=3, age=24, playstyle="Graindaaja", license="X"),
            Player(name="Jan-Emil Sillanpaa", number=87, position1="H", position2="K", stick="L", invited_by="Matias Santapakka", years_played=3, age=24, playstyle="Kahden suunnan hyökkääjä", license="Yes"),
            Player(name="Sydney Crosby", number=87, position1="K", position2="P", stick="L", invited_by="Roope Lahti", years_played=3, age=24, playstyle="Graindaaja", license="X"),
            Player(name="Jan-Emil Sillanpaa", number=87, position1="H", position2="K", stick="L", invited_by="Matias Santapakka", years_played=3, age=24, playstyle="Kahden suunnan hyökkääjä", license="Yes"),
            Player(name="Sydney Crosby", number=87, position1="K", position2="P", stick="L", invited_by="Roope Lahti", years_played=3, age=24, playstyle="Graindaaja", license="X"),
            Player(name="Jan-Emil Sillanpaa", number=87, position1="H", position2="K", stick="L", invited_by="Matias Santapakka", years_played=3, age=24, playstyle="Kahden suunnan hyökkääjä", license="Yes"),
            Player(name="Sydney Crosby", number=87, position1="K", position2="P", stick="L", invited_by="Roope Lahti", years_played=3, age=24, playstyle="Graindaaja", license="X"),
            Player(name="Jan-Emil Sillanpaa", number=87, position1="H", position2="K", stick="L", invited_by="Matias Santapakka", years_played=3, age=24, playstyle="Kahden suunnan hyökkääjä", license="Yes"),
            Player(name="Sydney Crosby", number=87, position1="K", position2="P", stick="L", invited_by="Roope Lahti", years_played=3, age=24, playstyle="Graindaaja", license="X"),
            Player(name="Jan-Emil Sillanpaa", number=87, position1="H", position2="K", stick="L", invited_by="Matias Santapakka", years_played=3, age=24, playstyle="Kahden suunnan hyökkääjä", license="Yes"),
            Player(name="Sydney Crosby", number=87, position1="K", position2="P", stick="L", invited_by="Roope Lahti", years_played=3, age=24, playstyle="Graindaaja", license="X"),
            Player(name="Jan-Emil Sillanpaa", number=87, position1="H", position2="K", stick="L", invited_by="Matias Santapakka", years_played=3, age=24, playstyle="Kahden suunnan hyökkääjä", license="Yes"),
            Player(name="Sydney Crosby", number=87, position1="K", position2="P", stick="L", invited_by="Roope Lahti", years_played=3, age=24, playstyle="Graindaaja", license="X"),
            Player(name="Jan-Emil Sillanpaa", number=87, position1="H", position2="K", stick="L", invited_by="Matias Santapakka", years_played=3, age=24, playstyle="Kahden suunnan hyökkääjä", license="Yes"),
            Player(name="Sydney Crosby", number=87, position1="K", position2="P", stick="L", invited_by="Roope Lahti", years_played=3, age=24, playstyle="Graindaaja", license="X"),
            Player(name="Jan-Emil Sillanpaa", number=87, position1="H", position2="K", stick="L", invited_by="Matias Santapakka", years_played=3, age=24, playstyle="Kahden suunnan hyökkääjä", license="Yes"),
            Player(name="Sydney Crosby", number=87, position1="K", position2="P", stick="L", invited_by="Roope Lahti", years_played=3, age=24, playstyle="Graindaaja", license="X"),
            Player(name="Jan-Emil Sillanpaa", number=87, position1="H", position2="K", stick="L", invited_by="Matias Santapakka", years_played=3, age=24, playstyle="Kahden suunnan hyökkääjä", license="Yes"),
            Player(name="Sydney Crosby", number=87, position1="K", position2="P", stick="L", invited_by="Roope Lahti", years_played=3, age=24, playstyle="Graindaaja", license="X"),
            Player(name="Jan-Emil Sillanpaa", number=87, position1="H", position2="K", stick="L", invited_by="Matias Santapakka", years_played=3, age=24, playstyle="Hyökkäävä puolustaja", license="Yes"),
            Player(name="Sydney Crosby", number=87, position1="K", position2="P", stick="L", invited_by="Roope Lahti", years_played=3, age=24, playstyle="Graindaaja", license="X"),
            Player(name="Jan-Emil Sillanpaa", number=87, position1="H", position2="K", stick="L", invited_by="Matias Santapakka", years_played=3, age=24, playstyle="Kahden suunnan hyökkääjä", license="Yes"),
            Player(name="Sydney Crosby", number=87, position1="K", position2="P", stick="L", invited_by="Roope Lahti", years_played=3, age=24, playstyle="Graindaaja", license="X"),
            Player(name="Jan-Emil Sillanpaa", number=87, position1="H", position2="K", stick="L", invited_by="Matias Santapakka", years_played=3, age=24, playstyle="Kahden suunnan hyökkääjä", license="Yes"),
            Player(name="Sydney Crosby", number=87, position1="K", position2="P", stick="L", invited_by="Roope Lahti", years_played=3, age=24, playstyle="Graindaaja", license="X"),
            Player(name="Jan-Emil Sillanpaa", number=87, position1="H", position2="K", stick="L", invited_by="Matias Santapakka", years_played=3, age=24, playstyle="Kahden suunnan hyökkääjä", license="Yes"),
            Player(name="Sydney Crosby", number=87, position1="K", position2="P", stick="L", invited_by="Roope Lahti", years_played=3, age=24, playstyle="Graindaaja", license="X"),
            Player(name="Jan-Emil Sillanpaa", number=87, position1="H", position2="K", stick="L", invited_by="Matias Santapakka", years_played=3, age=24, playstyle="Kahden suunnan hyökkääjä", license="Yes"),
            Player(name="Sydney Crosby", number=87, position1="mv", position2="P", stick="L", invited_by="Roope Lahti", years_played=3, age=24, playstyle="Graindaaja", license="X"),
        ]
        for player in players:
            session.add(player)

        # schedule.html
        matches = [
            Match(division="A", home_team="Kiekkokingit", away_team="Rautakotkat", time="12.00"),
            Match(division="B", home_team="Jääkarhut", away_team="HC Metsurit", time="14.00"),
        ]
        for match in matches:
            session.add(match)

        # stats.html
        
        session.commit()

