from fastapi import FastAPI, Request, Query
from fastapi.responses import HTMLResponse, FileResponse
from fastapi.staticfiles import StaticFiles
from sqlmodel import Session, select
from typing import List
from database import engine, create_db_and_tables, seed_mock_data
from models import Team
from models import Player
from models import Match

app = FastAPI()

# Run when the server starts
@app.on_event("startup")
def on_startup():
    create_db_and_tables()
    seed_mock_data()



# LEADERBOARD

def generate_team_rows(teams):
    rows = ""
    for i, team in enumerate(teams, 1):
        rows += f"""
            <tr class="tbody-tr">
                <td>{i}</td>
                <td>
                    <div class="team-container">
                        <img src="/static/photos/{team.photo}">
                        <span>{team.name}</span>
                    </div>
                </td>
                <td>{team.division}</td>
                <td>{team.points}</td>
                <td>{team.wins}</td>
                <td>{team.draws}</td>
                <td>{team.losses}</td>
                <td>{team.goals_for}</td>
                <td>{team.goals_against}</td>
            </tr>
        """
    return rows

@app.get("/leaderboard/division-a", response_class=HTMLResponse)
async def get_division_a():
    with Session(engine) as session:
        teams = session.exec(
            select(Team)
            .where(Team.division == "A")
            .order_by(Team.points.desc())
        ).all()
        return generate_team_rows(teams)

@app.get("/leaderboard/division-b", response_class=HTMLResponse)
async def get_division_b():
    with Session(engine) as session:
        teams = session.exec(
            select(Team)
            .where(Team.division == "B")
            .order_by(Team.points.desc())
        ).all()
        return generate_team_rows(teams)



# PLAYERS LIST

@app.get("/players", response_class=HTMLResponse)
async def get_players(
    position1: str = Query(default=""),
    position2: str = Query(default=""),
    stick: str = Query(default=""),
    # age: int = Query(default=""),
    # years_played: str = Query(default=""),
    playstyle: str = Query(default=""),
    license: str = Query(default=""),
    invited_by: str = Query(default=""),
    sort: str = Query(default="asc"),
):
    with Session(engine) as session:
        query = select(Player)

        p1_list = [v for v in position1.split(",") if v]
        p2_list = [v for v in position2.split(",") if v]
        stick_list = [v for v in stick.split(",") if v]
        # age_list = [v for v in age.split(",") if v]
        # years_played_list = [v for v in years_played.split(",") if v]
        playstyle_list = [v for v in playstyle.split(",") if v]
        license_list = [v for v in license.split(",") if v]
        invited_by_list = [v for v in invited_by.split(",") if v]

        # only apply filter if user selected something
        if p1_list:
            query = query.where(Player.position1.in_(p1_list))
        if p2_list:
            query = query.where(Player.position2.in_(p2_list))
        if stick_list:
            query = query.where(Player.stick.in_(stick_list))
        # if age_list:
        #     query = query.where(Player.age.in_(age_list))
        # if years_played_list:
        #     query = query.where(Player.years_played.in_(years_played_list))
        if playstyle_list:
            query = query.where(Player.playstyle.in_(playstyle_list))
        if license_list:
            query = query.where(Player.license.in_(license_list))
        if invited_by_list:
            query = query.where(Player.invited_by.in_(invited_by_list))

        # sort by name based on parameter
        if sort == "asc":
            query = query.order_by(Player.name.asc())
        else:
            query = query.order_by(Player.name.desc())

        players = session.exec(query).all()
        rows = ""
        for player in players:
            rows += f"""
                <tr class="tbody-tr">
                    <td>
                        <div class="player-container">
                            <div class="player-img-container">
                                <img src="/photos/{player.photo}">
                            </div>
                            <span>{player.name}</span>
                        </div>
                    </td>
                    <td>{player.number}</td>
                    <td>{player.position1}</td>
                    <td>{player.position2}</td>
                    <td>{player.stick}</td>
                    <td>{player.age}</td>
                    <td>{player.years_played}</td>
                    <td>{player.playstyle}</td>
                    <td>{player.license}</td>
                    <td>{player.invited_by}</td>
                </tr>
            """
        return rows


# MATCH SCHEDULES

@app.get("/schedule/division-a", response_class=HTMLResponse)
async def get_schedule_a():
    # SELECT * FROM match WHERE division = 'A'
    with Session(engine) as session:
        matches = session.exec(
            select(Match).where(Match.division == "A")
        ).all()
        return generate_match_rows(matches)

@app.get("/schedule/division-b", response_class=HTMLResponse)
async def get_schedule_b():
    # SELECT * FROM match WHERE division = 'B'
    with Session(engine) as session:
        matches = session.exec(
            select(Match).where(Match.division == "B")
        ).all()
        return generate_match_rows(matches)

def generate_match_rows(matches):
    rows = ""
    for match in matches:
        result = match.result or "N/A"
        rows += f"""
            <tr class="matchup-container">
                <td>
                    <div class="matchup-info-container">
                        <div class="matchup-info">
                            <span>Koti</span>
                            <span>{match.time}</span>
                            <span>Vieras</span>
                        </div>
                    </div>
                </td>
                <td>
                    <div class="matchup-teams">
                        <div class="team-container">
                            <span>{match.home_team}</span>
                            <div class="team-img-container">
                                <img class="team-img" src="/photos/profile.png">
                            </div>
                        </div>
                        <span class="matchup-vs">@</span>
                        <div class="team-container">
                            <div class="team-img-container">
                                <img class="team-img" src="/photos/profile.png">
                            </div>
                            <span>{match.away_team}</span>
                        </div>
                    </div>
                </td>
                <td class="game-result-container">
                    <span>Tulos:</span>
                    <div class="game-result">
                        <span>{result}</span>
                    </div>
                </td>
            </tr>
        """
    return rows

app.mount("/", StaticFiles(directory="static", html=True), name="static")