from fastapi import APIRouter, status, HTTPException, Response
from models.index import ORGANIZERS, DOCUMENTS
from schemas.index import Organizer, Document, Login
from sqlalchemy.orm import Session 
from fastapi import Depends
from config.db import get_db
from utils.jwt import get_hashed_password, verify_password, create_refresh_token, create_access_token, get_current_user
from uuid import uuid4
from sqlalchemy import and_, select
from uuid import uuid4

# from fastapi_pagination import LimitOffsetPage, Page
# from fastapi_pagination.ext.sqlalchemy import paginate


#routes
organizerRouter = APIRouter()

@organizerRouter.get('/')
async def fetch_all_org(db: Session = Depends(get_db)):
    return  db.query(ORGANIZERS).all()

@organizerRouter.get('/{orgMail}')
async def fetch_org_by_mail(orgMail, db: Session = Depends(get_db)):
    organizer = db.query(ORGANIZERS).filter(ORGANIZERS.email_id == orgMail).first()
    if organizer is None:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Organizer not found"
        )
    return organizer

# login functionality with access token creation
@organizerRouter.post('/login')
async def organizer_login(data: Login, response: Response, db: Session=Depends(get_db)):
    organizer = db.query(ORGANIZERS).filter(ORGANIZERS.email_id == data.email_id).first()
    if organizer is None:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Incorrect email or password"
        )

    hashed_pass = organizer.password
    if not verify_password(data.password, hashed_pass):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Incorrect email or password"
        )
    
    response.set_cookie(key="access_token", value=create_access_token(organizer.email_id))
    response.set_cookie(key="refresh_token", value=create_refresh_token(organizer.email_id))
    response.set_cookie(key="user_type", value="organizer")
    
    return {
        'status': 'success',
        'message': 'login successfully',
        'data': organizer
    }

# adding new org to db
@organizerRouter.post('/register')
async def add_new_organizer(organizer: Organizer, db: Session = Depends(get_db)):

    #check if organizer with same email exists
    user = db.query(ORGANIZERS).filter(ORGANIZERS.email_id == organizer.email_id).first()
    if user is not None:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Organizer with this email already exist"
        )

    organizer.password = get_hashed_password(organizer.password)
    
    newOrganizer = ORGANIZERS( **dict(organizer))
    newOrganizer.id = uuid4().hex[:10]
    db.add(newOrganizer)  
    db.commit()
    return {
        'status': 'success',
        'message': 'Organizer added successfully'
    }


# update certain fields of the organizer
@organizerRouter.patch("/details")
async def organizer_update(user: str = Depends(get_current_user), updated_data: dict = {}, db: Session=Depends(get_db)):
    organizer = db.query(ORGANIZERS).filter(ORGANIZERS.email_id == user).first()
    if organizer is None:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Organizer not found"
        )

    for key, value in updated_data.items():
        setattr(organizer, key, value)

    db.add(organizer)
    db.commit()
    return {
        'status': 'success',
        'message': 'Organizer updated successfully'
    }

# uploading document of organizer
@organizerRouter.post('/document')
async def organizer_documents_upload(document: Document, user: str=Depends(get_current_user), db:Session=Depends(get_db)):
    organizer = db.query(ORGANIZERS).filter(ORGANIZERS.email_id == user).first()
    if organizer is None:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Organizer not found"
        )
    
    organizer.verified = False
    newDoc = DOCUMENTS(**dict(document))
    db.add(organizer)
    db.add(newDoc)
    db.commit()

    return {
        'status': 'success',
        'message': 'Organizer documents uploaded successfully'
    }

# get uploaded documents of the organizer
@organizerRouter.get('/document')
async def organizer_documents_upload( user: str=Depends(get_current_user), db:Session=Depends(get_db)):
    organizer = db.query(ORGANIZERS).filter(ORGANIZERS.email_id == user).first()
    if organizer is None:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Organizer not found"
        )
    
    documents = db.query(DOCUMENTS).filter(and_(DOCUMENTS.user_type=='organizer', DOCUMENTS.user_id==organizer.id)).all()

    return {
        'status': 'success',
        'message': 'Data found',
        'data': documents
    }
