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

class Fixtures_Service_League():
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
        pass
    
    def create_fixtures(self, tournament_id: str, tournament_game_id: str,game_id:int, user_id: str):
    
        pass