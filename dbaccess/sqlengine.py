from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.declarative import declarative_base
import admin.config as cfg


connection_string = 'mysql+mysqlconnector://{}:{}@{}:{}/mypandemic'.format(cfg.get_config_value('database', 'username'), cfg.get_config_value('database', 'password'),cfg.get_config_value('database', 'host'), cfg.get_config_value('database', 'port'),  cfg.get_config_value('database', 'database'))
engine = create_engine(connection_string, pool_size=100, max_overflow=0)
Session = sessionmaker(bind=engine)
Base = declarative_base()
Base.metadata.create_all(engine)

def get_session():
   return Session()

def save_all(objects):
   session = get_session()
   session.bulk_save_objects(objects)
   session.commit()

