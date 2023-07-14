from pydantic import BaseModel
import datetime

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
    user_type: str
    user_id: int
    document_type: str
    document_url: str

class TokenPayload(BaseModel):
    sub: str = None
    exp: int = None
