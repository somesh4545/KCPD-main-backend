from schemas.index import GenericResponseModel, Tournament, Tournament_Games, Teams, TeamPlayers
from models.index import TOURNAMENT, USERS, TOURNAMENT_GAMES, TEAMS, TEAM_PLAYERS
from sqlalchemy.orm import Session, joinedload, load_only
from sqlalchemy import and_
import shortuuid
from utils.general import model_to_dict
import http
from datetime import datetime

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


    # to check if user already registerd for the given tournament game or not
    def check_if_registered(self, user_id: str, tournament_id: str, tournament_game_id: str, team_id: str=None):
        
        return False
    
    def calculate_age(self, dob: datetime) -> int:
        today = datetime.now()
        age = today.year - dob.year - ((today.month, today.day) < (dob.month, dob.day))
        return age
    
    def checker(self, team: Teams, user_id: str, team_id: str=None):
        tournament = self.db.query(TOURNAMENT_GAMES).filter(and_(TOURNAMENT_GAMES.id==team.tournament_game_id, TOURNAMENT_GAMES.tournament_id==team.tournament_id)).first()
        if tournament is None:
            return GenericResponseModel(status='error', message='Invalid details provided', status_code=http.HTTPStatus.BAD_REQUEST)

        if tournament.is_active==False:
            return GenericResponseModel(status='error', message='Tournament Game is not active', status_code=http.HTTPStatus.BAD_REQUEST)
        
        user = self.db.query(USERS).options(load_only(USERS.gender, USERS.verified, USERS.dob)).filter(USERS.id==user_id).first()
        
        if (tournament.open_to!=2 and tournament.open_to!=user.gender) or user.gender is None or user.dob is None:
            return GenericResponseModel(status='error', message='Tournament Game is not for your gender or update profile', status_code=http.HTTPStatus.BAD_REQUEST)

        if user.verified==0 or user.verified==-1:
            return GenericResponseModel(status='error', message='User profile is not verified', status_code=http.HTTPStatus.BAD_REQUEST)

        user_age = self.calculate_age(user.dob)

        if (tournament.min_age is not None and user_age < tournament.min_age) or (tournament.max_age is not None and user_age > tournament.max_age):
            return GenericResponseModel(status='error', message='User age does not meet the tournament requirements', status_code=http.HTTPStatus.BAD_REQUEST)

        count1 = self.db.query(TEAMS).filter(and_(TEAMS.admin_id==user_id, TEAMS.tournament_id==team.tournament_id, TEAMS.tournament_game_id==team.tournament_game_id)).count()
        if count1 != 0:
            return GenericResponseModel(status='error', message='User already registered', status_code=http.HTTPStatus.BAD_REQUEST)
        count2 = 0
        if team_id is not None:
            team_obj = self.db.query(TEAMS).filter(TEAMS.id == team_id).first()
            if team_obj is None:
                return GenericResponseModel(status='error', message='Invalid team id provided', status_code=http.HTTPStatus.BAD_REQUEST)
            
            count2 = self.db.query(TEAM_PLAYERS).filter(and_(TEAM_PLAYERS.team_id==team_id, TEAM_PLAYERS.player_id==user_id)).count()
            if count2 != 0:
                return GenericResponseModel(status='error', message='User already registered', status_code=http.HTTPStatus.BAD_REQUEST)
        

            team_size = tournament.team_size
            team_filled = team_obj.no_of_boys+team_obj.no_of_girls
            if  team_filled == team_size:
                return GenericResponseModel(status='error', message='Team is already full', status_code=http.HTTPStatus.BAD_REQUEST)

            min_boys = tournament.min_boys
            min_girls = tournament.min_girls
            
            user_gender = user.gender
            if user_gender == 1 and team_obj.no_of_girls<min_girls and min_girls+(team_filled-team_obj.no_of_girls)+1>team_size:
                return GenericResponseModel(status='error', message='Maximum boys that can be added reached', status_code=http.HTTPStatus.BAD_REQUEST)
            elif user_gender == 0 and team_obj.no_of_boys<min_boys and min_boys+(team_filled-team_obj.no_of_boys)+1>team_size:
                return GenericResponseModel(status='error', message='Maximum girls that can be added reached', status_code=http.HTTPStatus.BAD_REQUEST)
            else:
                if user_gender == 1:
                    team_obj.no_of_boys += 1
                else:
                    team_obj.no_of_girls += 1
                self.db.add(team_obj)



        
        return True


    def create_team(self, team: Teams, user_id: str)->GenericResponseModel:
        checker_result = self.checker(team, user_id)
        if checker_result is not True:
            return checker_result
        
        print("\n\nReached after checker result if\n\n")

        team_obj = TEAMS(**team.dict())
        team_obj.id = shortuuid.uuid()[:16]
        team_id = team_obj.id
        team_player_obj = TEAM_PLAYERS(team_id=team_id, player_id=user_id)
        self.db.add(team_obj)
        self.db.add(team_player_obj)
        self.db.commit()

        return GenericResponseModel(status='success', message='Team created successfully', data={'team_id': team_id}, status_code=http.HTTPStatus.ACCEPTED)
        


    def join_team(self, team: Teams, team_id: str, user_id: str):
        # obj = {'tournament_id':tournament_id, 'tournament_game_id':tournament_game_id};

        # return obj
        checker_result = self.checker(team, user_id, team_id)
        if checker_result is not True:
            return checker_result
        
        team_player = TEAM_PLAYERS(team_id= team_id, player_id= user_id)
        self.db.add(team_player)
        self.db.commit()
        return GenericResponseModel(status='success', message='Team player added successfully',  status_code=http.HTTPStatus.ACCEPTED)
        