from fastapi import APIRouter, status, HTTPException, Response
from models.index import ORGANIZERS, DOCUMENTS, USERS
from schemas.index import Organizer, Document, Login, User
from sqlalchemy.orm import Session 
from fastapi import Depends
from config.db import get_db
from utils.jwt import get_hashed_password, verify_password, create_refresh_token, create_access_token, get_current_user
from uuid import uuid4
from sqlalchemy import and_, or_, select
from uuid import uuid4
import shortuuid

# from fastapi_pagination import LimitOffsetPage, Page
# from fastapi_pagination.ext.sqlalchemy import paginate


#routes
userRouter = APIRouter()

@userRouter.get('/')
async def fetch_all_users(db: Session = Depends(get_db)):
    return  db.query(USERS).all()

# @userRouter.get('/{userMail}')
# async def fetch_user_by_mail(orgMail, db: Session = Depends(get_db)):
#     user = db.query(USERS).filter(USERS.email_id == orgMail).first()
#     if user is None:
#         raise HTTPException(
#             status_code=status.HTTP_400_BAD_REQUEST,
#             detail="user not found"
#         )
#     return user

# login functionality with access token creation
@userRouter.post('/login')
async def user_login(data: Login, response: Response, db: Session=Depends(get_db)):
    user = db.query(USERS).filter(USERS.email_id == data.email_id).first()
    if user is None:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Incorrect email or password"
        )

    hashed_pass = user.password
    if not verify_password(data.password, hashed_pass):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Incorrect email or password"
        )
    
    
    
    return {
        'status': 'success',
        'message': 'login successfully',
        'data': user,
        'access_token': create_access_token(user.email_id)
    }

# adding new org to db
@userRouter.post('/register')
async def add_new_user(user: User, db: Session = Depends(get_db)):

    #check if organizer with same email exists
    user_check = db.query(USERS).filter(or_(USERS.email_id == user.email_id, USERS.phone_no==user.phone_no)).first()
    if user_check is not None:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="User with this email or phone already exist"
        )

    user.password = get_hashed_password(user.password)
    
    newOrganizer = USERS( **dict(user))
    newOrganizer.id = shortuuid.uuid()[:10]
    db.add(newOrganizer)  
    db.commit()
    return {
        'status': 'success',
        'message': 'User added successfully'
    }


# update certain fields of the organizer
@userRouter.patch("/details")
async def user_update(user: str = Depends(get_current_user), updated_data: dict = {}, db: Session=Depends(get_db)):
    user = db.query(USERS).filter(USERS.email_id == user).first()
    if user is None:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="User not found"
        )

    for key, value in updated_data.items():
        setattr(user, key, value)

    db.add(user)
    db.commit()
    return {
        'status': 'success',
        'message': 'User updated successfully',
        'data': user
    }

# uploading document of organizer
@userRouter.post('/document')
async def user_documents_upload(document: Document, user: str=Depends(get_current_user), db:Session=Depends(get_db)):
    user = db.query(USERS).filter(and_(USERS.email_id == user, USERS.id==document.user_id)).first()
    if user is None:
        raise HTTPException(
            status_code=status.HTTP_404_BAD_REQUEST,
            detail="user not found"
        )
    
    #checking if already is there is any document if yes only update it
    prevDoc = db.query(DOCUMENTS).filter(and_( DOCUMENTS.user_id==user.id, DOCUMENTS.document_type==document.document_type)).first()
    if prevDoc is not None:
        prevDoc.document_url = document.document_url
        user.verified = False
        db.add(user)
        db.add(prevDoc)
    else:
        user.verified = False
        db.add(user)
        newDoc = DOCUMENTS(**dict(document))
        db.add(newDoc)
    
    db.commit()

    return {
        'status': 'success',
        'message': 'users documents uploaded successfully'
    }

# get uploaded documents of the users
@userRouter.get('/document')
async def user_documents_upload( user: str=Depends(get_current_user), db:Session=Depends(get_db)):
    user = db.query(USERS).filter(USERS.email_id == user).first()
    if user is None:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="User not found"
        )
    
    documents = db.query(DOCUMENTS).filter(DOCUMENTS.user_id==user.id).all()

    return {
        'status': 'success',
        'message': 'Data found',
        'data': documents
    }
