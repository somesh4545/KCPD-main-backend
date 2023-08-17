from fastapi import APIRouter, status, HTTPException, Response
from models.index import GAMES
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

@generalRouter.get('/fixture/{fixture_id}')
async def get_fixture_by_id(fixture_id:int,user_id: str=Depends(get_current_user), db: Session = Depends(get_db)):
    return Tournament_Game_Service(db).get_fixture_by_id(fixture_id, user_id)

@generalRouter.get('/get_all_games')
async def get_all_games(db: Session = Depends(get_db)):
    pass
    games = db.query(GAMES).all()

    result = [{'id': g.id, 'text': g.name, 'value': g.name} for g in games]

    return result