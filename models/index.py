

from sqlalchemy import Column, ForeignKey, Integer, String, Float, Date, DateTime, Boolean
from sqlalchemy.orm import relationship
import datetime
from config.db import Base

class USERS(Base):
    __tablename__ = "USERS"
    
    id = Column(String(30), primary_key=True, index=True)
    first_name = Column(String(80))
    last_name = Column(String(80))
    email_id = Column(String(80), nullable=False, unique=True)
    phone_no = Column(String(20), nullable=False, unique=True)
    password = Column(String(100), nullable=False)
    verified = Column(Integer, default=0)
    gender = Column(String(20), default=None)
    dob = Column(Date, default=None)
    profile_url = Column(String(150), default="https://encrypted-tbn0.gstatic.com/images?q=tbn:ANd9GcTJJ7NRetidOXGwJVnAJXbKD-aTCpm2iDzT6g&usqp=CAU")
    createdAt = Column(DateTime, default=datetime.datetime.utcnow)

    
class PLAYERS(Base):
    __tablename__ = "PLAYERS"
    
    id = Column(Integer, primary_key=True,index=True)
    user_id = Column(String(30), ForeignKey("USERS.id", ondelete="CASCADE"), nullable=False)
    user = relationship("USERS")
    ranking  = Column(Integer, default=1)
    plays = Column(String(100))


class ORGANIZERS(Base):
    __tablename__ = "ORGANIZERS"
    
    id = Column(Integer, primary_key=True,index=True)
    user_id = Column(String(30), ForeignKey("USERS.id", ondelete="CASCADE"), nullable=False)
    user = relationship("USERS")
    name = Column(String(150), nullable=True)
    about = Column(String(150), nullable=True)

    def __repr__(self):
        return 'ItemModel(name=%s)' % (self.name)

class DOCUMENTS(Base):
    __tablename__ = "DOCUMENTS"
    
    id = Column(Integer, primary_key=True,index=True)
    user_id = Column(String(30), ForeignKey("USERS.id", ondelete="CASCADE"), nullable=False)
    user = relationship("USERS")
    document_type = Column(String(100), nullable=False)
    document_url = Column(String(150), nullable=False)
    verified = Column(Integer, default=0)
    createdAt = Column(DateTime, default=datetime.datetime.utcnow)

    
class TOURNAMENT(Base):
    __tablename__ = "TOURNAMENT"
    id = Column(String(30), primary_key=True, index=True)
    name = Column(String(100), nullable=False)
    about = Column(String(100), nullable=False)
    organizer_id = Column(String(30), ForeignKey("USERS.id", ondelete="CASCADE"), nullable=False)
    organizer = relationship("USERS")
    start_date = Column(Date, nullable=False)
    end_date = Column(Date, nullable=False)
    is_payment_done = Column(Boolean, default=True)
    is_active = Column(Boolean, default=True)

class GAMES(Base):
    __tablename__ = "GAMES"
    id = Column(Integer, primary_key=True)
    name = Column(String(100), nullable=False)

class TOURNAMENT_GAMES(Base):
    __tablename__ = "TOURNAMENT_GAMES"
    id = Column(String(30), primary_key=True,index=True)    
    name = Column(String(100), nullable=False)
    info = Column(String(100), default=None)
    tournament_id = Column(String(30), ForeignKey('TOURNAMENT.id',ondelete="CASCADE"), nullable=False)
    tournament = relationship("TOURNAMENT")
    game_id = Column(Integer, ForeignKey('GAMES.id',ondelete="CASCADE"), nullable=False)
    game = relationship("GAMES")
    participation_fees = Column(Integer, default=0)
    prize_pool = Column(Integer, default=0)
    max_teams = Column(Integer, default=8)
    team_size = Column(Integer, default=1)
    min_girls = Column(Integer)
    min_boys= Column(Integer)
    open_to  = Column(String(10), default="Boys")
    total_rounds = Column(Integer, default=3)
    qualification_method = Column(String(10), default="Single Elimintation")
