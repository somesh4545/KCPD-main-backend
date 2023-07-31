from schemas.index import GenericResponseModel, Tournament
from models.index import TOURNAMENT
from sqlalchemy.orm import Session 
import shortuuid
from utils.general import model_to_dict
import http

class TournamentService():

    def __init__(self, db: Session):
        self.db = db
    
    def create_tournament(self, tournament: Tournament) -> GenericResponseModel:
        t = TOURNAMENT(**tournament.dict())
        t.id = shortuuid.uuid()[:8]
        self.db.add(t)
        self.db.commit()

        # return t0
        # t_dict = {key: value for key, value in t.__dict__.items() if key in t.__table__.columns.keys()}

        return GenericResponseModel(status='success', message='tournament created successfully', data=model_to_dict(t), status_code=http.HTTPStatus.CREATED)