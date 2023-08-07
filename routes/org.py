from fastapi import APIRouter, status, HTTPException, Response
from models.index import ORGANIZERS, TOURNAMENT, TOURNAMENT_GAMES
from schemas.index import Organizer, Tournament,GenericResponseModel, Tournament_Games, Umpires, Grounds
from sqlalchemy.orm import Session, load_only
from fastapi import Depends
from config.db import get_db
from utils.jwt import  get_current_user
from uuid import uuid4
from sqlalchemy import and_, select
from uuid import uuid4
from service.tournament import TournamentService
import http
from typing import List

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


@organizerRouter.post('/tournament/{tournament_id}/games/{game_id}')
async def add_grounds_umpries(umpires: List[Umpires], grounds: List[Grounds], tournament_id: str, game_id: str, user_id: str=Depends(get_current_user), db: Session = Depends(get_db))->GenericResponseModel:
    response = TournamentService(db).add_grounds_umpries(tournament_id, umpires, grounds, user_id)
    return response


@organizerRouter.get('/tournament/{tournament_id}/games/{tournament_game_id}/teams')
async def get_registered_teams(tournament_id: str, tournament_game_id: str, user_id: str=Depends(get_current_user), db: Session = Depends(get_db))->GenericResponseModel:
    return TournamentService(db).get_registered_teams(tournament_id, tournament_game_id)


## route for approving teams registered for the particular tournament and all
@organizerRouter.post('/tournament/{tournament_id}/games/{tournament_game_id}/teams/verification')
async def teams_approval(tournament_id: str, tournament_game_id: str, team_id: str, approve: bool, user_id: str=Depends(get_current_user), db: Session=Depends(get_db))->GenericResponseModel:
    check1 = db.query(TOURNAMENT).filter(and_(TOURNAMENT.id==tournament_id, TOURNAMENT.organizer_id==user_id)).first()
    print("\n\n",tournament_id,"\n\n")
    if check1 is None:
        return GenericResponseModel(status='error', message='Tournament id incorrect or organizer did not match', status_code=http.HTTPStatus.BAD_REQUEST)
    
    check = db.query(TOURNAMENT_GAMES).options(load_only(TOURNAMENT_GAMES.max_teams)).filter(and_(TOURNAMENT_GAMES.id==tournament_game_id)).first()
    if check is None:
        return GenericResponseModel(status='error', message='Tournament id incorrect or organizer did not match', status_code=http.HTTPStatus.BAD_REQUEST)

    return TournamentService(db).team_verification(tournament_id, tournament_game_id, team_id, approve, check.max_teams)
