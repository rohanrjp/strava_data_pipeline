from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.declarative import declarative_base
from config import settings

engine = create_engine(settings.DATABASE_URL) 
Session = sessionmaker(bind=engine)
Base = declarative_base()