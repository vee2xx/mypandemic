from sqlalchemy import Column, String, Date, Integer, func, desc
from sqlalchemy.ext.declarative import declarative_base
from models.basemodel import ORMBase
import dbaccess.sqlengine

declarative_base = declarative_base()

class Stat(ORMBase, declarative_base):
    __tablename__ = 'stats'

    id = Column(Integer, primary_key=True, index=True)
    country = Column(String)
    region = Column(String)
    location = Column(String)
    date = Column(Date) 
    confirmed = Column(Integer)
    deaths = Column(Integer)
    recovered = Column(Integer)
    active = Column(Integer)

def find(id):
    session = dbaccess.sqlengine.get_session()
    return session.query(Stat).filter_by(id=id).first()

def find_stats_by_date(country, date):
    session = dbaccess.sqlengine.get_session()
    return session.query(Stat).filter_by(date=date).first()

def find_stats_by_date_range(country, start_date, end_date):
    session = dbaccess.sqlengine.get_session()
    return session.query(Stat).filter_by(country = country).filter(Stat.date >= start_date).filter(Stat.date <= end_date).order_by(desc(Stat.date)).all()

def find_stats_by_region_and_date_range(region, start_date, end_date):
    session = dbaccess.sqlengine.get_session()
    return session.query(Stat).filter_by(region = region).filter(Stat.date >= start_date).filter(Stat.date <= end_date).order_by(desc(Stat.date)).all()

def find_stats_by_region_and_date(region, date):
    session = dbaccess.sqlengine.get_session()
    return session.query(Stat).filter_by(region = region).filter_by(date = date).first()

def get_count_by_region_and_date(region, date):
    session = dbaccess.sqlengine.get_session()
    result = session.query(Stat).filter_by(region = region).filter_by(date = date).first()
    count = 0
    if result is not None:
        count = result.confirmed
    return count

def get_max_date():
    session = dbaccess.sqlengine.get_session()
    mdate = session.query(func.max(Stat.date)).first()
    return mdate[0]
