from flask import Flask , render_template,redirect,url_for,request

from models import db, Customer, Professionals, Orders, Cart,Category,Admin

from app import app

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/login')
def login():
    return render_template('login.html')

@app.route('/register')
def register():
    return render_template('Registration.html')