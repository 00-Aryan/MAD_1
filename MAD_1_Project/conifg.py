from dotenv import load_dotenv
import os #this will fetch the info from .env using load env and from os.env to app.conig
load_dotenv
from app import app,db

app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv('SQLALCHEMY_DATABASE_URI')


