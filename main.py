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

# No need to add new players via api

# @app.post("/players")
# def add_player(
#     player_in: schemas.PlayerCreate,
#     session: Session = Depends(get_session)
# ):
#     try:
#         # Return player
#         return crud.create_player(session=session, player_in=player_in)
#     except Exception as e:
#         # Error handling
#         raise HTTPException(
#             status_code=400,
#             detail=str(e)
#         )


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
            "team_id" : Player.team_id,
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
            empty_player = f"""
                <tr>
                    <td colspan="9" style="text-align:left; padding: 20px;">
                        Mikään pelaaja ei vastannut hakua.
                    </td>
                </tr>
            """
            return empty_player
        else:
            rows = ""
            for player in players:
                stick_display    = "L" if player.lefthanded else "R"
                licenced_display = "✓" if player.licenced else "X"
                image            = player.image_url or "profile.png"
                rows += f"""
                    <tr class="tbody-tr">
                        <td class="left-column">
                            <div class="player-container">
                                <div class="player-img-container">
                                    <img src="/photos/{image}">
                                </div>
                                <span>{player.name}</span>
                            </div>
                        </td>
                        <td>{player.shirt_number or ""}</td>
                        <td>{player.team_id or ""}</td>
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

# Variables to store playoff game templates


def generate_match_rows(matches, session):
    game_count = 0
    rows = ""
    for match in matches:
        # fetch team objects using their IDs stored in match
        home = session.get(Team, match.home_team_id)
        away = session.get(Team, match.away_team_id)
        home_logo = home.logo_url or "profile.png"
        away_logo = away.logo_url or "profile.png"
        game_count += 1
        if match.finished == False:
            rows += f"""
                <tr class="matchup-container">
                    <td class="game-header">
                        <span>{match.match_time}</span>
                    </td>
                    <td>
                        <div class="matchup-teams">
                            <div class="team-container home-team">
                                <span>{home.team_name}</span>
                                <div class="team-img-container">
                                    <svg width="50px" height="50px">
                                        <use class="team-img" href="{home_logo}"></use>
                                    </svg>
                                </div>
                            </div>
                            <span class="matchup-vs">@</span>
                            <div class="team-container away-team">
                                <div class="team-img-container">
                                    <svg width="50px" height="50px">
                                        <use class="team-img" href="{away_logo}"></use>
                                    </svg>
                                </div>
                                <span>{away.team_name}</span>
                            </div>
                        </div>
                    </td>
                </tr>
            """
        else:
            if match.home_score > match.away_score:
                rows += f"""
                    <tr class="matchup-container">
                        <td class="game-header">
                            <div class="game-result">
                                <span>
                                    <span style="font-weight: 700">
                                        {match.home_score}
                                    </span> -
                                    <span style="font-weight: normal">
                                        {match.away_score}
                                    </span>
                                </span>
                            </div>
                        </td>
                        <td>
                            <div class="matchup-teams">
                                <div class="team-container home-team">
                                    <span style="font-weight: 700">
                                        {home.team_name}
                                    </span>
                                    <div class="team-img-container">
                                        <svg width="50px" height="50px">
                                            <use class="team-img" href="{home_logo}"></use>
                                        </svg>
                                    </div>
                                </div>
                                <span class="matchup-vs">@</span>
                                <div class="team-container away-team">
                                    <div class="team-img-container">
                                        <svg width="50px" height="50px">
                                            <use class="team-img" href="{away_logo}"></use>
                                        </svg>
                                    </div>
                                    <span style="font-weight: normal">
                                        {away.team_name}
                                    </span>
                                </div>
                            </div>
                        </td>
                        
                    </tr>
                """
            else:
                rows += f"""
                    <tr class="matchup-container">
                        <td class="game-header">
                            <div class="game-result">
                                <span>
                                    <span style="font-weight: normal">
                                        {match.home_score}
                                    </span> -
                                    <span style="font-weight: 700">
                                        {match.away_score}
                                    </span>
                                </span>
                            </div>
                        </td>
                        <td>
                            <div class="matchup-teams">
                                <div class="team-container home-team">
                                    <span style="font-weight: normal">
                                        {home.team_name}
                                    </span>
                                    <div class="team-img-container">
                                        <svg width="50px" height="50px">
                                            <use class="team-img" href="{home_logo}"></use>
                                        </svg>
                                    </div>
                                </div>
                                <span class="matchup-vs">@</span>
                                <div class="team-container away-team">
                                    <div class="team-img-container">
                                        <svg width="50px" height="50px">
                                            <use class="team-img" href="{away_logo}"></use>
                                        </svg>
                                    </div>
                                    <span style="font-weight: 700">
                                        {away.team_name}
                                    </span>
                                </div>
                            </div>
                        </td>
                        
                    </tr>
                """
    return rows

def generate_playoff_rows(matches, session):
    # Variables to store playoff game templates
    playoff_qf1 = f"""
            <tr class="matchup-container">
                <td class="game-header">
                    <span>14:30</span>
                </td>
                <td>
                    <div class="matchup-teams">
                        <div class="team-container home-team">
                            <span>B2</span>
                            <div class="team-img-container">
                                <svg width="42px" height="42px">
                                    <use class="team-img" href="/logos/logo_black_white.svg#logo_black_white"></use>
                                </svg>
                            </div>
                        </div>
                        <span class="matchup-vs">@</span>
                        <div class="team-container away-team">
                            <div class="team-img-container">
                                <svg width="42px" height="42px">
                                    <use class="team-img" href="/logos/logo_black_white.svg#logo_black_white"></use>
                                </svg>
                            </div>
                            <span>A3</span>
                        </div>
                    </div>
                </td>
                <td>
                    <div class="game-footer">
                        <span>QF1</span>
                    </div>
                </td>
            </tr>
        """
    playoff_qf2 = f"""
            <tr class="matchup-container">
                <td class="game-header">
                    <span>15:30</span>
                </td>
                <td>
                    <div class="matchup-teams">
                        <div class="team-container home-team">
                            <span>A2</span>
                            <div class="team-img-container">
                                <svg width="42px" height="42px">
                                    <use class="team-img" href="/logos/logo_black_white.svg#logo_black_white"></use>
                                </svg>
                            </div>
                        </div>
                        <span class="matchup-vs">@</span>
                        <div class="team-container away-team">
                            <div class="team-img-container">
                                <svg width="42px" height="42px">
                                    <use class="team-img" href="/logos/logo_black_white.svg#logo_black_white"></use>
                                </svg>
                            </div>
                            <span>B3</span>
                        </div>
                    </div>
                </td>
                <td>
                    <div class="game-footer">
                        <span>QF2</span>
                    </div>
                </td>
            </tr>
        """
    playoff_sf1 = f"""
            <tr class="matchup-container">
                <td class="game-header">
                    <span>16:30</span>
                </td>
                <td>
                    <div class="matchup-teams">
                        <div class="team-container home-team">
                            <span>A1</span>
                            <div class="team-img-container">
                                <svg width="42px" height="42px">
                                    <use class="team-img" href="/logos/logo_black_white.svg#logo_black_white"></use>
                                </svg>
                            </div>
                        </div>
                        <span class="matchup-vs">@</span>
                        <div class="team-container away-team">
                            <div class="team-img-container">
                                <svg width="42px" height="42px">
                                    <use class="team-img" href="/logos/logo_black_white.svg#logo_black_white"></use>
                                </svg>
                            </div>
                            <span>QF1</span>
                        </div>
                    </div>
                </td>
                <td>
                    <div class="game-footer">
                        <span>SF1</span>
                    </div>
                </td>
            </tr>
        """
    playoff_sf2 = f"""
            <tr class="matchup-container">
                <td class="game-header">
                    <span>17:30</span>
                </td>
                <td>
                    <div class="matchup-teams">
                        <div class="team-container home-team">
                            <span>B1</span>
                            <div class="team-img-container">
                                <svg width="42px" height="42px">
                                    <use class="team-img" href="/logos/logo_black_white.svg#logo_black_white"></use>
                                </svg>
                            </div>
                        </div>
                        <span class="matchup-vs">@</span>
                        <div class="team-container away-team">
                            <div class="team-img-container">
                                <svg width="42px" height="42px">
                                    <use class="team-img" href="/logos/logo_black_white.svg#logo_black_white"></use>
                                </svg>
                            </div>
                            <span>QF2</span>
                        </div>
                    </div>
                </td>
                <td>
                    <div class="game-footer">
                        <span>SF2</span>
                    </div>
                </td>
            </tr>
        """
    playoff_final = f"""
            <tr class="matchup-container">
                <td class="game-header">
                    <span>19:00</span>
                </td>
                <td>
                    <div class="matchup-teams">
                        <div class="team-container home-team">
                            <span>SF2</span>
                            <div class="team-img-container">
                                <svg width="42px" height="42px">
                                    <use class="team-img" href="/logos/logo_black_white.svg#logo_black_white"></use>
                                </svg>
                            </div>
                        </div>
                        <span class="matchup-vs">@</span>
                        <div class="team-container away-team">
                            <div class="team-img-container">
                                <svg width="42px" height="42px">
                                    <use class="team-img" href="/logos/logo_black_white.svg#logo_black_white"></use>
                                </svg>
                            </div>
                            <span>SF1</span>
                        </div>
                    </div>
                </td>
                <td>
                    <div class="game-footer">
                        <span>FINAALI</span>
                    </div>
                </td>
            </tr>
            """
    
    if matches == []:
        empty_matches = f"""
            <tr class="matchup-container">
                <td class="game-header">
                    <span>14:30</span>
                </td>
                <td>
                    <div class="matchup-teams">
                        <div class="team-container home-team">
                            <span>B2</span>
                            <div class="team-img-container">
                                <svg width="42px" height="42px">
                                    <use class="team-img" href="/logos/logo_black_white.svg#logo_black_white"></use>
                                </svg>
                            </div>
                        </div>
                        <span class="matchup-vs">@</span>
                        <div class="team-container away-team">
                            <div class="team-img-container">
                                <svg width="42px" height="42px">
                                    <use class="team-img" href="/logos/logo_black_white.svg#logo_black_white"></use>
                                </svg>
                            </div>
                            <span>A3</span>
                        </div>
                    </div>
                </td>
                <td>
                    <div class="game-footer">
                        <span>QF1</span>
                    </div>
                </td>
            </tr>
            <tr class="matchup-container">
                <td class="game-header">
                    <span>15:30</span>
                </td>
                <td>
                    <div class="matchup-teams">
                        <div class="team-container home-team">
                            <span>A2</span>
                            <div class="team-img-container">
                                <svg width="42px" height="42px">
                                    <use class="team-img" href="/logos/logo_black_white.svg#logo_black_white"></use>
                                </svg>
                            </div>
                        </div>
                        <span class="matchup-vs">@</span>
                        <div class="team-container away-team">
                            <div class="team-img-container">
                                <svg width="42px" height="42px">
                                    <use class="team-img" href="/logos/logo_black_white.svg#logo_black_white"></use>
                                </svg>
                            </div>
                            <span>B3</span>
                        </div>
                    </div>
                </td>
                <td>
                    <div class="game-footer">
                        <span>QF2</span>
                    </div>
                </td>
            </tr>
            <tr class="matchup-container">
                <td class="game-header">
                    <span>16:30</span>
                </td>
                <td>
                    <div class="matchup-teams">
                        <div class="team-container home-team">
                            <span>A1</span>
                            <div class="team-img-container">
                                <svg width="42px" height="42px">
                                    <use class="team-img" href="/logos/logo_black_white.svg#logo_black_white"></use>
                                </svg>
                            </div>
                        </div>
                        <span class="matchup-vs">@</span>
                        <div class="team-container away-team">
                            <div class="team-img-container">
                                <svg width="42px" height="42px">
                                    <use class="team-img" href="/logos/logo_black_white.svg#logo_black_white"></use>
                                </svg>
                            </div>
                            <span>QF1</span>
                        </div>
                    </div>
                </td>
                <td>
                    <div class="game-footer">
                        <span>SF1</span>
                    </div>
                </td>
            </tr>
            <tr class="matchup-container">
                <td class="game-header">
                    <span>17:30</span>
                </td>
                <td>
                    <div class="matchup-teams">
                        <div class="team-container home-team">
                            <span>B1</span>
                            <div class="team-img-container">
                                <svg width="42px" height="42px">
                                    <use class="team-img" href="/logos/logo_black_white.svg#logo_black_white"></use>
                                </svg>
                            </div>
                        </div>
                        <span class="matchup-vs">@</span>
                        <div class="team-container away-team">
                            <div class="team-img-container">
                                <svg width="42px" height="42px">
                                    <use class="team-img" href="/logos/logo_black_white.svg#logo_black_white"></use>
                                </svg>
                            </div>
                            <span>QF2</span>
                        </div>
                    </div>
                </td>
                <td>
                    <div class="game-footer">
                        <span>SF2</span>
                    </div>
                </td>
            </tr>
            <tr class="matchup-container">
                <td class="game-header">
                    <span>19:00</span>
                </td>
                <td>
                    <div class="matchup-teams">
                        <div class="team-container home-team">
                            <span>SF2</span>
                            <div class="team-img-container">
                                <svg width="42px" height="42px">
                                    <use class="team-img" href="/logos/logo_black_white.svg#logo_black_white"></use>
                                </svg>
                            </div>
                        </div>
                        <span class="matchup-vs">@</span>
                        <div class="team-container away-team">
                            <div class="team-img-container">
                                <svg width="42px" height="42px">
                                    <use class="team-img" href="/logos/logo_black_white.svg#logo_black_white"></use>
                                </svg>
                            </div>
                            <span>SF1</span>
                        </div>
                    </div>
                </td>
                <td>
                    <div class="game-footer">
                        <span>FINAALI</span>
                    </div>
                </td>
            </tr>
            """
        
        return empty_matches
    else:
        game_count = 0
        rows = ""
        playoff_stage = ""
        stage_names = ["QF1", "QF2", "SF1", "SF2", "Finaali"]
        
        for match in matches:
            # fetch team objects using their IDs stored in match
            home = session.get(Team, match.home_team_id)
            away = session.get(Team, match.away_team_id)
            game_count += 1
            playoff_stage = stage_names[game_count]
            
            # stages = [playoff_qf2, playoff_sf1, playoff_sf2, playoff_final]
            # playoff_stage = stages[game_count - 1]

            home_logo = home.logo_url or "profile.png"
            away_logo = away.logo_url or "profile.png"
            if match.finished == False:
                rows += f"""
                        <tr class="matchup-container">
                            <td class="game-header">
                                <span>{match.match_time}</span>
                            </td>
                            <td>
                                <div class="matchup-teams">
                                    <div class="team-container home-team">
                                        <span>{home.team_name}</span>
                                        <div class="team-img-container">
                                            <svg width="50px" height="50px">
                                                <use class="team-img" href="{home_logo}"></use>
                                            </svg>
                                        </div>
                                    </div>
                                    <span class="matchup-vs">@</span>
                                    <div class="team-container away-team">
                                        <div class="team-img-container">
                                            <svg width="50px" height="50px">
                                                <use class="team-img" href="{away_logo}"></use>
                                            </svg>
                                        </div>
                                        <span>{away.team_name}</span>
                                    </div>
                                </div>
                            </td>
                            <td>
                                <div class="game-footer">
                                    <span>{playoff_stage}</span>
                                </div>
                            </td>
                        </tr>
                    """
            else:
                if match.home_score > match.away_score:
                    rows += f"""
                        <tr class="matchup-container">
                            <td class="game-header">
                                <div class="game-result">
                                    <span>
                                        <span style="font-weight: 700">
                                            {match.home_score}
                                        </span> -
                                        <span>
                                            {match.away_score}
                                        </span>
                                    </span>
                                </div>
                            </td>
                            <td>
                                <div class="matchup-teams">
                                    <div class="team-container home-team">
                                        <span style="font-weight: 700">
                                            {home.team_name}
                                        </span>
                                        <div class="team-img-container">
                                            <svg width="50px" height="50px">
                                                <use class="team-img" href="{home_logo}"></use>
                                            </svg>
                                        </div>
                                    </div>
                                    <span class="matchup-vs">@</span>
                                    <div class="team-container away-team">
                                        <div class="team-img-container">
                                            <svg width="50px" height="50px">
                                                <use class="team-img" href="{away_logo}"></use>
                                            </svg>
                                        </div>
                                        <span>
                                            {away.team_name}
                                        </span>
                                    </div>
                                </div>
                            </td>
                            <td>
                                <div class="game-footer">
                                    <span>{playoff_stage}</span>
                                </div>
                            </td>
                        </tr>
                    """
                else:
                    rows += f"""
                        <tr class="matchup-container">
                            <td class="game-header">
                                <div class="game-result">
                                    <span>
                                        <span>
                                            {match.home_score}
                                        </span> -
                                        <span style="font-weight: 700">
                                            {match.away_score}
                                        </span>
                                    </span>
                                </div>
                            </td>
                            <td>
                                <div class="matchup-teams">
                                    <div class="team-container home-team">
                                        <span>
                                            {home.team_name}
                                        </span>
                                        <div class="team-img-container">
                                            <svg width="50px" height="50px">
                                                <use class="team-img" href="{home_logo}"></use>
                                            </svg>
                                        </div>
                                    </div>
                                    <span class="matchup-vs">@</span>
                                    <div class="team-container away-team">
                                        <div class="team-img-container">
                                            <svg width="50px" height="50px">
                                                <use class="team-img" href="{away_logo}"></use>
                                            </svg>
                                        </div>
                                        <span style="font-weight: 700">
                                            {away.team_name}
                                        </span>
                                    </div>
                                </div>
                            </td>
                            <td>
                                <div class="game-footer">
                                    <span>{playoff_stage}</span>
                                </div>
                            </td>
                        </tr>
                    """

        remaining_placeholders = {
            1: playoff_qf2 + playoff_sf1 + playoff_sf2 + playoff_final,
            2: playoff_sf1 + playoff_sf2 + playoff_final,
            3: playoff_sf2 + playoff_final,
            4: playoff_final,
            5: "",
        }
        rows += remaining_placeholders.get(game_count, "")
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
        return generate_playoff_rows(matches, session)


# -------------------------------------------------------
# STATIC FILES - must be last
# -------------------------------------------------------

app.mount("/", StaticFiles(directory="static", html=True), name="static")
