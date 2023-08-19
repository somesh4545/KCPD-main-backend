from fastapi import APIRouter, status, HTTPException, Response
from models.index import GAMES
from schemas.index import GenericResponseModel, Vtb, Football_Goals,Football_Cards,Football_Shootout,Football_Time
from sqlalchemy.orm import Session, joinedload, load_only
from fastapi import Depends
from config.db import get_db
from utils.jwt import  get_current_user
from uuid import uuid4
from sqlalchemy import and_
from service.index import Tournament_Game_Service, VTB_Serivce, FOOTBALL_Serivce
import http
from utils.general import model_to_dict
from typing import List


fixturesRouter = APIRouter()

@fixturesRouter.get('/id/{fixture_id}')
async def get_fixture_by_id(fixture_id:int,user_id: str=Depends(get_current_user), db: Session = Depends(get_db)):
    return Tournament_Game_Service(db).get_fixture_by_id(fixture_id, user_id)



# routes related to volleyball, tt, badminton scores
vtbRouter = APIRouter()
@vtbRouter.get('/id/{fixture_id}/score')
async def get_score_vtb(fixture_id: int, db: Session = Depends(get_db)):
    response = VTB_Serivce(db).get_score(fixture_id)
    return response


@vtbRouter.post('/id/{fixture_id}/score')
async def vtb_add_score_vtb(vtb: List[Vtb], fixture_id: int, user_id: str=Depends(get_current_user), db: Session = Depends(get_db)):
    response = VTB_Serivce(db).add_score(fixture_id, vtb)
    return response
    

@vtbRouter.delete('/id/{fixture_id}/score')
async def vtb_delete_score_vtb(point_ids: List[int], fixture_id: int, user_id: str=Depends(get_current_user), db: Session = Depends(get_db)):
    return VTB_Serivce(db).delete_score(fixture_id, point_ids)
    

# routes for football
footballRouter = APIRouter()
@footballRouter.get('/id/{fixture_id}/score')
async def get_football_score(fixture_id: int,  db: Session = Depends(get_db)):
    response = FOOTBALL_Serivce(db).get_details(fixture_id)
    return response

@footballRouter.post('/id/{fixture_id}/goal')
async def add_goal(goal: Football_Goals, fixture_id: int, user_id: str=Depends(get_current_user), db: Session = Depends(get_db)):
    response = FOOTBALL_Serivce(db).add_goal(goal,fixture_id)
    return response

@footballRouter.delete('/id/{fixture_id}/goal')
async def delete_goal(goal_id: int, fixture_id: int, user_id: str=Depends(get_current_user), db: Session = Depends(get_db)):
    response = FOOTBALL_Serivce(db).delete_goal(goal_id,fixture_id)
    return response


@footballRouter.post('/id/{fixture_id}/card')
async def give_card(card: Football_Cards, fixture_id: int, user_id: str=Depends(get_current_user), db: Session = Depends(get_db)):
    response = FOOTBALL_Serivce(db).give_card(card,fixture_id)
    return response



@footballRouter.post('/id/{fixture_id}/shootout')
async def add_shootout(shootout:Football_Shootout, fixture_id: int, user_id: str=Depends(get_current_user), db: Session = Depends(get_db)):
    response = FOOTBALL_Serivce(db).add_shootout(shootout,fixture_id)
    return response


@footballRouter.delete('/id/{fixture_id}/shootout')
async def delete_shootout(shootout_id: int, fixture_id: int, user_id: str=Depends(get_current_user), db: Session = Depends(get_db)):
    response = FOOTBALL_Serivce(db).delete_shootout(shootout_id,fixture_id)
    return response


@footballRouter.post('/id/{fixture_id}/time')
async def add_time_halfs(time_halfs: Football_Time, fixture_id: int, user_id: str=Depends(get_current_user), db: Session = Depends(get_db)):
    response = FOOTBALL_Serivce(db).add_time_halfs(time_halfs,fixture_id)
    return response

