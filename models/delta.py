from sqlalchemy import Column, String, Date, Integer, Float, func, desc
from sqlalchemy.ext.declarative import declarative_base
from models.basemodel import ORMBase
import dbaccess.sqlengine
import datetime
from pytz import timezone

declarative_base = declarative_base()


class Delta(ORMBase, declarative_base):
    __tablename__ = 'deltas'

    id = Column(Integer, primary_key=True, index=True)
    country = Column(String)
    region = Column(String)
    date = Column(Date) 
    new_cases = Column(Integer)
    percent_delta = Column(Float)


def find(id):
    session = dbaccess.sqlengine.get_session()
    return session.query(Delta).filter_by(id=id).first()

def find_deltas_by_date_range(region, start_date, end_date):
    session = dbaccess.sqlengine.get_session()
    return session.query(Delta).filter_by(region = region).filter(Delta.date >= start_date).filter(Delta.date <= end_date).order_by(desc(Delta.date)).all()

def find_delta_by_region_and_date(region, date):
    session = dbaccess.sqlengine.get_session()
    test = session.query(Delta).filter_by(region = region).filter_by(date = date)
    return session.query(Delta).filter_by(region = region).filter_by(date = date).first()

def find_deltas_by_date(date, country):
    session = dbaccess.sqlengine.get_session()
    return session.query(Delta, Region).filter(Delta.region == Region.region).filter_by(country = country).filter_by(date = date).order_by(desc(Delta.new_cases)).all()

def get_max_date():
    session = dbaccess.sqlengine.get_session()
    mdate = session.query(func.max(Delta.date)).first()
    return mdate[0]
