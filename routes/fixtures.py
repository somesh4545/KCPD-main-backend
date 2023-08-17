from fastapi import APIRouter, status, HTTPException, Response
from models.index import GAMES
from schemas.index import GenericResponseModel, Vtb
from sqlalchemy.orm import Session, joinedload, load_only
from fastapi import Depends
from config.db import get_db
from utils.jwt import  get_current_user
from uuid import uuid4
from sqlalchemy import and_
from service.index import Tournament_Game_Service, VTB_Serivce
import http
from utils.general import model_to_dict
from typing import List


fixturesRouter = APIRouter()

@fixturesRouter.get('/id/{fixture_id}')
async def get_fixture_by_id(fixture_id:int,user_id: str=Depends(get_current_user), db: Session = Depends(get_db)):
    return Tournament_Game_Service(db).get_fixture_by_id(fixture_id, user_id)



# routes related to volleyball, tt, badminton scores

@fixturesRouter.get('/id/{fixture_id}/VTB/score')
async def get_score_vtb(fixture_id: int, db: Session = Depends(get_db)):
    response = VTB_Serivce(db).get_score(fixture_id)
    return response


@fixturesRouter.post('/id/{fixture_id}/VTB/score')
async def vtb_add_score_vtb(vtb: List[Vtb], fixture_id: int, user_id: str=Depends(get_current_user), db: Session = Depends(get_db)):
    response = VTB_Serivce(db).add_score(fixture_id, vtb)
    return response
    

@fixturesRouter.delete('/id/{fixture_id}/VTB/score')
async def vtb_delete_score_vtb(point_ids: List[int], fixture_id: int, user_id: str=Depends(get_current_user), db: Session = Depends(get_db)):
    return VTB_Serivce(db).delete_score(fixture_id, point_ids)
    
