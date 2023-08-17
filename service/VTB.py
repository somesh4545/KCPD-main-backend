# service class for 3 games
# volleyball tt badminton 
# all the services function related to that



from schemas.index import GenericResponseModel, Vtb
from models.index import TEAMS, VTB,FIXTURES, USERS
from sqlalchemy.orm import Session, joinedload, load_only
from sqlalchemy import and_, or_
import shortuuid
from utils.general import model_to_dict
import http
from typing import List


class VTB_Serivce():

    def __init__(self, db: Session):
        self.db = db


    
    def get_score(self, fixture_id):
        details = self.db.query(VTB).options(
            joinedload(VTB.team).load_only(TEAMS.name),
            joinedload(VTB.scorer).load_only(USERS.first_name, USERS.profile_url),
            load_only(VTB.points, VTB.created_at)
        ).filter(VTB.fixture_id==fixture_id).order_by(VTB.created_at).all()
        if details is None:
            return GenericResponseModel(status='error', message='Invalid details passed', status_code=http.HTTPStatus.BAD_REQUEST)
        teamWinner = self.db.query(FIXTURES).options(
            load_only(FIXTURES.winner_id),
            joinedload(FIXTURES.winner).load_only(TEAMS.name)
        ).filter(and_(FIXTURES.id==fixture_id, FIXTURES.winner_id!=None)).first()
        winner = None if teamWinner is None else teamWinner
        return {'status': 'success', 'message': "Fixtures found", 'status_code': http.HTTPStatus.OK, 
                'data': {'winner': winner,  'match_details':details}}
        


    
    # add score
    def add_score(self, fixture_id: int, vtbs: Vtb):
        check = self.db.query(FIXTURES).filter(FIXTURES.id==fixture_id).first()
        if check is None:
            return GenericResponseModel(status='error', message='Invalid details passed', status_code=http.HTTPStatus.BAD_REQUEST)
        result = []
        vtb_objs = [VTB(**v.dict()) for v in vtbs]
        self.db.add_all(vtb_objs)
        self.db.commit()
        result = [model_to_dict(vtb_obj) for vtb_obj in vtb_objs]
        return GenericResponseModel(status='success', data=result, message="Successfully saved", status_code=http.HTTPStatus.OK)

    
    
    def delete_score(self, fixture_id, point_ids: int):
        check = self.db.query(FIXTURES).filter(FIXTURES.id==fixture_id).first()
        if check is None:
            return GenericResponseModel(status='error', message='Invalid details passed', status_code=http.HTTPStatus.BAD_REQUEST)
        
        self.db.query(VTB).filter(VTB.id.in_(point_ids)).delete(synchronize_session=False)
        self.db.commit()
        return GenericResponseModel(status='success', message="Successfully deleted", status_code=http.HTTPStatus.OK)

