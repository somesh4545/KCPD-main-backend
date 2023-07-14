from fastapi import APIRouter, status, HTTPException
from models.index import PLAYERS, DOCUMENTS
from schemas.index import Player, Document
from sqlalchemy.orm import Session 
from fastapi import Depends
from config.db import get_db
from utils.jwt import get_hashed_password, verify_password, create_refresh_token, create_access_token, get_current_user
from uuid import uuid4
from sqlalchemy import and_

playersRouter = APIRouter()

@playersRouter.get('/')
async def fetch_all_users(db: Session = Depends(get_db)):
    return db.query(PLAYERS).all()

# adding new player to db
@playersRouter.post('/auth')
async def add_new_player(player: Player, db: Session = Depends(get_db)):

    #check if player with same email exists
    user = db.query(PLAYERS).filter(PLAYERS.email_id == player.email_id).first()
    if user is not None:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Player with this email already exist"
        )

    player.password = get_hashed_password(player.password)
    
    newPlayer = PLAYERS( **dict(player))
    newPlayer.id =  uuid4().hex[:10]
    db.add(newPlayer)  
    db.commit()
    return {
        'status': 'success',
        'message': 'Player added successfully'
    }


# login functionality with access token creation
@playersRouter.get('/auth')
async def player_login(email_id: str, password: str, db: Session = Depends(get_db)):
    player = db.query(PLAYERS).filter(PLAYERS.email_id == email_id).first()
    if player is None:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Incorrect email or password"
        )

    hashed_pass = player.password
    if not verify_password(password, hashed_pass):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Incorrect email or password"
        )
    
    return {
        'status': 'success',
        'message': 'login successfully',
        "access_token": create_access_token(player.email_id),
        "refresh_token": create_refresh_token(player.email_id),
    }

# update certain fields of the player
@playersRouter.patch("/auth")
async def player_update(user: str = Depends(get_current_user), updated_data: dict = {}, db: Session=Depends(get_db)):
    player = db.query(PLAYERS).filter(PLAYERS.email_id == user).first()
    if player is None:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Player not found"
        )

    for key, value in updated_data.items():
        setattr(player, key, value)

    db.add(player)
    db.commit()
    return {
        'status': 'success',
        'message': 'Player updated successfully'
    }

# uploading document of player
@playersRouter.post('/document')
async def player_documents_upload(document: Document, user: str=Depends(get_current_user), db:Session=Depends(get_db)):
    player = db.query(PLAYERS).filter(PLAYERS.email_id == user).first()
    if player is None:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Player not found"
        )
    
    #checking if already is there is any document if yes only update it
    prevDoc = db.query(DOCUMENTS).filter(and_(DOCUMENTS.user_type=='player', DOCUMENTS.user_id==player.id, DOCUMENTS.document_type==document.document_type)).first()
    if prevDoc is not None:
        prevDoc.document_url = document.document_url
        player.verified = False
        db.add(player)
        db.add(prevDoc)
    else:
        player.verified = False
        db.add(player)
        newDoc = DOCUMENTS(**dict(document))
    
    db.commit()

    return {
        'status': 'success',
        'message': 'Player documents uploaded successfully/updated'
    }

# get uploaded documents of the player
@playersRouter.get('/document')
async def player_documents_upload( user: str=Depends(get_current_user), db:Session=Depends(get_db)):
    player = db.query(PLAYERS).filter(PLAYERS.email_id == user).first()
    if player is None:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Player not found"
        )
    
    documents = db.query(DOCUMENTS).filter(and_(DOCUMENTS.user_type=='player', DOCUMENTS.user_id==player.id)).all()

    return {
        'status': 'success',
        'message': 'Data found',
        'data': documents
    }

# checking token is valid
@playersRouter.get('/token')
async def check_token(user: str = Depends(get_current_user)):
    return user