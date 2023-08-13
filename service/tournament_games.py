from schemas.index import GenericResponseModel, Tournament, Tournament_Games, Teams, TeamPlayers, Umpires, Grounds
from models.index import TOURNAMENT, USERS, TOURNAMENT_GAMES, TEAMS, TEAM_PLAYERS, UMPIRES, GROUNDS, FIXTURES
from sqlalchemy.orm import Session, joinedload, load_only
from sqlalchemy import and_
from utils.general import model_to_dict
import random
import http
from datetime import datetime
from service.fixtures_single_elimination import Fixtures_Serivce_Single_Elimination

class Tournament_Game_Service():

    def __init__(self, db: Session):
        self.db = db
    
    ## adding required grounds and umpries for particular game
    def add_grounds_umpries(self, tournament_id: str, umpires: Umpires, grounds: Grounds, user_id: str) -> GenericResponseModel:
        tournament = self.db.query(TOURNAMENT).filter(and_(TOURNAMENT.id == tournament_id, TOURNAMENT.organizer_id==user_id)).first()
        if tournament is None:
            return GenericResponseModel(status='error', message='Tournament or organizer not associated with tournament', status_code=http.HTTPStatus.BAD_REQUEST)

        for up in umpires:
            db_umpire = UMPIRES(**up.dict())
            self.db.add(db_umpire)
        for ground in grounds:
            db_ground = GROUNDS(**ground.dict())
            self.db.add(db_ground)
        self.db.commit()
        return GenericResponseModel(status='success', message='Game details added', status_code=http.HTTPStatus.ACCEPTED)

    
    ## for updating any ground
    def update_ground_for_game(self,ground_id: int, ground: Grounds, user_id: str):
        print("\n\n",ground,"\n\n")
        org_ground = self.db.query(GROUNDS).filter(and_(GROUNDS.id==ground_id, GROUNDS.game_id==ground["game_id"])).first()
        if org_ground is None:
            return GenericResponseModel(status='error', message='Incorrect details passed', status_code=http.HTTPStatus.BAD_REQUEST)

        for key, value in ground.items():
            setattr(org_ground, key, value)

        self.db.add(org_ground)
        self.db.commit()
        return GenericResponseModel(status='success', message="Ground details updated", status_code=http.HTTPStatus.CREATED)
    

    def validation(self, tournament_id: str, user_id: str):
        t = self.db.query(TOURNAMENT).filter(and_(TOURNAMENT.id == tournament_id, TOURNAMENT.organizer_id==user_id)).first()
        if t is None:
            return False
        return True

    # delete ground
    def delete_ground_for_game(self, tournament_id: str, ground_id: int, user_id: str):
        if self.validation(tournament_id, user_id)==False:
            return GenericResponseModel(status='error', message='Mismatch details passed', status_code=http.HTTPStatus.BAD_REQUEST)

        g = self.db.query(GROUNDS).filter(GROUNDS.id==ground_id).delete()
        self.db.commit()
        if g > 0:
            return GenericResponseModel(status='success', message="Deleted successfully", status_code=http.HTTPStatus.CREATED)
        else:
            return GenericResponseModel(status='error', message='Already deleted or incorrect details', status_code=http.HTTPStatus.BAD_REQUEST)
        
    # delete a umpire from certain game
    def delete_umpire_for_game(self, tournament_id: str, umpire_id: int, user_id: str):
        if self.validation(tournament_id, user_id)==False:
            return GenericResponseModel(status='error', message='Mismatch details passed', status_code=http.HTTPStatus.BAD_REQUEST)

        ump = self.db.query(UMPIRES).filter(and_(UMPIRES.id==umpire_id)).delete()
        self.db.commit()
        if ump > 0:
            return GenericResponseModel(status='success', message="Deleted successfully", status_code=http.HTTPStatus.CREATED)
        else:
            return GenericResponseModel(status='error', message='Already deleted or incorrect details', status_code=http.HTTPStatus.BAD_REQUEST)
        
   
    def get_fixtures(self, tournament_id:str, tournament_game_id: str,game_id:int, user_id: str):
        fixtures = self.db.query(FIXTURES).filter(and_(FIXTURES.tournament_id==tournament_id, FIXTURES.tournament_game_id==tournament_game_id)).all()
        if fixtures is None or len(fixtures)==0:
            return GenericResponseModel(status='error', message="Fixtures not created or found", status_code=http.HTTPStatus.BAD_REQUEST)
        
        fixtures_list = [model_to_dict(f) for f in fixtures]
        return GenericResponseModel(status='success', data=fixtures_list, message="Fixtures", status_code=http.HTTPStatus.OK)
        


    # def create_fixtures(self, tournament_id: str, tournament_game_id: str, user_id: str)
    def create_fixtures(self, tournament_id:str, tournament_game_id: str,game_id:int, user_id: str):
        return Fixtures_Serivce_Single_Elimination(self.db).create_fixtures(tournament_id, tournament_game_id, game_id, user_id)
    

    def apply_fixtures(self, tournament_id:str, tournament_game_id: str,game_id:int, user_id: str):
        teams = self.db.query(TEAMS).filter(and_(TEAMS.tournament_id == tournament_id, TEAMS.tournament_game_id==tournament_game_id, TEAMS.verified==1)).all()
        if len(teams)==0:
            return GenericResponseModel(status='error', message="No team found", status_code=http.HTTPStatus.BAD_REQUEST)
        fixtures = self.db.query(FIXTURES).filter(and_(FIXTURES.tournament_id==tournament_id, FIXTURES.tournament_game_id==tournament_game_id)).all()
        if len(fixtures)==0:
            return GenericResponseModel(status='error', message="Fixtures not created", status_code=http.HTTPStatus.BAD_REQUEST)
        
        random.shuffle(teams)

        for i, fixture in enumerate(fixtures):
            if i*2 < len(teams):
                fixture.team_1_id = teams[i*2].id
            if i*2+1 < len(teams):
                fixture.team_2_id = teams[i*2+1].id
        self.db.commit()
        return GenericResponseModel(status='success', message="Fixtures", status_code=http.HTTPStatus.ACCEPTED)

        

    # helper function to check if all matches of that round are over. if over start creating fixtures of next round
    def check_and_declare_next_round(self, tournament_id:str, tournament_game_id:str, round_no: int):
        fixtures = self.db.query(FIXTURES).options(load_only(FIXTURES.winner_id)).filter(and_(FIXTURES.tournament_game_id==tournament_game_id, FIXTURES.round_no==round_no)).all()
        total = len(fixtures)
        winners = []
        for fixture in fixtures:
            if fixture.winner_id != None:
                winners.append(fixture.winner_id)
        print("\n\n")
        print(winners)
        print("\n\n")
        if len(winners) == total:
            next_fixtures = self.db.query(FIXTURES).filter(and_(FIXTURES.tournament_game_id==tournament_game_id, FIXTURES.round_no==round_no+1)).all()
            if len(next_fixtures)>0:
                for i, fixture in enumerate(next_fixtures):
                    if i*2 < len(winners):
                        fixture.team_1_id = winners[i*2]
                    if i*2+1 < len(winners):
                        fixture.team_2_id = winners[i*2+1]
                self.db.commit()


    def give_buy(self, tournament_id:str, tournament_game_id: str, fixture_id:int, user_id: str):
        fixture = self.db.query(FIXTURES).filter(and_(FIXTURES.id==fixture_id, FIXTURES.tournament_id==tournament_id, FIXTURES.tournament_game_id==tournament_game_id)).first()
        if fixture is None:
            return GenericResponseModel(status='error', message="Fixtures not found", status_code=http.HTTPStatus.BAD_REQUEST)

        fixture.winner_id = fixture.team_1_id
        self.db.commit()
        self.check_and_declare_next_round(tournament_id, tournament_game_id, fixture.round_no)
        return GenericResponseModel(status='success', message="Fixture winner successfully updated", status_code=http.HTTPStatus.ACCEPTED)
    

    def post_match_results(self, tournament_id:str, tournament_game_id: str, fixture_id:int, winner_id: str, user_id: str):
        fixture = self.db.query(FIXTURES).filter(and_(FIXTURES.id==fixture_id, FIXTURES.tournament_id==tournament_id, FIXTURES.tournament_game_id==tournament_game_id)).first()
        if fixture is None:
            return GenericResponseModel(status='error', message="Fixtures not found", status_code=http.HTTPStatus.BAD_REQUEST)

        if fixture.team_1_id!=winner_id and fixture.team_2_id!=winner_id:
            return GenericResponseModel(status='error', message="Invalid winner declared", status_code=http.HTTPStatus.BAD_REQUEST)


        fixture.winner_id = winner_id
        self.db.commit()
        self.check_and_declare_next_round(tournament_id, tournament_game_id, fixture.round_no)
        return GenericResponseModel(status='success', message="Fixture winner successfully updated", status_code=http.HTTPStatus.ACCEPTED)
    