from schemas.index import GenericResponseModel, Tournament, Tournament_Games
from models.index import TOURNAMENT, USERS, TOURNAMENT_GAMES
from sqlalchemy.orm import Session, joinedload, load_only
from sqlalchemy import and_
import shortuuid
from utils.general import model_to_dict
import http

class TournamentService():

    def __init__(self, db: Session):
        self.db = db
    

    def create_tournament(self, tournament: Tournament):
        print("\ndata1\n")
        t = TOURNAMENT(**tournament.dict())
        t.id = shortuuid.uuid()[:16]
        self.db.add(t)
        return GenericResponseModel(status='success', message='tournament created successfully', data=model_to_dict(t), status_code=http.HTTPStatus.CREATED)
    

    def update_tournament(self, tournament: Tournament, tournament_id: str, user_id: str) -> GenericResponseModel:
        t = self.db.query(TOURNAMENT).filter(and_(TOURNAMENT.id == tournament_id, TOURNAMENT.organizer_id==user_id)).first()
        
        # print("\ndata4 ", user_id,"\n")
        # print("\ndata4 ", tournament_id,"\n")
        if t is None:
            return GenericResponseModel(status='error', message='Tournament not found or invalid data', status_code=http.HTTPStatus.BAD_REQUEST)
        for key, value in tournament.items():
            setattr(t, key, value)
        self.db.add(t)
        self.db.commit()
        return GenericResponseModel(status='success', message='Tournament details updated', status_code=http.HTTPStatus.ACCEPTED)


    def get_tournaments(self, page: int, limit: int)->GenericResponseModel:
        tournaments = self.db.query(TOURNAMENT).filter(and_(TOURNAMENT.is_active==True, TOURNAMENT.is_payment_done==True)).offset(page*limit).limit(limit).all()
        tournaments_list = [model_to_dict(t) for t in tournaments]

        return GenericResponseModel(status='success', message='Tournament details', data=tournaments_list, status_code=http.HTTPStatus.ACCEPTED)
    
    
    # .options(joinedload(Matches.team_1).load_only(Teams.name), joinedload(Matches.team_2).load_only(Teams.name))
    def get_tournament_by_id(self, tournament_id: str):
        tournament = self.db.query(TOURNAMENT).options(joinedload(TOURNAMENT.organizer).load_only(USERS.first_name, USERS.email_id)).filter(TOURNAMENT.id == tournament_id).first()
        
        if tournament is None:
            return GenericResponseModel(status='error', message='Tournament not found or invalid data', status_code=http.HTTPStatus.BAD_REQUEST)
        return {'status': 'success', 'data': tournament, 'message': 'Tournament details found', 'status_code':http.HTTPStatus.ACCEPTED}
    

    def add_game(self, game: Tournament_Games,tournament_id: str, user_id: str):
        game_obj = TOURNAMENT_GAMES(**game.dict())
        game_obj.id = shortuuid.uuid()[:16]
        self.db.add(game_obj)
        return GenericResponseModel(status='success', message='tournament created successfully', data={'game_id': game_obj.id}, status_code=http.HTTPStatus.CREATED)


    def update_game(self, game: Tournament_Games, game_id: str, user_id: str) -> GenericResponseModel:
        t_g = self.db.query(TOURNAMENT_GAMES).filter(and_(TOURNAMENT_GAMES.id == game_id)).first()
        
        if t_g is None:
            return GenericResponseModel(status='error', message='Tournament game not found or invalid data', status_code=http.HTTPStatus.BAD_REQUEST)
        for key, value in game.items():
            setattr(t_g, key, value)
        self.db.add(t_g)
        self.db.commit()
        return GenericResponseModel(status='success', message='Tournament game details updated', status_code=http.HTTPStatus.ACCEPTED)
