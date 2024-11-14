from flask import Flask , render_template,request,redirect,url_for 
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)
db =SQLAlchemy(app)

import config

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(32), unique=True , nullable = False)
    passhash =db.Column(db.String(512), nullable=False)
    name = db.Column()