# Description: Data Access Object (DAO) for Player model
# player_dao.py

from sqlalchemy.orm import Session
from models.player import Player

def get_player(db: Session, player_id: int):
    return db.query(Player).filter(Player.id == player_id).first()

def get_players(db: Session):
    return db.query(Player).all()

def create_player(db: Session, player: Player):
    db.add(player)
    db.commit()
    db.refresh(player)
    return player

def update_player(db: Session, player: Player):
    db.merge(player)
    db.commit()
    return player

def delete_player(db: Session, player_id: int):
    player = db.query(Player).filter(Player.id == player_id).first()
    if player:
        db.delete(player)
        db.commit()
    return player
