

from sqlalchemy import Column, ForeignKey, Integer, String, Float, Date, DateTime, Boolean
from sqlalchemy.orm import relationship
import datetime
from config.db import Base
    
class PLAYERS(Base):
    __tablename__ = "PLAYERS"
    
    id = Column(Integer, primary_key=True,index=True)
    name = Column(String(80), nullable=False)
    email_id= Column(String(80), nullable=False, unique=True)
    mobile_number = Column(String(80), nullable=False)
    emergency_contact = Column(String(80), nullable=True)
    photo_url = Column(String(150), nullable=True)
    dob = Column(Date)
    verified = Column(Boolean, default=False)
    password = Column(String(255), nullable=False)
    createdAt = Column(DateTime, default=datetime.datetime.utcnow)

    def __repr__(self):
        return 'ItemModel(name=%s)' % (self.name)

class ORGANIZERS(Base):
    __tablename__ = "ORGANIZERS"
    
    id = Column(Integer, primary_key=True,index=True)
    name = Column(String(80), nullable=False)
    email_id= Column(String(80), nullable=False, unique=True)
    mobile_number = Column(String(80), nullable=False)
    about = Column(String(150), nullable=True)
    verified = Column(Boolean, default=False)
    password = Column(String(255), nullable=False)
    createdAt = Column(DateTime, default=datetime.datetime.utcnow)

    def __repr__(self):
        return 'ItemModel(name=%s)' % (self.name)

class DOCUMENTS(Base):
    __tablename__ = "DOCUMENTS"
    
    id = Column(Integer, primary_key=True,index=True)
    user_type = Column(String(100), nullable=False)
    user_id = Column(Integer, nullable=False)
    document_type = Column(String(100), nullable=False)
    document_url = Column(String(150), nullable=False)
    verified = Column(Boolean, default=False)
    createdAt = Column(DateTime, default=datetime.datetime.utcnow)

    def __repr__(self):
        return 'ItemModel(name=%s)' % (self.name)
    
