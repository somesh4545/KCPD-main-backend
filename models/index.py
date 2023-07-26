

from sqlalchemy import Column, ForeignKey, Integer, String, Float, Date, DateTime, Boolean
from sqlalchemy.orm import relationship
import datetime
from config.db import Base

class USERS(Base):
    __tablename__ = "USERS"
    
    id = Column(String(15), primary_key=True, index=True)
    first_name = Column(String(80))
    last_name = Column(String(80))
    email_id = Column(String(80), nullable=False)
    phone_no = Column(String(20), nullable=False)
    password = Column(String(100), nullable=False)
    verified = Column(Integer, default=0)
    gender = Column(String(10), default=None)
    dob = Column(Date, default=None)
    profile_url = Column(String(150), default="https://encrypted-tbn0.gstatic.com/images?q=tbn:ANd9GcTJJ7NRetidOXGwJVnAJXbKD-aTCpm2iDzT6g&usqp=CAU")
    createdAt = Column(DateTime, default=datetime.datetime.utcnow)


    def __repr__(self):
        return 'ItemModel(name=%s)' % (self.name)

    
class PLAYERS(Base):
    __tablename__ = "PLAYERS"
    
    id = Column(Integer, primary_key=True,index=True)
    user_id = Column(String(15), ForeignKey("USERS.id", ondelete="CASCADE"), nullable=False)
    user = relationship("USERS")
    ranking  = Column(Integer, default=1)
    plays = Column(String(100))

    def __repr__(self):
        return 'ItemModel(name=%s)' % (self.name)

class ORGANIZERS(Base):
    __tablename__ = "ORGANIZERS"
    
    id = Column(Integer, primary_key=True,index=True)
    user_id = Column(String(15), ForeignKey("USERS.id", ondelete="CASCADE"), nullable=False)
    user = relationship("USERS")
    name = Column(String(150), nullable=True)
    about = Column(String(150), nullable=True)

    def __repr__(self):
        return 'ItemModel(name=%s)' % (self.name)

class DOCUMENTS(Base):
    __tablename__ = "DOCUMENTS"
    
    id = Column(Integer, primary_key=True,index=True)
    user_id = Column(String(15), ForeignKey("USERS.id", ondelete="CASCADE"), nullable=False)
    user = relationship("USERS")
    document_type = Column(String(100), nullable=False)
    document_url = Column(String(150), nullable=False)
    verified = Column(Integer, default=0)
    createdAt = Column(DateTime, default=datetime.datetime.utcnow)

    def __repr__(self):
        return 'ItemModel(name=%s)' % (self.name)
    
