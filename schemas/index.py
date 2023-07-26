from pydantic import BaseModel
import datetime

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