from fastapi import APIRouter, status, HTTPException, Response
from models.index import PLAYERS, DOCUMENTS, TEAMS, TEAM_PLAYERS, USERS
from schemas.index import Player, Document, Login, Teams, TeamPlayers,GenericResponseModel
from sqlalchemy.orm import Session, joinedload, load_only
from fastapi import Depends
from config.db import get_db
from utils.jwt import  get_current_user
from uuid import uuid4
from sqlalchemy import and_
from service.index import TournamentService,PLAYERS_Serivce
import http
from utils.general import model_to_dict


playersRouter = APIRouter()

@playersRouter.get('/')
async def fetch_all_players(db: Session = Depends(get_db)):
    return db.query(PLAYERS).all()

# @playersRouter.post('/plays')
# async def add_plays(game: str, user_id: str, db: Session = Depends(get_db)):
#     pass

@playersRouter.post('/create_team')
async def join_game(team: Teams, user_id: str=Depends(get_current_user), db: Session = Depends(get_db)):
    return TournamentService(db).create_team(team, user_id)
    
@playersRouter.post('/join_team')
async def join_team(team: Teams,  team_id: str, user_id: str=Depends(get_current_user), db: Session = Depends(get_db)):
    return TournamentService(db).join_team(team, team_id, user_id)
    
@playersRouter.get('/team/{team_id}')
async def get_team_by_id(team_id: str, user_id: str=Depends(get_current_user), db: Session = Depends(get_db)):
    team = db.query(TEAMS).options(
        load_only(TEAMS.admin_id, TEAMS.createdAt, TEAMS.no_of_boys, TEAMS.no_of_girls),
        joinedload(TEAMS.admin).load_only(USERS.first_name, USERS.email_id, USERS.profile_url, USERS.last_name, USERS.dob, USERS.gender),
        joinedload(TEAMS.team_players).load_only(TEAM_PLAYERS.id).joinedload(TEAM_PLAYERS.player).load_only(USERS.first_name, USERS.email_id, USERS.profile_url, USERS.last_name, USERS.dob, USERS.gender),
    ).filter(TEAMS.id == team_id).first()
    if team is None:
        return GenericResponseModel(status='error', message='Invalid team id passed', status_code=http.HTTPStatus.BAD_REQUEST)

    return {'status': 'success', 'message': 'Team details', 'status_code': http.HTTPStatus.OK, 'data': team}


@playersRouter.get('/previous_participation')
async def get_previous_participation( user_id: str=Depends(get_current_user), db: Session = Depends(get_db)):
    response = PLAYERS_Serivce(db).get_previous_participation(user_id)
    return response


# to check if user has any umpiring duty
@playersRouter.get('/umpiring_task')
async def get_umpiring_tasks( user_id: str=Depends(get_current_user), db: Session = Depends(get_db)):
    response = PLAYERS_Serivce(db).get_umpiring_tasks(user_id)
    return response