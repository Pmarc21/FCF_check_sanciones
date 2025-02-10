from sqlalchemy import create_engine, Column, Integer, String
from sqlalchemy.orm import sessionmaker, declarative_base

Base = declarative_base()

class SuspendedPlayer(Base):
    __tablename__ = 'suspended_players'
    id = Column(Integer, primary_key=True)
    name = Column(String)
    sanction_matches = Column(Integer)
    team = Column(String)

class MatchdayPlayers(Base):
    __tablename__ = 'MatchdayPlayers'
    id = Column(Integer, primary_key=True)
    name = Column(String)
    matchday = Column(Integer)

engine = create_engine('sqlite:///suspended_players.db')
Base.metadata.create_all(engine)

Session = sessionmaker(bind=engine)
session = Session()