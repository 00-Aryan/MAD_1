from flask import Flask , render_template,request,redirect,url_for 
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)
db =SQLAlchemy(app)

