from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base

#SQLALCHEMY_DATABASE_URL = "postgresql://app_data:1q2w3e4r!@localhost/mypatabase"
SQLALCHEMY_DATABASE_URL = "postgresql://user:agNMRVNGIcFTorzPe9Wf1cjx2fGuogq4@dpg-d6r1odfafjfc73evbgqg-a/mypatabase_sub"

engine = create_engine(SQLALCHEMY_DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
