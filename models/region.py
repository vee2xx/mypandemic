from sqlalchemy import Column, String, Date, Integer, Numeric
from sqlalchemy.ext.declarative import declarative_base
from models.basemodel import ORMBase
import dbaccess.sqlengine

declarative_base = declarative_base()

class Region(ORMBase, declarative_base):
    __tablename__ = 'country_regions'

    id = Column(Integer, primary_key=True, index=True)
    country = Column(String)
    region = Column(String)

def find(id):
    session = dbaccess.sqlengine.get_session()
    return session.query(Delta).filter_by(id=id).first()


def find_region_by_country(country):
    session = dbaccess.sqlengine.get_session()
    return session.query(Region).distinct(Region.region).filter_by(country=country)