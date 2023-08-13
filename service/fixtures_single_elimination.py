from schemas.index import GenericResponseModel, Tournament, Tournament_Games, Teams, TeamPlayers, Umpires, Grounds
from models.index import TOURNAMENT, USERS, TOURNAMENT_GAMES, TEAMS, TEAM_PLAYERS, UMPIRES, GROUNDS, FIXTURES
from sqlalchemy.orm import Session, joinedload, load_only
from sqlalchemy import and_
import shortuuid
from utils.general import model_to_dict
import http
from datetime import datetime
import heapq
import random
from datetime import datetime, timedelta
import random

class Fixtures_Serivce_Single_Elimination():
    def __init__(self, db: Session):
        self.db = db


    def get_required_matches(self, num_teams):
        # Calculate the total number of matches and matches in each round
        total_matches = num_teams - 1
        num_teams //= 2
        matches_per_round = [num_teams // 2 ** i for i in range(total_matches.bit_length())]
        print("\n\n",matches_per_round,"\n\n")
        return matches_per_round
        
    def convert_to_24_hour_format(self, day, start_date, minutes):
        if day == 0:
            new_datetime = datetime.combine(start_date.date(), datetime.min.time()) + timedelta(minutes=minutes)
        else:
            new_datetime = start_date + timedelta(days=day, minutes=minutes)
        return new_datetime



    def schedule_matches(self,tournament_id: str, tournament_game_id: str,game_id:int, num_teams, umpires, grounds, start_date:datetime, end_date:datetime, match_duration):
        matches = []
        
        no_of_rounds = self.get_required_matches(num_teams)
        
        grounds_schedule = dict()
        for ground in grounds:
            grounds_schedule[ground['id']] = None
        umpires_schedule = dict()
        for ump in umpires:
            print(ump)
            umpires_schedule[ump['user_id']] = None
        
        start_time =  start_date.hour*60+start_date.minute
        current_time =  start_time
        end_time = end_date.hour*60+start_date.minute
        
        round_no = 0
        match_number = 0
        day = 0

        print(grounds_schedule)
        print(umpires_schedule)
        print(start_time)

        for total in no_of_rounds:
            round_no += 1
            for i in range(1, total+1):
                match_number += 1
                
                #finding ground
                ground_available = None
                while ground_available == None:
                    mini = 100000
                    for g, time in grounds_schedule.items():
                        if time is None or time < current_time:
                            ground_available = g
                            break
                        mini = min(mini, time)
                    if ground_available is not None:
                        break
                    else:
                        current_time = mini + 10
                    if current_time >= end_time:
                        current_time = start_time
                        day += 1
                
                # finding umpire
                umpire_available = None
                while umpire_available == None:
                    mini = 100000
                    for ump, time in umpires_schedule.items():
                        if time is None or time < current_time:
                            umpire_available = ump
                            break
                        mini = min(mini, time)
                    if umpire_available is not None:
                        break
                    else:
                        current_time = mini + 10
                    if current_time >= end_time:
                        current_time = start_time
                        day += 1
                
                # grounds_schedule[ground_available] = current_time + timedelta(minutes=match_duration)
                grounds_schedule[ground_available] = current_time + match_duration
                umpires_schedule[umpire_available] = current_time +  match_duration
                
                obj = {
                    'tournament_id':tournament_id,
                    'tournament_game_id': tournament_game_id,
                    'game_id': game_id,
                    'round_no': round_no,
                    'team_1_id': None,
                    'team_2_id': None,
                    'winner_id': None,
                    'ground_id': ground_available,
                    'umpire_id': umpire_available,
                    'start_time':  self.convert_to_24_hour_format(day,start_date, current_time),
                    'end_time':  self.convert_to_24_hour_format(day,start_date, current_time+match_duration),
                }
                
                matches.append(obj)
            current_time += match_duration + (match_duration//2)   
            
            
        return matches

    
    def create_fixtures(self, tournament_id: str, tournament_game_id: str,game_id:int, user_id: str):
        
        match_duration = 30
        # Example usage
        num_teams = 16
        # start_time = datetime(year=2023, month=8, day=1, hour=9, minute=0)  # Start time (e.g., August 1, 2023, 9:00 AM)
        # end_time = datetime(year=2023, month=8, day=1, hour=17, minute=0)  # End time (e.g., August 1, 2023, 5:00 PM)
        start_date = datetime(2023, 8, 9, 9) # Start time in minutes (e.g., 9:00 AM)
        end_date = datetime(2023, 8, 10, 17) # Start time in minutes (e.g., 9:00 AM)
        

        # umpires = [{'id': 1, 'name': 'xyt'}, {'id': 2, 'name': 'ytx'}, {'id': 3, 'name': 'mxz'}, {'id': 4, 'name': 'abc'}]
        # grounds = [{'id': 1, 'name': 'g1'},  {'id': 2, 'name': 'g2'}, {'id': 3, 'name': 'g3'}, {'id': 4, 'name': 'g4'}]

        t_obj = self.db.query(TOURNAMENT).options(load_only(TOURNAMENT.start_date, TOURNAMENT.end_date)).filter(and_(TOURNAMENT.id==tournament_id, TOURNAMENT.organizer_id==user_id)).first()
        if t_obj is None:
            return GenericResponseModel(status='error', message="No tournament found or accessing other tournament", status_code=http.HTTPStatus.NOT_FOUND)
        
        g_obj = self.db.query(TOURNAMENT_GAMES).options(load_only(TOURNAMENT_GAMES.avg_duration, TOURNAMENT_GAMES.max_teams)).filter(and_(TOURNAMENT_GAMES.id==tournament_game_id)).first()
        if g_obj is None:
            return GenericResponseModel(status='error', message="Game details not found", status_code=http.HTTPStatus.NOT_FOUND)
        

        check_if_fixtures = self.db.query(FIXTURES).filter(and_(FIXTURES.tournament_id==tournament_id, FIXTURES.tournament_game_id==tournament_game_id)).count()
        if check_if_fixtures>0:
            return GenericResponseModel(status='error', message="Fixtures already created", status_code=http.HTTPStatus.BAD_REQUEST)



        grounds = self.db.query(GROUNDS).filter(and_(GROUNDS.game_id==tournament_game_id)).all()
        umpires = self.db.query(UMPIRES).filter(UMPIRES.game_id==tournament_game_id).all()

        if len(grounds)==0 or len(umpires)==0:
            return GenericResponseModel(status='error', message="Insufficient umpires or grounds", status_code=http.HTTPStatus.CONFLICT)


        grounds = [model_to_dict(g) for g in grounds]
        umpires = [model_to_dict(g) for g in umpires]

        matches = self.schedule_matches(tournament_id, tournament_game_id,game_id, g_obj.max_teams, umpires, grounds, t_obj.start_date, t_obj.end_date, g_obj.avg_duration)
        fixtures_list = []
        for match in matches:
            fixtures_list.append(match)
            self.db.add(FIXTURES(**match))

        self.db.commit()
        return GenericResponseModel(status='success', message="Fixtures", data=fixtures_list, status_code=http.HTTPStatus.ACCEPTED)

