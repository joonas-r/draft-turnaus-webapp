from sqlmodel import Session
from models import Player, PlayerStats
from schemas import PlayerCreate

def create_player(*, session: Session, player_in: PlayerCreate) -> Player:
    player = Player.model_validate(player_in)
    session.add(player)

    session.flush() # draft_players.player_id käytettävissä

    # Luodaan tilasto-entry pelaajalle player_stats.player_id
    stats = PlayerStats(player_id=player.player_id)
    session.add(stats)

    session.commit()
    session.refresh(player)
    return player
