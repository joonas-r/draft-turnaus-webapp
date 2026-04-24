from fastapi import FastAPI, Query, HTTPException, Depends
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from sqlmodel import Session, select
from database import engine, create_db_and_tables, seed_mock_data, get_session
from models import Team, Player, PlayerStats, Match
import crud, schemas

app = FastAPI()

# Runs automatically when the server starts
@app.on_event("startup")
def on_startup():
    create_db_and_tables()
#    seed_mock_data()

@app.post("/players")
def add_player(
    player_in: schemas.PlayerCreate,
    session: Session = Depends(get_session)
):
    try:
        # Return player
        return crud.create_player(session=session, player_in=player_in)
    except Exception as e:
        # Error handling
        raise HTTPException(
            status_code=400,
            detail=str(e)
        )


# -------------------------------------------------------
# LEADERBOARD
# -------------------------------------------------------

def generate_team_rows(teams):
    rows = ""
    for i, team in enumerate(teams, 1):
        # calculate points: win = 3pts, draw = 1pt, loss = 0pts
        points = (team.wins * 3) + team.draws
        logo = team.logo_url or "profile.png"
        rows += f"""
            <tr class="tbody-tr">
                <td>{i}</td>
                <td>
                    <div class="team-container">
                        <img src="/photos/{logo}">
                        <span>{team.team_name}</span>
                    </div>
                </td>
                <td>{team.group}</td>
                <td>{points}</td>
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
            .where(Team.group == "A")
            .order_by((Team.wins * 3 + Team.draws).desc())
        ).all()
        return generate_team_rows(teams)

@app.get("/leaderboard/division-b", response_class=HTMLResponse)
async def get_division_b():
    with Session(engine) as session:
        teams = session.exec(
            select(Team)
            .where(Team.group == "B")
            .order_by((Team.wins * 3 + Team.draws).desc())
        ).all()
        return generate_team_rows(teams)


# -------------------------------------------------------
# PLAYERS
# -------------------------------------------------------

@app.get("/players", response_class=HTMLResponse)
async def get_players(
    position1: str = Query(default=""),
    position2: str = Query(default=""),
    stick: str = Query(default=""),
    playstyle: str = Query(default=""),
    licenced: str = Query(default=""),
    recruiter: str = Query(default=""),
    sort_by: str = Query(default="name"),
    sort_order: str = Query(default="asc"),
):
    with Session(engine) as session:
        query = select(Player)

        # split comma separated filter strings into lists
        p1_list       = [v for v in position1.split(",") if v]
        p2_list       = [v for v in position2.split(",") if v]
        stick_list    = [v for v in stick.split(",") if v]
        playstyle_list = [v for v in playstyle.split(",") if v]
        licenced_list = [v for v in licenced.split(",") if v]
        recruiter_list = [v for v in recruiter.split(",") if v]

        # apply filters only when something is selected
        if p1_list:
            query = query.where(Player.primary_pos.in_(p1_list))
        if p2_list:
            query = query.where(Player.secondary_pos.in_(p2_list))
        if stick_list:
            # lefthanded is bool in new model: L = True, R = False
            if "L" in stick_list and "R" not in stick_list:
                query = query.where(Player.lefthanded == True)
            elif "R" in stick_list and "L" not in stick_list:
                query = query.where(Player.lefthanded == False)
            # if both selected no filter needed - show all
        if playstyle_list:
            query = query.where(Player.playstyle.in_(playstyle_list))
        if licenced_list:
            # licenced is bool: ✓ = True, X = False
            if "✓" in licenced_list and "X" not in licenced_list:
                query = query.where(Player.licenced == True)
            elif "X" in licenced_list and "✓" not in licenced_list:
                query = query.where(Player.licenced == False)
        if recruiter_list:
            query = query.where(Player.recruiter.in_(recruiter_list))

        # Map frontend sort parameters to actual database columns
        sort_map = {
            "name": Player.name,
            "shirt_number": Player.shirt_number,
            "primary_pos": Player.primary_pos,
            "secondary_pos": Player.secondary_pos,
            "stick": Player.lefthanded,
            "age": Player.age,
            "experience": Player.experience,
            "playstyle": Player.playstyle,
            "licenced": Player.licenced,
            "recruiter": Player.recruiter
        }
        
        # Get the selected field, default to Player.name if not found
        field = sort_map.get(sort_by, Player.name)

        if sort_order == "asc":
            query = query.order_by(field.asc())
        else:
            query = query.order_by(field.desc())
        
        players = session.exec(query).all()
        if players == []:
            empty = f"""
                <div class="no-filter-match">
                    <span>Mikään pelaaja ei vastannut hakua.</span>
                </div>
                """
            return empty
        else:
            rows = ""
            for player in players:
                stick_display    = "L" if player.lefthanded else "R"
                licenced_display = "✓" if player.licenced else "X"
                image            = player.image_url or "profile.png"
                rows += f"""
                    <tr class="tbody-tr">
                        <td>
                            <div class="player-container">
                                <div class="player-img-container">
                                    <img src="/photos/{image}">
                                </div>
                                <span>{player.name}</span>
                            </div>
                        </td>
                        <td>{player.shirt_number}</td>
                        <td>{player.primary_pos or "-"}</td>
                        <td>{player.secondary_pos or "-"}</td>
                        <td>{stick_display}</td>
                        <td>{player.age}</td>
                        <td>{player.experience}</td>
                        <td>{player.playstyle or "-"}</td>
                        <td>{licenced_display}</td>
                        <td>{player.recruiter or "Toimitsijat"}</td>
                    </tr>
                """
            return rows


# -------------------------------------------------------
# SCHEDULE
# -------------------------------------------------------

def generate_match_rows(matches, session):
    rows = ""
    for match in matches:
        # fetch team objects using their IDs stored in match
        home = session.get(Team, match.home_team_id)
        away = session.get(Team, match.away_team_id)
        home_logo = home.logo_url or "profile.png"
        away_logo = away.logo_url or "profile.png"
        rows += f"""
            <tr class="matchup-container">
                <td>
                    <div class="matchup-teams">
                        <div class="team-container">
                            <span>{home.team_name}</span>
                            <div class="team-img-container">
                                <img class="team-img" src="/photos/{home_logo}">
                            </div>
                        </div>
                        <span class="matchup-vs">@</span>
                        <div class="team-container">
                            <div class="team-img-container">
                                <img class="team-img" src="/photos/{away_logo}">
                            </div>
                            <span>{away.team_name}</span>
                        </div>
                    </div>
                </td>
                <td class="game-result-container">
                    <span>Tulos:</span>
                    <div class="game-result">
                        <span>{match.home_score} - {match.away_score}</span>
                    </div>
                </td>
            </tr>
        """
    return rows

@app.get("/schedule/division-a", response_class=HTMLResponse)
async def get_schedule_a():
    with Session(engine) as session:
        # get team IDs for group A
        group_a_ids = [
            t.team_id for t in session.exec(
                select(Team).where(Team.group == "A")
            ).all()
        ]
        matches = session.exec(
            select(Match)
            .where(Match.playoff == False)
            .where(Match.home_team_id.in_(group_a_ids))
        ).all()
        return generate_match_rows(matches, session)

@app.get("/schedule/division-b", response_class=HTMLResponse)
async def get_schedule_b():
    with Session(engine) as session:
        group_b_ids = [
            t.team_id for t in session.exec(
                select(Team).where(Team.group == "B")
            ).all()
        ]
        matches = session.exec(
            select(Match)
            .where(Match.playoff == False)
            .where(Match.home_team_id.in_(group_b_ids))
        ).all()
        return generate_match_rows(matches, session)

@app.get("/schedule/playoffs", response_class=HTMLResponse)
async def get_schedule_playoffs():
    with Session(engine) as session:
        matches = session.exec(
            select(Match).where(Match.playoff == True)
        ).all()
        return generate_match_rows(matches, session)


# -------------------------------------------------------
# STATIC FILES - must be last
# -------------------------------------------------------

app.mount("/", StaticFiles(directory="static", html=True), name="static")