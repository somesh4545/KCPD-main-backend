from fastapi import APIRouter, status, HTTPException, Response
from models.index import PLAYERS, DOCUMENTS
from schemas.index import Player, Document, Login, Teams, TeamPlayers
from sqlalchemy.orm import Session 
from fastapi import Depends
from config.db import get_db
from utils.jwt import  get_current_user
from uuid import uuid4
from sqlalchemy import and_
from service.tournament import TournamentService

playersRouter = APIRouter()

@playersRouter.get('/')
async def fetch_all_players(db: Session = Depends(get_db)):
    return db.query(PLAYERS).all()

@playersRouter.post('/plays')
async def add_plays(game: str, user_id: str, db: Session = Depends(get_db)):
    pass

@playersRouter.post('/create_team')
async def join_game(team: Teams, user_id: str=Depends(get_current_user), db: Session = Depends(get_db)):
    return TournamentService(db).create_team(team, user_id)
    
@playersRouter.post('/join_team')
async def join_team(team_id: str, tournament_id: str, tournament_game_id: str, user_id: str=Depends(get_current_user), db: Session = Depends(get_db)):
    return TournamentService(db).join_team(tournament_id, tournament_game_id, team_id, user_id)
    