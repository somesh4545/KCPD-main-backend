from schemas.index import GenericResponseModel, Vtb
from models.index import TEAMS, VTB,FIXTURES, USERS
from sqlalchemy.orm import Session, joinedload, load_only
from sqlalchemy import and_, or_
import shortuuid
from utils.general import model_to_dict
import http
from typing import List


class PLAYERS_Serivce():

    def __init__(self, db: Session):
        self.db = db


    def get_previous_participation(userid: str):
        # data = self.db.query()
        pass
        # return {'status': 'success', 'data': data, 'message': 'Previous participation', 'status_code':http.HTTPStatus.OK}
        


    