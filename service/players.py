from schemas.index import GenericResponseModel, Vtb
from models.index import TEAMS,FIXTURES,TOURNAMENT,GAMES, U_PAST_PARTICIPATION,TOURNAMENT_GAMES,GROUNDS
from sqlalchemy.orm import Session, joinedload, load_only
from sqlalchemy import and_, or_, desc
import shortuuid
from utils.general import model_to_dict
import http
from typing import List


class PLAYERS_Serivce():

    def __init__(self, db: Session):
        self.db = db


    def get_previous_participation(self, user_id: str):
        data = self.db.query(U_PAST_PARTICIPATION).options(
                joinedload(U_PAST_PARTICIPATION.tournament_game).load_only(
                    TOURNAMENT_GAMES.name,TOURNAMENT_GAMES.info,TOURNAMENT_GAMES.start_date,TOURNAMENT_GAMES.end_date, TOURNAMENT_GAMES.game_id 
                ).options(
                    joinedload(TOURNAMENT_GAMES.game).load_only(
                        GAMES.name
                    ),
                    joinedload(TOURNAMENT_GAMES.tournament).load_only(
                        TOURNAMENT.organizer_name, TOURNAMENT.organizer_info,TOURNAMENT.name
                    )
                )
            ).filter(U_PAST_PARTICIPATION.user_id==user_id).order_by(desc(U_PAST_PARTICIPATION.createdAt)).all()
        
        return {'status': 'success', 'data': data, 'message': 'Previous participation', 'status_code':http.HTTPStatus.OK}
        


    def get_umpiring_tasks(self, user_id: str):
        pass
        data = self.db.query(FIXTURES).options(
                load_only(FIXTURES.match_number, FIXTURES.round_no),
                joinedload(FIXTURES.tournament_game).load_only(TOURNAMENT_GAMES.name),
                joinedload(FIXTURES.game).load_only(GAMES.name),
                joinedload(FIXTURES.team_1).load_only(TEAMS.name),
                joinedload(FIXTURES.team_2).load_only(TEAMS.name),
                joinedload(FIXTURES.winner).load_only(TEAMS.name),
                joinedload(FIXTURES.ground).load_only(GROUNDS.name, GROUNDS.location)
            ).filter(FIXTURES.umpire_id==user_id).all()
        
        if data is None or len(data)==0:
            return {'status': 'success', 'data': [], 'message': 'No tasks related to umpiring', 'status_code':http.HTTPStatus.OK}

        return {'status': 'success', 'message': 'Umpiring tasks (hint if winner is present dont provide button to scoring)',
                 'data': data, 'status_code':http.HTTPStatus.OK}

            