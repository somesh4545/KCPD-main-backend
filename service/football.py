# service class for 3 games
# volleyball tt badminton 
# all the services function related to that



from schemas.index import GenericResponseModel, Vtb, Football_Goals, Football_Cards, Football_Shootout, Football_Time
from models.index import TEAMS, FOOTBALL_GOALS, FOOTBALL_CARDS, FOOTBALL_SHOOTOUT, FOOTBALL_TIME, FIXTURES, USERS, VTB
from sqlalchemy.orm import Session, joinedload, load_only
from sqlalchemy import and_, or_
import shortuuid
from utils.general import model_to_dict
import http
from typing import List


class FOOTBALL_Serivce():

    def __init__(self, db: Session):
        self.db = db


    
    def get_details(self, fixture_id:int):
        pass
        

    # add score
    def add_goal(self, goal: Football_Goals, fixture_id: int):
        check = self.db.query(FIXTURES).filter(FIXTURES.id==fixture_id).first()
        if check is None:
            return GenericResponseModel(status='error', message='Invalid details passed', status_code=http.HTTPStatus.BAD_REQUEST)
        
        obj = FOOTBALL_GOALS(**goal.dict())
        self.db.add(obj)
        self.db.commit()
        return GenericResponseModel(status='success', message='Goal stored', status_code=http.HTTPStatus.OK, data=model_to_dict(obj))
    

    def delete_goal(self, goal_id:int, fixture_id:int):
        check = self.db.query(FIXTURES).filter(FIXTURES.id==fixture_id).first()
        if check is None:
            return GenericResponseModel(status='error', message='Invalid details passed', status_code=http.HTTPStatus.BAD_REQUEST)
        
        self.db.query(FOOTBALL_GOALS).filter(and_(FOOTBALL_GOALS.fixture_id==fixture_id, FOOTBALL_GOALS.id==goal_id)).delete()
        self.db.commit()
        return GenericResponseModel(status='success', message='Goal delete', status_code=http.HTTPStatus.OK)


    def give_card(self, card: Football_Cards, fixture_id: int):
        check = self.db.query(FIXTURES).filter(FIXTURES.id==fixture_id).first()
        if check is None:
            return GenericResponseModel(status='error', message='Invalid details passed', status_code=http.HTTPStatus.BAD_REQUEST)
        obj = FOOTBALL_CARDS(**card.dict())
        self.db.add(obj)
        self.db.commit()
        return GenericResponseModel(status='success', message='Card given', status_code=http.HTTPStatus.OK, data=model_to_dict(obj))
    

    def add_shootout(self, shootout: Football_Shootout,fixture_id: int):
        check = self.db.query(FIXTURES).filter(FIXTURES.id==fixture_id).first()
        if check is None:
            return GenericResponseModel(status='error', message='Invalid details passed', status_code=http.HTTPStatus.BAD_REQUEST)
        obj = FOOTBALL_SHOOTOUT(**shootout.dict())
        self.db.add(obj)
        self.db.commit()
        return GenericResponseModel(status='success', message='Shootout done', status_code=http.HTTPStatus.OK, data=model_to_dict(obj))
    

    def delete_shootout(self, shootout_id:int, fixture_id:int):
        check = self.db.query(FIXTURES).filter(FIXTURES.id==fixture_id).first()
        if check is None:
            return GenericResponseModel(status='error', message='Invalid details passed', status_code=http.HTTPStatus.BAD_REQUEST)
        self.db.query(FOOTBALL_SHOOTOUT).filter(and_(FOOTBALL_SHOOTOUT.fixture_id==fixture_id, FOOTBALL_SHOOTOUT.id==shootout_id)).delete()
        self.db.commit()
        return GenericResponseModel(status='success', message='Shootout delete', status_code=http.HTTPStatus.OK)


    def add_time_halfs(self, time_half:Football_Time, fixture_id:int):
        check = self.db.query(FIXTURES).filter(FIXTURES.id==fixture_id).first()
        if check is None:
            return GenericResponseModel(status='error', message='Invalid details passed', status_code=http.HTTPStatus.BAD_REQUEST)
        obj = FOOTBALL_TIME(**time_half.dict())
        self.db.add(obj)
        self.db.commit()
        return GenericResponseModel(status='success', message='TIme half stored', status_code=http.HTTPStatus.OK, data=model_to_dict(obj))
    