import os
from sqlmodel import SQLModel, create_engine, Session, select
from models import Team, Player, PlayerStats, Match
from dotenv import load_dotenv, dotenv_values

# Load .env enviroment variables
load_dotenv()

# Switch DATABASE_URL to the actual database in production
#DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///test.db") # db_url
DATABASE_URL = os.getenv("db_url")

# Creates a connection to the database
engine = create_engine(DATABASE_URL)

# Create a session, can call from other places
def get_session():
     with Session(engine) as session:
         yield session

# Creates database tables based on models.py where table=True
def create_db_and_tables():
    SQLModel.metadata.create_all(engine)

# Creates mock data for test.db
def seed_mock_data():
    with Session(engine) as session:
        # Check if data exists - prevents duplication on restart
        existing = session.exec(select(Team)).first()
        if existing:
            return

        # --- TEAMS ---
        # Teams must be committed first so they get IDs
        # Players and matches reference these IDs

        team_a1 = Team(team_name="Kiekkokingit",  group="A", wins=4, draws=1, losses=0, games=5, goals_for=18, goals_against=6)
        team_a2 = Team(team_name="Jääkarhut",     group="A", wins=2, draws=1, losses=2, games=5, goals_for=12, goals_against=11)
        team_a3 = Team(team_name="HC Metsurit",   group="A", wins=0, draws=0, losses=5, games=5, goals_for=4,  goals_against=17)
        team_b1 = Team(team_name="Rautakotkat",   group="B", wins=3, draws=2, losses=0, games=5, goals_for=15, goals_against=7)
        team_b2 = Team(team_name="Jäätiikerit",   group="B", wins=2, draws=0, losses=3, games=5, goals_for=10, goals_against=12)
        team_b3 = Team(team_name="Lumivyöry",     group="B", wins=0, draws=2, losses=3, games=5, goals_for=6,  goals_against=12)

        for team in [team_a1, team_a2, team_a3, team_b1, team_b2, team_b3]:
            session.add(team)
        session.commit()  # commit so teams get their IDs before players reference them

        # --- PLAYERS ---
        # team_id links each player to their team
        # lefthanded is a bool: True = L, False = R
        # licenced is a bool: True = has licence, False = no licence

        players = [
            # --- TEAM A1 ---
            Player(team_id=team_a1.team_id, name="Jan-Emil Sillanpaa", shirt_number=87, primary_pos="K", secondary_pos="H", lefthanded=True,  age=24, experience=3,  playstyle="Kahden suunnan hyökkääjä", licenced=True,  recruiter=""),
            Player(team_id=team_a1.team_id, name="Mikko Korhonen",      shirt_number=11, primary_pos="P", secondary_pos="K", lefthanded=False, age=28, experience=5,  playstyle="Hyökkäävä puolustaja",     licenced=True,  recruiter=""),
            Player(team_id=team_a1.team_id, name="Ville Mäkinen",       shirt_number=34, primary_pos="H", secondary_pos="K", lefthanded=True,  age=22, experience=1,  playstyle="Graindaaja",              licenced=False, recruiter=""),
            Player(team_id=team_a1.team_id, name="Tero Leinonen",       shirt_number=55, primary_pos="P", secondary_pos=None,lefthanded=False, age=31, experience=9,  playstyle="Puolustava puolustaja",    licenced=True,  recruiter=""),
            Player(team_id=team_a1.team_id, name="Olli Saarinen",       shirt_number=19, primary_pos="MV",secondary_pos=None,lefthanded=True,  age=26, experience=4,  playstyle="Aggressiivinen torjuja",   licenced=True,  recruiter=""),

            # --- TEAM A2 ---
            Player(team_id=team_a2.team_id, name="Pekka Virtanen",      shirt_number=7,  primary_pos="K", secondary_pos="H", lefthanded=True,  age=29, experience=6,  playstyle="Pelin rakentaja",          licenced=True,  recruiter="Roope Lahti"),
            Player(team_id=team_a2.team_id, name="Janne Heikkinen",     shirt_number=22, primary_pos="H", secondary_pos="K", lefthanded=False, age=25, experience=3,  playstyle="Nopeuspelaaja",            licenced=False, recruiter=""),
            Player(team_id=team_a2.team_id, name="Lauri Nieminen",      shirt_number=44, primary_pos="P", secondary_pos=None,lefthanded=True,  age=33, experience=11, playstyle="Puolustava puolustaja",    licenced=True,  recruiter=""),
            Player(team_id=team_a2.team_id, name="Sami Koskinen",       shirt_number=3,  primary_pos="P", secondary_pos="H", lefthanded=False, age=27, experience=5,  playstyle="Hyökkäävä puolustaja",     licenced=True,  recruiter="Roope Lahti"),
            Player(team_id=team_a2.team_id, name="Ari Salonen",        shirt_number=30, primary_pos="MV",secondary_pos=None,lefthanded=True,  age=30, experience=8,  playstyle="Rauhallinen torjuja",      licenced=True,  recruiter=""),

            # --- TEAM A3 ---
            Player(team_id=team_a3.team_id, name="Hannu Järvinen",      shirt_number=9,  primary_pos="K", secondary_pos="H", lefthanded=True,  age=23, experience=2,  playstyle="Graindaaja",              licenced=False, recruiter="Matias Keränen"),
            Player(team_id=team_a3.team_id, name="Kimmo Hakala",        shirt_number=16, primary_pos="H", secondary_pos="H", lefthanded=False, age=21, experience=1,  playstyle="Nopeuspelaaja",            licenced=False, recruiter="Mitri Keränen"),
            Player(team_id=team_a3.team_id, name="Petri Mäkinen",       shirt_number=5,  primary_pos="P", secondary_pos=None,lefthanded=True,  age=35, experience=14, playstyle="Puolustava puolustaja",    licenced=True,  recruiter=""),
            Player(team_id=team_a3.team_id, name="Risto Leppänen",      shirt_number=24, primary_pos="P", secondary_pos="K", lefthanded=False, age=28, experience=6,  playstyle="Hyökkäävä puolustaja",     licenced=True,  recruiter=""),
            Player(team_id=team_a3.team_id, name="Vesa Hämäläinen",     shirt_number=31, primary_pos="MV",secondary_pos=None,lefthanded=True,  age=32, experience=10, playstyle="Aggressiivinen torjuja",   licenced=True,  recruiter=""),

            # --- TEAM B1 ---
            Player(team_id=team_b1.team_id, name="Antti Korhonen",      shirt_number=14, primary_pos="K", secondary_pos="H", lefthanded=False, age=26, experience=4,  playstyle="Pelin rakentaja",          licenced=True,  recruiter="Julius Metsälä"),
            Player(team_id=team_b1.team_id, name="Jari Laine",          shirt_number=28, primary_pos="H", secondary_pos="K", lefthanded=True,  age=30, experience=7,  playstyle="Kahden suunnan hyökkääjä", licenced=True,  recruiter=""),
            Player(team_id=team_b1.team_id, name="Matti Rantanen",      shirt_number=6,  primary_pos="P", secondary_pos=None,lefthanded=False, age=24, experience=3,  playstyle="Puolustava puolustaja",    licenced=False, recruiter=""),
            Player(team_id=team_b1.team_id, name="Ilkka Turunen",       shirt_number=2,  primary_pos="P", secondary_pos="H", lefthanded=True,  age=29, experience=6,  playstyle="Hyökkäävä puolustaja",     licenced=True,  recruiter="Titus Metsälä"),
            Player(team_id=team_b1.team_id, name="Keijo Niemi",         shirt_number=35, primary_pos="MV",secondary_pos=None,lefthanded=False, age=27, experience=5,  playstyle="Rauhallinen torjuja",      licenced=True,  recruiter=""),

            # --- TEAM B2 ---
            Player(team_id=team_b2.team_id, name="Timo Aaltonen",       shirt_number=18, primary_pos="K", secondary_pos="H", lefthanded=True,  age=25, experience=3,  playstyle="Nopeuspelaaja",            licenced=False, recruiter="Roni Haarala"),
            Player(team_id=team_b2.team_id, name="Eero Lindqvist",      shirt_number=41, primary_pos="H", secondary_pos="K", lefthanded=False, age=34, experience=12, playstyle="Graindaaja",              licenced=True,  recruiter=""),
            Player(team_id=team_b2.team_id, name="Harri Kinnunen",      shirt_number=4,  primary_pos="P", secondary_pos=None,lefthanded=True,  age=22, experience=1,  playstyle="Puolustava puolustaja",    licenced=False, recruiter=""),
            Player(team_id=team_b2.team_id, name="Seppo Mustonen",      shirt_number=17, primary_pos="P", secondary_pos="K", lefthanded=False, age=31, experience=9,  playstyle="Hyökkäävä puolustaja",     licenced=True,  recruiter=""),
            Player(team_id=team_b2.team_id, name="Unto Väisänen",       shirt_number=29, primary_pos="MV",secondary_pos=None,lefthanded=True,  age=28, experience=6,  playstyle="Aggressiivinen torjuja",   licenced=True,  recruiter=""),

            # --- TEAM B3 ---
            Player(team_id=team_b3.team_id, name="Paavo Heinonen",      shirt_number=13, primary_pos="K", secondary_pos="H", lefthanded=False, age=20, experience=1,  playstyle="Pelin rakentaja",          licenced=False, recruiter="Roope Lahti"),
            Player(team_id=team_b3.team_id, name="Osmo Leppänen",       shirt_number=77, primary_pos="H", secondary_pos="K", lefthanded=True,  age=38, experience=16, playstyle="Kahden suunnan hyökkääjä", licenced=True,  recruiter=""),
            Player(team_id=team_b3.team_id, name="Reino Mäkinen",       shirt_number=8,  primary_pos="P", secondary_pos=None,lefthanded=False, age=26, experience=4,  playstyle="Puolustava puolustaja",    licenced=True,  recruiter=""),
            Player(team_id=team_b3.team_id, name="Aarne Salminen",      shirt_number=21, primary_pos="P", secondary_pos="H", lefthanded=True,  age=23, experience=2,  playstyle="Hyökkäävä puolustaja",     licenced=False, recruiter=""),
            Player(team_id=team_b3.team_id, name="Urho Koivisto",       shirt_number=33, primary_pos="MV",secondary_pos=None,lefthanded=False, age=30, experience=8,  playstyle="Rauhallinen torjuja",      licenced=True,  recruiter=""),
        ]

        for player in players:
            session.add(player)
        session.commit()  # commit players so they get IDs before stats reference them

        # --- PLAYER STATS ---
        # player_id links to draft_players table
        # one PlayerStats row per player

        all_players = session.exec(select(Player)).all()
        for p in all_players:
            stats = PlayerStats(
                player_id=p.player_id,
                goals=0,
                assists=0,
                played_games=0,
                penalty_min=0,
            )
            session.add(stats)

        # --- MATCHES ---
        # home_team_id and away_team_id reference teams.team_id
        # playoff=False means group stage, playoff=True means playoff

        matches = [
            # Group A matches
            Match(home_team_id=team_a1.team_id, away_team_id=team_a2.team_id, home_score=3, away_score=1, playoff=False),
            Match(home_team_id=team_a2.team_id, away_team_id=team_a3.team_id, home_score=2, away_score=0, playoff=False),
            Match(home_team_id=team_a1.team_id, away_team_id=team_a3.team_id, home_score=5, away_score=1, playoff=False),
            Match(home_team_id=team_a2.team_id, away_team_id=team_a1.team_id, home_score=2, away_score=3, playoff=False),
            Match(home_team_id=team_a3.team_id, away_team_id=team_a1.team_id, home_score=1, away_score=4, playoff=False),
            # Group B matches
            Match(home_team_id=team_b1.team_id, away_team_id=team_b2.team_id, home_score=4, away_score=2, playoff=False),
            Match(home_team_id=team_b2.team_id, away_team_id=team_b3.team_id, home_score=3, away_score=1, playoff=False),
            Match(home_team_id=team_b1.team_id, away_team_id=team_b3.team_id, home_score=3, away_score=3, playoff=False),
            Match(home_team_id=team_b3.team_id, away_team_id=team_b1.team_id, home_score=2, away_score=3, playoff=False),
            Match(home_team_id=team_b2.team_id, away_team_id=team_b1.team_id, home_score=1, away_score=2, playoff=False),
        ]

        for match in matches:
            session.add(match)

        session.commit()