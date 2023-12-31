from schemas.index import GenericResponseModel, Umpires, Grounds, Winners, Losers
from models.index import TOURNAMENT, USERS, TOURNAMENT_GAMES, TEAMS, TEAM_PLAYERS, UMPIRES, GROUNDS, FIXTURES
from sqlalchemy.orm import Session, joinedload, load_only, aliased
from sqlalchemy import and_, func, desc
from utils.general import model_to_dict, enhanced_model_to_dict
import random
import http
from datetime import datetime
from service.index import Fixtures_Serivce_Single_Elimination, Fixtures_Service_League

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
        

   
    def get_fixtures(self, tournament_id:str, tournament_game_id: str, user_id: str):
        fixtures = self.db.query(FIXTURES).options(
            joinedload(FIXTURES.team_1).load_only(TEAMS.name),
            joinedload(FIXTURES.team_2).load_only(TEAMS.name),
            joinedload(FIXTURES.winner).load_only(TEAMS.name),
            joinedload(FIXTURES.ground).load_only(GROUNDS.name, GROUNDS.location),
            joinedload(FIXTURES.umpire).load_only(USERS.first_name),
        ).where(and_(FIXTURES.tournament_id==tournament_id, FIXTURES.tournament_game_id==tournament_game_id)).all()
        if fixtures is None or len(fixtures)==0:
            return GenericResponseModel(status='error', message="Fixtures not created or found", status_code=http.HTTPStatus.BAD_REQUEST)
        
        # return fixtures
        return {'status': 'success', 'message': "Fixtures found", 'status_code': http.HTTPStatus.OK, 'data': fixtures}


    def get_fixture_by_id(self, fixture_id: int, user_id: str):
        fixture = self.db.query(FIXTURES).options(
            joinedload(FIXTURES.team_1).load_only(TEAMS.name).joinedload(TEAMS.team_players).load_only(TEAM_PLAYERS.id).joinedload(TEAM_PLAYERS.player).load_only(USERS.first_name),
            joinedload(FIXTURES.team_2).load_only(TEAMS.name).joinedload(TEAMS.team_players).load_only(TEAM_PLAYERS.id).joinedload(TEAM_PLAYERS.player).load_only(USERS.first_name),
            joinedload(FIXTURES.winner).load_only(TEAMS.name),
            joinedload(FIXTURES.ground).load_only(GROUNDS.name, GROUNDS.location),
            joinedload(FIXTURES.umpire).load_only(USERS.first_name),
        ).where(and_(FIXTURES.id == fixture_id)).first()
        if fixture is None :
            return GenericResponseModel(status='error', message="Fixture not found", status_code=http.HTTPStatus.BAD_REQUEST)
        return {'status': 'success', 'message': "Fixture found", 'status_code': http.HTTPStatus.OK, 'data': fixture}
        


    # def create_fixtures(self, tournament_id: str, tournament_game_id: str, user_id: str)
    def create_fixtures(self, tournament_id:str, tournament_game_id: str,game_id:int, user_id: str):
        game = self.db.query(TOURNAMENT_GAMES).options(load_only(TOURNAMENT_GAMES.type)).filter(and_(TOURNAMENT_GAMES.id==tournament_game_id)).first()
        if game is None:
            return GenericResponseModel(status='error', message="Invalid tournament game id passed", status_code=http.HTTPStatus.BAD_REQUEST)
        if game.type ==1:
            return Fixtures_Serivce_Single_Elimination(self.db).create_fixtures(tournament_id, tournament_game_id, game_id, user_id)
        if game.type == 2:
            return Fixtures_Service_League(self.db).create_fixtures(tournament_id, tournament_game_id, game_id, user_id)

        return GenericResponseModel(status='error', message="Mention tournament type", status_code=http.HTTPStatus.BAD_REQUEST)


    def apply_fixtures(self, tournament_id:str, tournament_game_id: str,game_id:int, user_id: str):
        game = self.db.query(TOURNAMENT_GAMES).options(load_only(TOURNAMENT_GAMES.type)).filter(and_(TOURNAMENT_GAMES.id==tournament_game_id)).first()
        if game is None:
            return GenericResponseModel(status='error', message="Invalid tournament game id passed", status_code=http.HTTPStatus.BAD_REQUEST)
        if game.type ==1:
            return Fixtures_Serivce_Single_Elimination(self.db).apply_fixtures(tournament_id, tournament_game_id)
        if game.type == 2:
            return Fixtures_Service_League(self.db).apply_fixtures(tournament_id, tournament_game_id)
        
        

    # helper function to check if all matches of that round are over. if over start creating fixtures of next round
    def check_s_and_declare_next_round(self, tournament_game_id:str, round_no: int):
        fixtures = self.db.query(FIXTURES).options(load_only(FIXTURES.winner_id)).filter(and_(FIXTURES.tournament_game_id==tournament_game_id, FIXTURES.round_no==round_no)).all()
        total = len(fixtures)
        winners = []
        for fixture in fixtures:
            if fixture.winner_id != None:
                winners.append(fixture.winner_id)
        if len(winners) == total:
            next_fixtures = self.db.query(FIXTURES).filter(and_(FIXTURES.tournament_game_id==tournament_game_id, FIXTURES.round_no==round_no+1)).all()
            if len(next_fixtures)>0:
                for i, fixture in enumerate(next_fixtures):
                    if i*2 < len(winners):
                        fixture.team_1_id = winners[i*2]
                    if i*2+1 < len(winners):
                        fixture.team_2_id = winners[i*2+1]
                self.db.commit()

    
    def check_l_and_declare_next_round(self, tournament_game_id:str, round_no: int):
        pass
        fixtures = self.db.query(FIXTURES).options(load_only(FIXTURES.winner_id)).filter(and_(FIXTURES.tournament_game_id==tournament_game_id, FIXTURES.round_no==round_no)).count()
       
        winners = self.db.query(FIXTURES).options(load_only(FIXTURES.winner_id)).filter(and_(FIXTURES.tournament_game_id==tournament_game_id, FIXTURES.round_no==round_no, FIXTURES.winner_id!=None)).count()

        if winners == fixtures:
            print("\n\nyesss\n\n")

            print(tournament_game_id)

            top_teams_per_group = self.db.query(TEAMS).options(
                    load_only(TEAMS.group, TEAMS.points)
                ).where(
                    and_(TEAMS.tournament_game_id==tournament_game_id, TEAMS.verified==1)
                ).order_by(TEAMS.group, desc(TEAMS.points), desc(TEAMS.nr)).all()
            
            result = []
            grp = None
            for team in top_teams_per_group:
                if grp == team.group and count<2:
                    count+=1
                    result.append(team)
                elif grp!=team.group:
                    count = 1
                    grp = team.group
                    result.append(team)
                
            next_fixtures = self.db.query(FIXTURES).filter(and_(FIXTURES.tournament_game_id==tournament_game_id, FIXTURES.round_no==round_no+1)).all()
            # to randomize the matches that is top 1 will play with 2nd top from other leagaue
            if len(next_fixtures)>0:
                count = 0
                for i, fixture in enumerate(next_fixtures):
                    if i*2 < len(result):
                        fixture.team_1_id = result[i*2].id
                    if i*2+1 < len(result):
                        inc = 0
                        if count == 0:
                            inc = 3
                            count+=1
                        elif count == 1:
                            inc = -1
                            count = 0
                        fixture.team_2_id = result[i*2+inc].id
                self.db.commit()


    def give_buy(self, tournament_id:str, tournament_game_id: str, fixture_id:int, user_id: str):
        fixture = self.db.query(FIXTURES).filter(and_(FIXTURES.id==fixture_id, FIXTURES.tournament_id==tournament_id, FIXTURES.tournament_game_id==tournament_game_id)).first()
        if fixture is None:
            return GenericResponseModel(status='error', message="Fixtures not found", status_code=http.HTTPStatus.BAD_REQUEST)

        fixture.winner_id = fixture.team_1_id
        self.db.commit()
        t = self.db.query(TOURNAMENT_GAMES).options(load_only(TOURNAMENT_GAMES.type)).filter(TOURNAMENT_GAMES.id==tournament_game_id).first()
        if t.type == 1:
            self.check_s_and_declare_next_round(tournament_game_id, fixture.round_no)
        return GenericResponseModel(status='success', message="Fixture winner successfully updated", status_code=http.HTTPStatus.ACCEPTED)
    

    def post_match_results(self, tournament_game_id: str, fixture_id:int, winner: Winners, loser: Losers):
        
        fixture = self.db.query(FIXTURES).filter(and_(FIXTURES.id==fixture_id, FIXTURES.tournament_game_id==tournament_game_id)).first()
        if fixture is None:
            return GenericResponseModel(status='error', message="Fixtures not found", status_code=http.HTTPStatus.BAD_REQUEST)

        if fixture.team_1_id!=winner.winner_id and fixture.team_2_id!=winner.winner_id:
            return GenericResponseModel(status='error', message="Invalid winner declared", status_code=http.HTTPStatus.BAD_REQUEST)

        team_loser = self.db.query(TEAMS).filter(TEAMS.id==loser.loser_id).first()
        if team_loser is None:    
            return GenericResponseModel(status='error', message="Team not found", status_code=http.HTTPStatus.BAD_REQUEST)
        
        fixture.winner_id = winner.winner_id

        #updating the team points and net run rate if any
        team = self.db.query(TEAMS).filter(TEAMS.id==winner.winner_id).first()
        team.points = (0 if team.points==None else team.points) + winner.points
        team.nr = (0 if team.nr==None else team.nr) + winner.nr
        
        team_loser.points =(0 if team_loser.points==None else team_loser.points) + loser.points
        team_loser.nr = (0 if team_loser.nr==None else team_loser.nr) + loser.nr

        self.db.commit()

        t = self.db.query(TOURNAMENT_GAMES).options(load_only(TOURNAMENT_GAMES.type)).filter(TOURNAMENT_GAMES.id==tournament_game_id).first()
        if t.type == 1:
            self.check_s_and_declare_next_round(tournament_game_id, fixture.round_no)
        if t.type == 2:
            if fixture.round_no+1 == 2:
                self.check_l_and_declare_next_round(tournament_game_id, fixture.round_no)
            else:
                self.check_s_and_declare_next_round(tournament_game_id, fixture.round_no)

        return GenericResponseModel(status='success', message="Fixture winner successfully updated", status_code=http.HTTPStatus.ACCEPTED)



    def get_standings(self, tournament_id:str, tournament_game_id: str, user_id: str):
        t_obj = self.db.query(TOURNAMENT_GAMES).options(load_only(TOURNAMENT_GAMES.type)).filter(TOURNAMENT_GAMES.id==tournament_game_id).first()
        if t_obj is None:
            return GenericResponseModel(status='error', message="Invalid details passed", status_code=http.HTTPStatus.BAD_REQUEST)

        if t_obj.type == 1:
            teams = self.db.query(TEAMS).options(
                load_only(TEAMS.admin_id, TEAMS.points, TEAMS.nr, TEAMS.group)
            ).filter(
                and_(TEAMS.tournament_game_id==tournament_game_id, TEAMS.tournament_id==tournament_id, TEAMS.verified==1)
            ).order_by(desc(TEAMS.points), desc(TEAMS.nr)).all()
            if teams is None:
                return GenericResponseModel(status='error', message="Invalid details passed", status_code=http.HTTPStatus.BAD_REQUEST)

            return {'status': 'success', 'message': "Team standings", 'data': teams, 'status_code': http.HTTPStatus.OK}
        
        if t_obj.type == 2:
            teams = self.db.query(TEAMS).options(
                load_only(TEAMS.admin_id, TEAMS.points, TEAMS.nr, TEAMS.group)
            ).filter(and_(
                TEAMS.tournament_game_id==tournament_game_id, TEAMS.tournament_id==tournament_id, TEAMS.verified==1
            )).order_by(TEAMS.group, desc(TEAMS.points), desc(TEAMS.nr)).all()
            if teams is None:
                return GenericResponseModel(status='error', message="Invalid details passed", status_code=http.HTTPStatus.BAD_REQUEST)

            return {'status': 'success', 'message': "Team standings", 'data': teams, 'status_code': http.HTTPStatus.OK}
        



    def get_tournamenet_game_details(self, tournament_id:str, tournament_game_id: str, user_id: str):
        details = self.db.query(TOURNAMENT_GAMES).options(
            joinedload(TOURNAMENT_GAMES.grounds).load_only(GROUNDS.name, GROUNDS.location),
            joinedload(TOURNAMENT_GAMES.umpires).load_only(UMPIRES.id).joinedload(UMPIRES.user).load_only(USERS.first_name, USERS.last_name, USERS.profile_url)
        ).filter(and_(TOURNAMENT_GAMES.id==tournament_game_id)).first()
        if details is None:
            return GenericResponseModel(status='error', message="Invalid details passed", status_code=http.HTTPStatus.BAD_REQUEST)
        
        return {'status': 'success', 'message': "Details", 'data': details, 'status_code': http.HTTPStatus.OK}
        