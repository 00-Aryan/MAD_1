from flask import Flask , render_template,redirect,url_for,request
from flask_sqlalchemy import SQLAlchemy


app = Flask(__name__)

import os

import config

import models

import routes 
