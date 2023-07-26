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
