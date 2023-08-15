from fastapi import APIRouter, Query
from models.index import ORGANIZERS, TOURNAMENT
from schemas.index import Organizer, Tournament,GenericResponseModel
from sqlalchemy.orm import Session, joinedload
from fastapi import Depends
from config.db import get_db
from utils.jwt import  get_current_user
from uuid import uuid4
from sqlalchemy import and_, select
from uuid import uuid4
from utils.general import model_to_dict
import http
from service.index import TournamentService, Tournament_Game_Service

#routes
tournamentRouter = APIRouter()

# @organizerRouter.get('/')
# async def fetch_all_org(db: Session = Depends(get_db)):
#     return  db.query(ORGANIZERS).all()

# @tournamentRouter.post('/')
# async def create_new_tournament(tournament: Tournament,user_id: str = Depends(get_current_user), db: Session = Depends(get_db))->GenericResponseModel:
#     return TournamentService(db).create_tournament(tournament)

@tournamentRouter.get('/')
async def get_tournaments(page: int = Query(0, ge=0), limit: int = Query(5, le=100),user_id: str = Depends(get_current_user), db: Session = Depends(get_db))->GenericResponseModel:
    return TournamentService(db).get_tournaments(page, limit)

@tournamentRouter.get('/{tournament_id}')
async def get_tournament_by_id(tournament_id: str, user_id: str=Depends(get_current_user), db: Session=Depends(get_db)):
    return TournamentService(db).get_tournament_by_id(tournament_id)

@tournamentRouter.get('/{tournament_id}/games')
async def get_tournament_games(tournament_id: str,user_id: str = Depends(get_current_user),  db: Session = Depends(get_db))->GenericResponseModel:
    response = TournamentService(db).get_tournament_games(tournament_id, user_id)
    return response

@tournamentRouter.get('/tournament/{tournament_id}/games/{tournament_game_id}/fixtures/')
async def get_fixtures(tournament_id:str, tournament_game_id: str, game_id:int, user_id: str=Depends(get_current_user), db: Session=Depends(get_db)):
    return Tournament_Game_Service(db).get_fixtures(tournament_id, tournament_game_id, game_id, user_id)
