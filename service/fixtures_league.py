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
from operator import attrgetter
import random

class Fixtures_Service_League():
    def __init__(self, db: Session):
        self.db = db


    def get_required_matches(self, num_teams, teams_per_group, total_groups):
        matches_per_round = []
        
        # Calculate the number of matches in round 1 (round robin)
        matches_round_1 = (teams_per_group * (teams_per_group - 1)) // 2  # Matches per group
        total_matches_round_1 = matches_round_1 * total_groups  # Total matches in round 1
        matches_per_round.append(total_matches_round_1)
        
        # Calculate the number of knockout matches in each round after round 1
        num_teams //= 2
        while num_teams > 1:
            num_teams //= 2
            matches_per_round.append(num_teams)
        return matches_per_round
    
        
    def convert_to_24_hour_format(self, day, start_date, minutes):
        if day == 0:
            new_datetime = datetime.combine(start_date.date(), datetime.min.time()) + timedelta(minutes=minutes)
        else:
            new_datetime = start_date + timedelta(days=day, minutes=minutes)
        return new_datetime



    def schedule_matches(self,tournament_id: str, tournament_game_id: str,game_id:int, num_teams, umpires, grounds, start_date:datetime, end_date:datetime, match_duration, nums_group, teams_per_group):
        matches = []
        
        no_of_rounds = self.get_required_matches(num_teams, teams_per_group, nums_group)
        
        grounds_schedule = dict()
        for ground in grounds:
            grounds_schedule[ground['id']] = None
        umpires_schedule = dict()
        for ump in umpires:
            umpires_schedule[ump['user_id']] = None
        
        start_time =  start_date.hour*60+start_date.minute
        current_time =  start_time
        end_time = end_date.hour*60+start_date.minute
        
        round_no = 0
        match_number = 0
        day = 0

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
                    'match_number': match_number,
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
                if round_no == 1:
                    obj['group'] = (match_number%nums_group)+1
                
                matches.append(obj)
            current_time += match_duration + (match_duration//2)   
            
            
        return matches


    
    def create_fixtures(self, tournament_id: str, tournament_game_id: str,game_id:int, user_id: str):
        g_obj = self.db.query(TOURNAMENT_GAMES).options(
            load_only(TOURNAMENT_GAMES.avg_duration, 
                      TOURNAMENT_GAMES.max_teams, 
                      TOURNAMENT_GAMES.start_date, 
                      TOURNAMENT_GAMES.end_date, 
                      TOURNAMENT_GAMES.teams_per_group, 
                      TOURNAMENT_GAMES.num_groups)
                      ).filter(
            and_(TOURNAMENT_GAMES.id==tournament_game_id)).first()
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


        # umpires = [{'user_id': 1, 'name': 'xyt'}, {'user_id': 2, 'name': 'ytx'}, {'user_id': 3, 'name': 'mxz'}, {'user_id': 4, 'name': 'abc'}]
        # grounds = [{'id': 1, 'name': 'g1'},  {'id': 2, 'name': 'g2'}, {'id': 3, 'name': 'g3'}, {'id': 4, 'name': 'g4'}]

        
        matches = self.schedule_matches(tournament_id, tournament_game_id, game_id, g_obj.max_teams, umpires, grounds, g_obj.start_date, g_obj.end_date, g_obj.avg_duration, g_obj.num_groups, g_obj.teams_per_group)
        for match in matches:
            self.db.add(FIXTURES(**match))
        
        self.db.commit()
        return GenericResponseModel(status='success', message="Fixtures created!", status_code=http.HTTPStatus.ACCEPTED)
        
    

    def apply_fixtures(self, tournament_id: str, tournament_game_id: str):
        teams = self.db.query(TEAMS).filter(and_(TEAMS.tournament_id==tournament_id, TEAMS.tournament_game_id==tournament_game_id)).all()
        if len(teams)==0:
            return GenericResponseModel(status='error', message="No team found", status_code=http.HTTPStatus.BAD_REQUEST)
        fixtures = self.db.query(FIXTURES).filter(and_(FIXTURES.tournament_id==tournament_id, FIXTURES.tournament_game_id==tournament_game_id, FIXTURES.round_no==1)).all()
        if len(fixtures)==0:
            return GenericResponseModel(status='error', message="Fixtures not created", status_code=http.HTTPStatus.BAD_REQUEST)
        
        t_g_obj = self.db.query(TOURNAMENT_GAMES).options(load_only(TOURNAMENT_GAMES.num_groups, TOURNAMENT_GAMES.teams_per_group)).filter(TOURNAMENT_GAMES.id==tournament_game_id).first()
        if t_g_obj is None:
            return GenericResponseModel(status='error', message="Invalid details passed", status_code=http.HTTPStatus.BAD_REQUEST)

        random.shuffle(teams)
        teams = teams[:min(len(teams), t_g_obj.num_groups*t_g_obj.teams_per_group)]
        i = 0
        while i < len(teams):
            teams[i].group = (i%t_g_obj.num_groups)+1
            i = i+1

        teams = sorted(teams,  key=attrgetter('group'))
        fixtures = sorted(fixtures, key=attrgetter('group')) 
        groups = [[] for _ in range(t_g_obj.num_groups)]
        for i, team in enumerate(teams):
            groups[team.group-1].append(team)

        # Create round robin schedule within groups
        round_robin_matches = []
        for group in groups:
            for i in range(len(group)):
                for j in range(i + 1, len(group)):
                    round_robin_matches.append((group[i], group[j]))

        # Assign the round robin matches to the fixtures
        for i, fixture in enumerate(fixtures):
            team_1, team_2 = round_robin_matches[i % len(round_robin_matches)]
            fixture.team_1_id = team_1.id
            fixture.team_2_id = team_2.id

        # Now you can commit the changes to the database
        self.db.commit()

        # return fixtures
        return GenericResponseModel(status='success', message="Fixtures applied pull to refresh", status_code=http.HTTPStatus.ACCEPTED)
        
