from dotenv import load_dotenv
import os
load_dotenv
from app import app
app.config['SQLALCHEMY_DATABASE_URI']= os.getenv('SQLALCHEMY_DATABASE_URI')
app.config['SQLALCHEMY_TRACK_MODIFICATION']= os.getenv('SQLALCHEMY_TRACK_MODIFICATION')
app.config['SECRET_KEY']= os.getenv('SECRET_KEY')
app.config['UPLOAD_FOLDER'] = os.getenv('UPLOAD_FOLDER','uploads')


