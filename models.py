from sqlalchemy import Column, Integer, String, Float
from database import Base

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, unique=True, index=True)
    email = Column(String, unique=True, index=True)
    password_hash = Column(String) # Storing plain text as requested for this specific task
    name = Column(String)

class CasualtyMain(Base):
    __tablename__ = "casualty_main"

    id = Column(Integer, primary_key=True, index=True)
    srvno = Column(String, index=True) # 군번
    nm = Column(String) # 이름
    rank = Column(String) # 계급
    uc = Column(String) # 부대명
    lat = Column(Float) # 위도
    lng = Column(Float) # 경도
    weather_desc = Column(String, nullable=True) # 기상
    temp = Column(String, nullable=True) # 기온

class Insa(Base):
    __tablename__ = "insa"

    id = Column(Integer, primary_key=True, index=True)
    srvno = Column(String, unique=True, index=True) # 군번 (Unique)
    nm = Column(String) # 이름
    rank = Column(String) # 계급
    uc = Column(String) # 부대명

class MessageLog(Base):
    __tablename__ = "message_log"

    id = Column(Integer, primary_key=True, index=True)
    srvno = Column(String, index=True) # 군번 relating to the message
    dt = Column(String) # datetime string
    msg_type = Column(String) # Message Type (e.g., "사망자 보고")
    recipient = Column(String) # Recipient (e.g., "상급 부대 (작전처)")
    title = Column(String) # Title
    content = Column(String) # Content text
