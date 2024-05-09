from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.declarative import declarative_base
from typing import Final

DATABASE_URL: Final[str] = 'sqlite:///database/discord_league.db'
Base = declarative_base()

engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def setup_database() -> None:
    Base.metadata.create_all(bind=engine)

def get_db_session():
    return SessionLocal()


if __name__ == '__main__':
    setup_database()
