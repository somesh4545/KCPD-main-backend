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
        check = self.db.query(FIXTURES).options(
            load_only(FIXTURES.team_1_id, FIXTURES.team_2_id, FIXTURES.winner_id),
            joinedload(FIXTURES.team_1).load_only(TEAMS.name),
            joinedload(FIXTURES.team_2).load_only(TEAMS.name),
            joinedload(FIXTURES.winner).load_only(TEAMS.name),
        ).filter(and_(FIXTURES.id==fixture_id, FIXTURES.game_id==4)).first()
        if check is None:
            return GenericResponseModel(status='error', message='Invalid details passed check fixture ID or game', status_code=http.HTTPStatus.BAD_REQUEST)

        goals = self.db.query(FOOTBALL_GOALS).options(
            load_only(FOOTBALL_GOALS.team_id, FOOTBALL_GOALS.scored_by, FOOTBALL_GOALS.assist_by, FOOTBALL_GOALS.goal_type, FOOTBALL_GOALS.minute),
            joinedload(FOOTBALL_GOALS.team).load_only(TEAMS.name),
            joinedload(FOOTBALL_GOALS.scorer).load_only(USERS.first_name, USERS.profile_url),
            joinedload(FOOTBALL_GOALS.assist).load_only(USERS.first_name, USERS.profile_url),
        ).filter(FOOTBALL_GOALS.fixture_id==fixture_id).order_by(FOOTBALL_GOALS.minute).all()

        cards = self.db.query(FOOTBALL_CARDS).options(
            load_only(FOOTBALL_CARDS.team_id, FOOTBALL_CARDS.player_id, FOOTBALL_CARDS.reason, FOOTBALL_CARDS.card_type, FOOTBALL_CARDS.minute),
            joinedload(FOOTBALL_CARDS.team).load_only(TEAMS.name),
            joinedload(FOOTBALL_CARDS.player).load_only(USERS.first_name, USERS.profile_url)
        ).filter(FOOTBALL_CARDS.fixture_id==fixture_id).order_by(FOOTBALL_CARDS.minute).all()

        shootouts = self.db.query(FOOTBALL_SHOOTOUT).options(
            load_only(FOOTBALL_SHOOTOUT.team_id, FOOTBALL_SHOOTOUT.player_id, FOOTBALL_SHOOTOUT.number, FOOTBALL_SHOOTOUT.number),
            joinedload(FOOTBALL_SHOOTOUT.team).load_only(TEAMS.name),
            joinedload(FOOTBALL_SHOOTOUT.player).load_only(USERS.first_name, USERS.profile_url)
        ).filter(FOOTBALL_SHOOTOUT.fixture_id==fixture_id).all()

        return {'status': 'success', 'message': "Fixture details", 'status_code': http.HTTPStatus.OK, 'data': {
            'summary': check,
            'goals': goals,
            'cards': cards,
            'shootouts': shootouts
        }}


        

    # add score
    def add_goal(self, goal: Football_Goals, fixture_id: int):
        check = self.db.query(FIXTURES).filter(and_(FIXTURES.id==fixture_id, FIXTURES.game_id==4)).first()
        if check is None:
            return GenericResponseModel(status='error', message='Invalid details passed', status_code=http.HTTPStatus.BAD_REQUEST)
        
        obj = FOOTBALL_GOALS(**goal.dict())
        self.db.add(obj)
        self.db.commit()
        return GenericResponseModel(status='success', message='Goal stored', status_code=http.HTTPStatus.OK, data=model_to_dict(obj))
    

    def delete_goal(self, goal_id:int, fixture_id:int):
        check = self.db.query(FIXTURES).filter(and_(FIXTURES.id==fixture_id, FIXTURES.game_id==4)).first()
        if check is None:
            return GenericResponseModel(status='error', message='Invalid details passed', status_code=http.HTTPStatus.BAD_REQUEST)
        
        self.db.query(FOOTBALL_GOALS).filter(and_(FOOTBALL_GOALS.fixture_id==fixture_id, FOOTBALL_GOALS.id==goal_id)).delete()
        self.db.commit()
        return GenericResponseModel(status='success', message='Goal delete', status_code=http.HTTPStatus.OK)


    def give_card(self, card: Football_Cards, fixture_id: int):        
        check = self.db.query(FIXTURES).filter(and_(FIXTURES.id==fixture_id, FIXTURES.game_id==4)).first()
        if check is None:
            return GenericResponseModel(status='error', message='Invalid details passed', status_code=http.HTTPStatus.BAD_REQUEST)
        obj = FOOTBALL_CARDS(**card.dict())
        self.db.add(obj)
        self.db.commit()
        return GenericResponseModel(status='success', message='Card given', status_code=http.HTTPStatus.OK, data=model_to_dict(obj))
    

    def add_shootout(self, shootout: Football_Shootout,fixture_id: int):
        check = self.db.query(FIXTURES).filter(and_(FIXTURES.id==fixture_id, FIXTURES.game_id==4)).first()
        if check is None:
            return GenericResponseModel(status='error', message='Invalid details passed', status_code=http.HTTPStatus.BAD_REQUEST)
        obj = FOOTBALL_SHOOTOUT(**shootout.dict())
        self.db.add(obj)
        self.db.commit()
        return GenericResponseModel(status='success', message='Shootout done', status_code=http.HTTPStatus.OK, data=model_to_dict(obj))
    

    def delete_shootout(self, shootout_id:int, fixture_id:int):
        check = self.db.query(FIXTURES).filter(and_(FIXTURES.id==fixture_id, FIXTURES.game_id==4)).first()
        if check is None:
            return GenericResponseModel(status='error', message='Invalid details passed', status_code=http.HTTPStatus.BAD_REQUEST)
        self.db.query(FOOTBALL_SHOOTOUT).filter(and_(FOOTBALL_SHOOTOUT.fixture_id==fixture_id, FOOTBALL_SHOOTOUT.id==shootout_id)).delete()
        self.db.commit()
        return GenericResponseModel(status='success', message='Shootout delete', status_code=http.HTTPStatus.OK)


    def add_time_halfs(self, time_half:Football_Time, fixture_id:int):
        check = self.db.query(FIXTURES).filter(and_(FIXTURES.id==fixture_id, FIXTURES.game_id==4)).first()
        if check is None:
            return GenericResponseModel(status='error', message='Invalid details passed', status_code=http.HTTPStatus.BAD_REQUEST)
        obj = FOOTBALL_TIME(**time_half.dict())
        self.db.add(obj)
        self.db.commit()
        return GenericResponseModel(status='success', message='TIme half stored', status_code=http.HTTPStatus.OK, data=model_to_dict(obj))
    