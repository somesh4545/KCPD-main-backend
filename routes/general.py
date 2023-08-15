from fastapi import APIRouter, status, HTTPException, Response
from models.index import PLAYERS, DOCUMENTS, TEAMS, TEAM_PLAYERS, USERS
from schemas.index import Player, Document, Login, Teams, TeamPlayers,GenericResponseModel
from sqlalchemy.orm import Session, joinedload, load_only
from fastapi import Depends
from config.db import get_db
from utils.jwt import  get_current_user
from uuid import uuid4
from sqlalchemy import and_
from service.index import Tournament_Game_Service
import http
from utils.general import model_to_dict


generalRouter = APIRouter()

@generalRouter.get('/fixture/{fixture_id}')
async def get_fixture_by_id(fixture_id:int,user_id: str=Depends(get_current_user), db: Session = Depends(get_db)):
    return Tournament_Game_Service(db).get_fixture_by_id(fixture_id, user_id)

# @generalRouter.get('/team/{team_id}')
# async def get_team_by_id(team_id: str, user_id: str=Depends(get_current_user), db: Session = Depends(get_db)):
#     team = db.query(TEAMS).options(
#         joinedload(TEAMS.admin).load_only(USERS.first_name, USERS.email_id),
#         joinedload(TEAMS.team_players).load_only(TEAM_PLAYERS.id).joinedload(TEAM_PLAYERS.player).load_only(USERS.first_name, USERS.email_id)
#     ).filter(TEAMS.id == team_id).first()
#     if team is None:
#         return GenericResponseModel(status='error', message='Invalid team id passed', status_code=http.HTTPStatus.BAD_REQUEST)

#     return {'status': 'success', 'message': 'Team details', 'status_code': http.HTTPStatus.OK, 'data': team}
