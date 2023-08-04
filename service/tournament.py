from schemas.index import GenericResponseModel, Tournament, Tournament_Games, Teams, TeamPlayers
from models.index import TOURNAMENT, USERS, TOURNAMENT_GAMES, TEAMS, TEAM_PLAYERS
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


    # to check if user already registerd for the given tournament game or not
    def check_if_registered(self, user_id: str, tournament_id: str, tournament_game_id: str, team_id: str=None):
        count1 = self.db.query(TEAMS).filter(and_(TEAMS.admin_id==user_id, TEAMS.tournament_id==tournament_id, TEAMS.tournament_game_id==tournament_game_id)).count()
        count2 = 0
        if team_id is not None:
            count2 = self.db.query(TEAM_PLAYERS).filter(and_(TEAM_PLAYERS.team_id==team_id, TEAM_PLAYERS.player_id==user_id)).count()
        if count1 == 0 and count2==0:
            return True
        return False

    
    def checker(self, team: Teams, user_id: str):
        tournament = self.db.query(TOURNAMENT_GAMES).options(load_only(TOURNAMENT_GAMES.is_active, TOURNAMENT_GAMES.open_to)).filter(and_(TOURNAMENT_GAMES.id==team.tournament_game_id, TOURNAMENT_GAMES.tournament_id==team.tournament_id)).first()
        if tournament is None:
            return GenericResponseModel(status='error', message='Invalid details provided', status_code=http.HTTPStatus.BAD_REQUEST)

        if tournament.is_active==False:
            return GenericResponseModel(status='error', message='Tournament Game is not active', status_code=http.HTTPStatus.BAD_REQUEST)
        
        user = self.db.query(USERS).options(load_only(USERS.gender, USERS.verified)).filter(USERS.id==user_id).first()
        
        if (tournament.open_to!=2 and tournament.open_to!=user.gender) or user.gender is None:
            return GenericResponseModel(status='error', message='Tournament Game is not for your gender or update profile', status_code=http.HTTPStatus.BAD_REQUEST)

        if user.verified==0 or user.verified==-1:
            return GenericResponseModel(status='error', message='User profile is not verified', status_code=http.HTTPStatus.BAD_REQUEST)
        
        return None

    def create_team(self, team: Teams, user_id: str)->GenericResponseModel:
        checker_result = self.checker(team, user_id)
        if checker_result is not None:
            return checker_result

        if self.check_if_registered(user_id, team.tournament_id, team.tournament_game_id) == False:
            return GenericResponseModel(status='error', message='User already registered for the game', status_code=http.HTTPStatus.BAD_REQUEST)

        team_obj = TEAMS(**team.dict())
        team_obj.id = shortuuid.uuid()[:16]
        team_id = team_obj.id
        team_player_obj = TEAM_PLAYERS(team_id=team_id, player_id=user_id)
        self.db.add(team_obj)
        self.db.add(team_player_obj)
        self.db.commit()

        return GenericResponseModel(status='success', message='Team created successfully', data={'team_id': team_id}, status_code=http.HTTPStatus.ACCEPTED)
        


    def join_team(self, tournament_id:str, tournament_game_id:str, team_id: str, user_id: str):
        pass