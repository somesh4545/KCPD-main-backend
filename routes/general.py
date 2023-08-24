from fastapi import APIRouter, status, HTTPException, Response
from models.index import GAMES, USERS
from schemas.index import GenericResponseModel
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

@generalRouter.get('/get_all_games')
async def get_all_games(db: Session = Depends(get_db)):
    games = db.query(GAMES).all()
    result = [{'id': g.id, 'text': g.name, 'value': g.name} for g in games]
    return result


@generalRouter.get('/validate_user')
async def get_user_id(email_id: str, user_id: str=Depends(get_current_user),db: Session = Depends(get_db)):
    result = db.query(USERS).filter(USERS.email_id==email_id).options(
            load_only(USERS.first_name, USERS.email_id, USERS.profile_url)
        ).first()
    
    if result is None:
        return GenericResponseModel(status='error', message='Invalid email id', status_code=http.HTTPStatus.BAD_REQUEST)

    return GenericResponseModel(status='success', data=model_to_dict(result),message='User found', status_code=http.HTTPStatus.OK)
    