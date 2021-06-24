from sqlalchemy import Column, String, Date, Integer, Numeric
from sqlalchemy.ext.declarative import declarative_base
from models.basemodel import ORMBase
from pydantic import BaseModel
import dbaccess.sqlengine
import bcrypt

declarative_base = declarative_base()

class User(declarative_base, ORMBase):
    __tablename__ = 'users'

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String)
    country = Column(String)
    region = Column(String)
    timezone = Column(String) 
    phone_number = Column(String)
    email = Column(String)
    preferences = Column(String)
    role = Column(Integer)
    password = Column(String)
    # CHECK (JSON_VALID(preferences)))

class UserResponseModel(BaseModel):
    username: str
    country: str
    region: str
    timezone: str
    phone_number: str
    email: str
    preferences: str
    role: int
    password: str


def find(id):
    session = dbaccess.sqlengine.get_session()
    return session.query(User).filter_by(id=id).first()

def find_by_username(username):
    session = dbaccess.sqlengine.get_session()
    return session.query(User).filter_by(username=username).first()

def find_users_by_region(region):
    session = dbaccess.sqlengine.get_session()
    return session.query(User).filter_by(region=region)

def update_user(username, data):
    session = dbaccess.sqlengine.get_session()
    session.query(User).filter(User.username == username).update(data)
    try:
        session.commit()
    except Exception as e:
        session.rollback()
        raise e
    finally:  
        session.close()          

def user_model_to_orm(user_model):
    user = User()
    user.username = user_model.username
    user.country = user_model.country
    user.region = user_model.region
    user.timezone = user_model.timezone
    user.phone_number = user_model.phone_number
    user.email = user_model.email
    user.preferences = user_model.preferences
    user.role = user_model.role
    user.password = bcrypt.hashpw(user_model.password.encode('utf-8'), bcrypt.gensalt())
    return user
    

def setpassword(username, password):
    hashed_password = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt())
    models.user.update_user(username, {'password': hashed_password})
