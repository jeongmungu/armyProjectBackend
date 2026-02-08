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

class Insa(Base):
    __tablename__ = "insa"

    id = Column(Integer, primary_key=True, index=True)
    srvno = Column(String, unique=True, index=True) # 군번 (Unique)
    nm = Column(String) # 이름
    rank = Column(String) # 계급
    uc = Column(String) # 부대명
