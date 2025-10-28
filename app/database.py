from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.declarative import declarative_base
from dotenv import load_dotenv
import os
load_dotenv()
# from dotenv import load_dotenv

# print(DATABASE_URL)
DATABASE_URL = os.getenv("DATABASE_URL")
print(os.getenv("DEBUG"))
engine = create_engine(DATABASE_URL)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()
