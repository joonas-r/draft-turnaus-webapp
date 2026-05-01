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

# -------------------------------------------------------
# INDEX
# -------------------------------------------------------

@app.get("/schedule/upcoming", response_class=HTMLResponse)
async def get_upcoming_matches():
    with Session(engine) as session:
        # 1. Look for real upcoming games (Regular or Playoff)
        matches = session.exec(
            select(Match)
            .where(Match.finished == False)
            .order_by(Match.match_time.asc())
            .limit(3)
        ).all()
        
        if matches:
            return generate_dashboard_schedule_rows(matches, session)
            
        # 2. Fallback: If no real games are left, show the mock-up playoff placeholders
        # We pass an empty list to your existing generator to get the placeholders
        return generate_playoff_rows([], session)

def generate_dashboard_schedule_rows(matches, session):
    rows = ""
    for match in matches:
        home = session.get(Team, match.home_team_id)
        away = session.get(Team, match.away_team_id)
        
        # Check if it's a playoff game to add a label[cite: 3]
        playoff_label = '<span class="playoff-tag">PLAYOFF</span>' if match.playoff else ""
        
        rows += f"""
            <tr class="matchup-container">
                <td class="game-header">
                    <span>{match.match_time}</span>
                    {playoff_label}
                </td>
                <td>
                    <div class="matchup-teams">
                        <div class="team-container home-team">
                            <span>{home.team_name}</span>
                            <div class="team-img-container">
                                <svg width="40px" height="40px"><use href="{home.logo_url}"></use></svg>
                            </div>
                        </div>
                        <span class="matchup-vs">@</span>
                        <div class="team-container away-team">
                            <div class="team-img-container">
                                <svg width="40px" height="40px"><use href="{away.logo_url}"></use></svg>
                            </div>
                            <span>{away.team_name}</span>
                        </div>
                    </div>
                </td>
            </tr>
        """
    return rows


# -------------------------------------------------------
# LEADERBOARD
# -------------------------------------------------------

def generate_team_rows(teams, sort_by="points"):
    rows = ""
    # Helper to apply the highlight class if the column matches the sort criteria
    def get_cls(col): 
        return ' class="active-sort-cell"' if sort_by == col else ""

    for i, team in enumerate(teams, 1):
        points = (team.wins * 2) + team.draws
        
        rows += f"""
            <tr class="tbody-tr">
                <td>{i}</td>
                <td{get_cls('team_name')}>
                    <div class="team-container" title="{team.team_name}">
                        <div class="team-img-container">
                            <svg width="50px" height="50px">
                                <use class="team-img" href="{team.logo_url}"></use>
                            </svg>
                        </div>
                        <span>{team.team_name}</span>
                    </div>
                </td>
                <td{get_cls('group')}>{team.group}</td>
                <td{get_cls('games')}>{team.games}</td>
                <td{get_cls('points')}>{points}</td>
                <td{get_cls('wins')}>{team.wins}</td>
                <td{get_cls('draws')}>{team.draws}</td>
                <td{get_cls('losses')}>{team.losses}</td>
                <td{get_cls('goals_for')}>{team.goals_for}</td>
                <td{get_cls('goals_against')}>{team.goals_against}</td>
            </tr>
        """
    return rows

@app.get("/leaderboard/division-a", response_class=HTMLResponse)
async def get_division_a():
    with Session(engine) as session:
        # Use * 2 for wins to match generate_team_rows logic
        teams = session.exec(
            select(Team)
            .where(Team.group == "A")
            .order_by((Team.wins * 2 + Team.draws).desc())
        ).all()
        return generate_team_rows(teams)

@app.get("/leaderboard/division-b", response_class=HTMLResponse)
async def get_division_b():
    with Session(engine) as session:
        # Use * 2 for wins to match generate_team_rows logic
        teams = session.exec(
            select(Team)
            .where(Team.group == "B")
            .order_by((Team.wins * 2 + Team.draws).desc())
        ).all()
        return generate_team_rows(teams)
    
@app.get("/leaderboard", response_class=HTMLResponse)
async def get_leaderboard(
    sort_by: str = Query(default="points"),
    sort_order: str = Query(default="desc"), 
):
    with Session(engine) as session:
        points_expr = (Team.wins * 2) + Team.draws
        
        sort_map = {
            "team_name": Team.team_name,
            "group": Team.group,
            "games": Team.games,
            "points" : points_expr,
            "wins": Team.wins,
            "draws": Team.draws,
            "losses": Team.losses,
            "goals_for": Team.goals_for,
            "goals_against": Team.goals_against
        }
        
        field = sort_map.get(sort_by, points_expr)

        query = select(Team)
        if sort_order == "asc":
            query = query.order_by(field.asc())
        else:
            query = query.order_by(field.desc())
            
        teams = session.exec(query).all()
        
        # PASS THE SORT_BY VARIABLE HERE:
        return generate_team_rows(teams, sort_by)

# -------------------------------------------------------
# PLAYERS STATS
# -------------------------------------------------------

@app.get("/playerStats", response_class=HTMLResponse)
async def get_player_stats(
    sort_by: str = Query(default="points"),
    sort_order: str = Query(default="desc"),
):
    with Session(engine) as session:
        query = (
            select(PlayerStats)
            .join(Player, PlayerStats.player_id == Player.player_id)
            .join(Team, Player.team_id == Team.team_id)
        )
        
        points_expr = PlayerStats.goals + PlayerStats.assists

        sort_map = {
            "name": Player.name,
            "team": Team.team_name,
            # "played_games": PlayerStats.played_games,
            "points" : points_expr,
            "goals": PlayerStats.goals,
            "assists": PlayerStats.assists,
            "penalty_min": PlayerStats.penalty_min,
            "stick": Player.lefthanded,
            "primary_pos": Player.primary_pos
        }
        
        field = sort_map.get(sort_by, points_expr)

        if sort_order == "asc":
            query = query.order_by(field.asc())
        else:
            query = query.order_by(field.desc())
        
        stats_list = session.exec(query).all()
        
        # PASS THE SORT_BY VARIABLE HERE:
        return generate_stats_rows(stats_list, sort_by)
        
def generate_stats_rows(stats_list, sort_by="points"):
    rows = ""
    def get_cls(col): 
        return ' class="active-sort-cell"' if sort_by == col else ""

    for i, stats_entry in enumerate(stats_list, 1):
        player = stats_entry.player
        team = player.team 
        stick_display = "L" if player.lefthanded else "R"
        image = player.image_url or "profile.png"
        team_logo = team.logo_url or "/logos/logo_default.png"
        
        rows += f"""
            <tr class="tbody-tr">
                <td>{i}</td>
                <td{get_cls('name')}>
                    <div class="player-container"">
                        <div class="player-img-container">
                            <img src="/photos/{image}">
                        </div>
                        <span>{player.name}</span>
                    </div>
                </td>
                <td{get_cls('team')}>
                    <div class="team-img-td">
                        <svg width="35px" height="35px">
                            <use class="team-img" href="{team_logo}"></use>
                        </svg>
                    </div>
                </td>
                
                <!-- <td{get_cls('played_games')}>{stats_entry.played_games}</td> -->

                <td{get_cls('points')}>{stats_entry.goals + stats_entry.assists}</td>
                <td{get_cls('goals')}>{stats_entry.goals}</td>
                <td{get_cls('assists')}>{stats_entry.assists}</td>
                <td{get_cls('penalty_min')}>{stats_entry.penalty_min}</td>
                <td{get_cls('stick')}>{stick_display}</td>
                <td{get_cls('primary_pos')}>{player.primary_pos}</td>
            </tr>
        """
    return rows



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
    sort_by: str = Query(default="team_id"),
    sort_order: str = Query(default="asc"),
):
    with Session(engine) as session:
        # Join Player and Team to access logo and team name
        query = select(Player).join(Team, Player.team_id == Team.team_id)

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
            "team_id" : Team.team_name, # Improved sorting
            "primary_pos": Player.primary_pos,
            "secondary_pos": Player.secondary_pos,
            "stick": Player.lefthanded,
            "age": Player.age,
            "experience": Player.experience,
            "playstyle": Player.playstyle,
            "licenced": Player.licenced,
            "recruiter": Player.recruiter
        }
        
        field = sort_map.get(sort_by, Team.team_name)

        if sort_order == "asc":
            query = query.order_by(field.asc())
        else:
            query = query.order_by(field.desc())
        
        players = session.exec(query).all()
        
        if not players:
            return """<tr><td colspan="11" style="text-align:left; padding: 20px;">
                      Mikään pelaaja ei vastannut hakua.</td></tr>"""

        # Generate rows with team logos
        rows = ""
        for player in players:
            # Helper to check which column gets the highlight class
            def get_cls(col_name):
                return ' class="active-sort-cell"' if sort_by == col_name else ""

            team = player.team
            stick_display = "L" if player.lefthanded else "R"
            licenced_display = "✓" if player.licenced else "X"
            image = player.image_url or "profile.png"
            team_logo = team.logo_url or "/logos/logo_default.png"
            
            rows += f"""
                <tr class="tbody-tr">
                    <td{get_cls('name')}>
                        <div class="player-container">
                            <div class="player-img-container"><img src="/photos/{image}"></div>
                            <span>{player.name}</span>
                        </div>
                    </td>
                    <td{get_cls('shirt_number')}>{player.shirt_number or "-"}</td>
                    <td{get_cls('team_id')}>
                        <div class="team-img-td">
                            <svg width="35px" height="35px"><use href="{team_logo}"></use></svg>
                        </div>
                    </td>
                    <td{get_cls('primary_pos')}>{player.primary_pos or "-"}</td>
                    <td{get_cls('secondary_pos')}>{player.secondary_pos or "-"}</td>
                    <td{get_cls('stick')}>{stick_display}</td>
                    <td{get_cls('age')}>{player.age}</td>
                    <td{get_cls('experience')}>{player.experience}</td>
                    <td{get_cls('playstyle')}>{player.playstyle or "-"}</td>
                    <td{get_cls('licenced')}>{licenced_display}</td>
                    <td{get_cls('recruiter')}>{player.recruiter or "Toimitsijat"}</td>
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
