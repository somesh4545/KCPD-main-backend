from fastapi import APIRouter, status, HTTPException, Response
from models.index import ORGANIZERS, TOURNAMENT
from schemas.index import Organizer, Tournament,GenericResponseModel, Tournament_Games
from sqlalchemy.orm import Session 
from fastapi import Depends
from config.db import get_db
from utils.jwt import  get_current_user
from uuid import uuid4
from sqlalchemy import and_, select
from uuid import uuid4
from service.tournament import TournamentService

# from fastapi_pagination import LimitOffsetPage, Page
# from fastapi_pagination.ext.sqlalchemy import paginate


#routes
organizerRouter = APIRouter()

# @organizerRouter.get('/')
# async def fetch_all_org(db: Session = Depends(get_db)):
#     return  db.query(ORGANIZERS).all()

@organizerRouter.post('/tournament')
async def create_new_tournament(tournament: Tournament,user_id: str = Depends(get_current_user), db: Session = Depends(get_db))->GenericResponseModel:
    response = TournamentService(db).create_tournament(tournament)
    db.commit()
    return response

@organizerRouter.patch('/tournament/{tournament_id}')
async def update_tournament(tournament_id: str,user_id: str = Depends(get_current_user),tournament: dict={},  db: Session = Depends(get_db))->GenericResponseModel:
    return TournamentService(db).update_tournament(tournament, tournament_id, user_id)

@organizerRouter.post('/tournament/{tournament_id}/games')
async def add_games_to_tournament(game: Tournament_Games,tournament_id: str,user_id: str = Depends(get_current_user),  db: Session = Depends(get_db))->GenericResponseModel:
    response = TournamentService(db).add_game(game, tournament_id, user_id)
    db.commit()
    return response

@organizerRouter.patch('/tournament/{tournament_id}/games')
async def update_game(game_id: str,user_id: str = Depends(get_current_user),game: dict={},  db: Session = Depends(get_db))->GenericResponseModel:
    return TournamentService(db).update_game(game, game_id, user_id)