from fastapi import APIRouter, status, HTTPException, Response
from models.index import ORGANIZERS, DOCUMENTS, USERS
from schemas.index import Organizer, Document, Login
from sqlalchemy.orm import Session 
from fastapi import Depends
from config.db import get_db
from utils.jwt import get_hashed_password, verify_password, create_refresh_token, create_access_token, get_current_user
from sqlalchemy import and_, or_
from utils.jwt import get_hashed_password, verify_password, create_refresh_token, create_access_token, get_current_user


adminRouter = APIRouter()

# @adminRouter.get('/')
# async def fetch_all_org(db: Session = Depends(get_db)):
#     return  db.query(ORGANIZERS).all()

@adminRouter.post('/login')
async def admin_login(data: Login, response: Response, db:Session=Depends(get_db)):
    if data.email_id=="admin" and data.password=="this this":
        return {
            'status': 'success',
            'message': 'login successfully',
            'token': create_access_token("admin")
        }
    else:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Incorrect details"
        )
    
# getting player and organizers documents to verifiy
@adminRouter.get('/documents')
async def get_new_documents(db:Session=Depends(get_db)):
    documents = db.query(DOCUMENTS).filter(DOCUMENTS.verified==False).all()

    return {
        'status': 'success',
        'message': 'found applications',
        'data': documents
    }

# approving documents and if all documents are verified then verify their account
@adminRouter.post('/documents')
async def approve_document( document_id: int, is_approve: bool, user_id:str, db:Session=Depends(get_db) ):
    # check the validity of doc id with that in database
    document = db.query(DOCUMENTS).filter(DOCUMENTS.id == document_id).first()
    if document is None:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid document id provided"
        )
    user = db.query(USERS).filter(USERS.id==user_id).first()
    
    if is_approve:
        document.verified = 1
        # check if any pending document of that user
        count = db.query(DOCUMENTS).filter(and_(DOCUMENTS.user_id==user_id, or_( DOCUMENTS.verified==0, DOCUMENTS.verified==-1 ))).count()
        if count == 0:
            user.verified = True
    else:
        user.verified = False
        document.verified = -1

    
    db.add(user)

    db.add(document)
    db.commit()

    return {
        'status': 'success',
        'message': 'documents verified',
    }