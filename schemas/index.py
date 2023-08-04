from pydantic import BaseModel
import datetime
from typing import Optional, Any

class User(BaseModel):
    email_id: str
    first_name: str
    last_name: str
    phone_no: str
    password: str

class Player(BaseModel):
    name: str
    email_id: str
    mobile_number: str
    dob: datetime.date
    password: str

class Organizer(BaseModel):
    name: str
    email_id: str
    mobile_number: str
    password: str

class Tournament(BaseModel):
    name: str
    about: str
    organizer_id: str
    start_date: datetime.date
    end_date: datetime.date
    is_payment_done: bool = True
    is_active: bool = True

class Tournament_Games(BaseModel):
    name: str
    info: str = None
    tournament_id :str
    game_id: int
    participation_fees: int
    prize_pool: int
    max_teams: int
    team_size: int
    min_girls: int
    min_boys: int
    open_to: int
    total_rounds: int
    qualification_method: str

class Document(BaseModel):
    user_id: str
    document_type: str
    document_url: str

class TokenPayload(BaseModel):
    sub: str = None
    exp: int = None

class Login(BaseModel):
    email_id: str
    password: str

class GenericResponseModel(BaseModel):
    """Generic response model for all responses"""
    api_id: Optional[str] = None
    status: Optional[str]
    message: Optional[str]
    data: Any = None
    status_code: Optional[int] = None

class Teams(BaseModel):
    name: str
    admin_id: str
    tournament_id: str
    tournament_game_id: str

class TeamPlayers(BaseModel):
    team_id: str
    player_id: str