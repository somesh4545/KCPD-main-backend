

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
    gender = Column(Integer, default=None)
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
    participation_fees = Column(Integer, default=0, nullable=False)
    prize_pool = Column(Integer, default=0,  nullable=False)
    max_teams = Column(Integer, default=8,  nullable=False)
    team_size = Column(Integer, default=1,  nullable=False)
    min_girls = Column(Integer,  nullable=False)
    min_boys= Column(Integer,  nullable=False)
    # open to 1(boys) 0(girls) 2(mix ups)
    open_to  = Column(Integer,  nullable=False)
    total_rounds = Column(Integer, default=3)
    qualification_method = Column(String(10), default="Single Elimintation")
    is_active = Column(Boolean, default=True)
    min_age = Column(Integer, default=17, nullable=False)
    max_age = Column(Integer, default=21, nullable=False)

class TEAMS(Base):
    __tablename__ = "TEAMS"
    id = Column(String(30), primary_key=True,index=True)    
    name = Column(String(100), nullable=False)
    admin_id = Column(String(30), ForeignKey("USERS.id"), nullable=False)
    admin = relationship("USERS")
    tournament_id = Column(String(30), ForeignKey('TOURNAMENT.id',ondelete="CASCADE"), nullable=False)
    tournament = relationship("TOURNAMENT")
    tournament_game_id = Column(String(30), ForeignKey('TOURNAMENT_GAMES.id',ondelete="CASCADE"), nullable=False)
    tournament_game = relationship("TOURNAMENT_GAMES")
    # 0 denotes yet to verify 1(verified) -1(rejected)
    verified = Column(Integer, default=0)
    no_of_boys = Column(Integer, nullable=False)
    no_of_girls = Column(Integer, nullable=False)
    createdAt = Column(DateTime, default=datetime.datetime.utcnow)

class TEAM_PLAYERS(Base):
    __tablename__ = "TEAM_PLAYERS"
    id = Column(Integer, primary_key=True,index=True)  
    team_id = Column(String(30), ForeignKey('TEAMS.id',ondelete="CASCADE"), nullable=False)
    team = relationship("TEAMS")
    player_id = Column(String(30), ForeignKey('USERS.id',ondelete="CASCADE"), nullable=False)
    player = relationship("USERS")
    createdAt = Column(DateTime, default=datetime.datetime.utcnow)
    