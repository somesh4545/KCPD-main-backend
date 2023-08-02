from fastapi import APIRouter, status, HTTPException, Response
from models.index import ORGANIZERS, DOCUMENTS, USERS
from schemas.index import Organizer, Document, Login, User, GenericResponseModel
from sqlalchemy.orm import Session 
from fastapi import Depends
from config.db import get_db
from utils.jwt import get_hashed_password, verify_password, create_refresh_token, create_access_token, get_current_user
from uuid import uuid4
from sqlalchemy import and_, or_, select
from uuid import uuid4
import shortuuid
import http
from utils.general import model_to_dict

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
async def user_login(data: Login, db: Session=Depends(get_db)):
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
        'access_token': create_access_token(user.id)
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
    
    newUser = USERS( **dict(user))
    newUser.id = shortuuid.uuid()[:10]
    db.add(newUser)  
    db.commit()
    return GenericResponseModel(status='success', data=model_to_dict(newUser), message='User added successfully', status_code=http.HTTPStatus.CREATED)


# update certain fields of the organizer
@userRouter.patch("/details")
async def user_update(user_id: str = Depends(get_current_user), updated_data: dict = {}, db: Session=Depends(get_db)):
    user = db.query(USERS).filter(USERS.id == user_id).first()
    if user is None:
        return GenericResponseModel(status='error', message='User not found', status_code=http.HTTPStatus.BAD_REQUEST)


    for key, value in updated_data.items():
        setattr(user, key, value)

    db.add(user)
    db.commit()
    return GenericResponseModel(status='success', data=model_to_dict(user),message='User updated successfully', status_code=http.HTTPStatus.CREATED)


# uploading document of organizer
@userRouter.post('/document')
async def user_documents_upload(document: Document, user_id: str=Depends(get_current_user), db:Session=Depends(get_db)):
    user = db.query(USERS).filter(USERS.id == user_id).first()
    if user is None:
        return GenericResponseModel(status='error', message='User not found', status_code=http.HTTPStatus.BAD_REQUEST)

    
    #checking if already is there is any document if yes only update it
    prevDoc = db.query(DOCUMENTS).filter(and_( DOCUMENTS.user_id==user_id, DOCUMENTS.document_type==document.document_type)).first()
    print("\n")
    print(prevDoc)
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
    print(http.HTTPStatus.CREATED)

    return GenericResponseModel(status='success',message='users documents uploaded successfully', status_code=http.HTTPStatus.CREATED)


# get uploaded documents of the users
@userRouter.get('/document')
async def user_documents_upload( user_id: str=Depends(get_current_user), db:Session=Depends(get_db)):
    user = db.query(USERS).filter(USERS.id == user_id).first()
    if user is None:
        return GenericResponseModel(status='error', message='User not found', status_code=http.HTTPStatus.BAD_REQUEST)

    documents = db.query(DOCUMENTS).filter(DOCUMENTS.user_id==user_id).all()
    # print(user_id)
    document_list = [model_to_dict(doc) for doc in documents]
    return GenericResponseModel(status='success',data=document_list, message='data found successfully', status_code=http.HTTPStatus.CREATED)
    
# to delete certain document 
@userRouter.delete('/document')
async def delete_document( user_id: str=Depends(get_current_user), db:Session=Depends(get_db)):
    return 'will be added in future'