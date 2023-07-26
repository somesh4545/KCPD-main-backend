from fastapi import APIRouter, status, HTTPException, Response
from models.index import PLAYERS, DOCUMENTS
from schemas.index import Player, Document, Login
from sqlalchemy.orm import Session 
from fastapi import Depends
from config.db import get_db
from utils.jwt import get_hashed_password, verify_password, create_refresh_token, create_access_token, get_current_user
from uuid import uuid4
from sqlalchemy import and_

playersRouter = APIRouter()

@playersRouter.get('/')
async def fetch_all_players(db: Session = Depends(get_db)):
    return db.query(PLAYERS).all()

@playersRouter.post('/plays')
async def add_plays(game: str, user_id: str, db: Session = Depends(get_db)):
    pass