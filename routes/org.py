from fastapi import APIRouter, status, HTTPException, Response
from models.index import ORGANIZERS, TOURNAMENT
from schemas.index import Organizer, Tournament,GenericResponseModel
from sqlalchemy.orm import Session 
from fastapi import Depends
from config.db import get_db
from utils.jwt import get_hashed_password, verify_password, create_refresh_token, create_access_token, get_current_user
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

@organizerRouter.post('/new')
async def create_new_tournament(tournament: Tournament,user_id: str = Depends(get_current_user), db: Session = Depends(get_db))->GenericResponseModel:
    return TournamentService(db).create_tournament(tournament)