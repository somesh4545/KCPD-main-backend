from fastapi import APIRouter, status, HTTPException
from models.index import ORGANIZERS, DOCUMENTS, PLAYERS
from schemas.index import Organizer, Document
from sqlalchemy.orm import Session 
from fastapi import Depends
from config.db import get_db
from utils.jwt import get_hashed_password, verify_password, create_refresh_token, create_access_token, get_current_user
from sqlalchemy import and_, select
from utils.jwt import get_hashed_password, verify_password, create_refresh_token, create_access_token, get_current_user


adminRouter = APIRouter()

# @adminRouter.get('/')
# async def fetch_all_org(db: Session = Depends(get_db)):
#     return  db.query(ORGANIZERS).all()

@adminRouter.get('/login')
async def admin_login(username:str, password:str, db:Session=Depends(get_db)):
    if username=="admin" and password=="this this":
        
        return {
            'status': 'success',
            'message': 'login successfully',
            "access_token": create_access_token('admin'),
            "refresh_token": create_refresh_token('admin'),
        }
    else:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Incorrect details"
        )
    
# getting player and organizers documents to verifiy
@adminRouter.get('/documents')
async def get_new_documents(user_type: str,db:Session=Depends(get_db)):
    documents = db.query(DOCUMENTS).filter(and_(DOCUMENTS.user_type==user_type, DOCUMENTS.verified==False)).all()

    return {
        'status': 'success',
        'message': 'found '+user_type+' applications',
        'data': documents
    }

# approving documents and if all documents are verified then verify their account
@adminRouter.post('/documents')
async def approve_document(user_type: str, document_id: int, user_id:int, db:Session=Depends(get_db) ):
    # check the validity of doc id with that in database
    document = db.query(DOCUMENTS).filter(and_(DOCUMENTS.id == document_id, DOCUMENTS.user_id==user_id)).first()
    if document is None:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid document id provided"
        )

    document.verified = True

    # check if any pending document of that user
    count = db.query(DOCUMENTS).filter(and_(DOCUMENTS.user_id==user_id, DOCUMENTS.verified==False)).count()

    if count == 0 and user_type=='player':
        player = db.query(PLAYERS).filter(PLAYERS.id==user_id).first()
        player.verified = True
        db.add(player)

    if count == 0 and user_type=='organizer':
        organizer = db.query(ORGANIZERS).filter(ORGANIZERS.id==user_id).first()
        organizer.verified = True
        db.add(organizer)

    db.add(document)
    db.commit()

    return {
        'status': 'success',
        'message': 'documents verified',
    }