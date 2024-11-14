from flask_sqlalchemy import SQLAlchemy
from app import app
db = SQLAlchemy(app) 
# db initialisation has to be done after setting config file 

##models

class Admin(db.Model):
    id = db.Column(db.Integer, primary_key=True)  # Primary key
    username = db.Column(db.String(50), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(128), nullable=False)

class Customer(db.Model):
    Cust_id = db.Column(db.Integer,primary_key=True)
    Email_id = db.Column(db.String(32),unique=True,nullable = False)
    passhash = db.Column(db.String(562),nullable = False)
    name = db.Column(db.String(32))

class Professionals(db.Model):
    Prof_id = db.Column(db.Integer,primary_key=True)
    Service_name = db.Column(db.String)
    Email_id = db.Column(db.String(32),unique=True,nullable = False)
    passhash = db.Column(db.String(562),nullable = False)
    # Service_details = db.Column(db.string(128))
    Price = db.Column(db.Float,nullable=False)
    # Image = db.Column(db.String,nullable=True)
    category_id = db.Column(db.Integer,db.ForeignKey('category_id'),nullable=False)

class Cart(db.Model):
    id = db.Column(db.Integer,primary_key = True)
    professional_id = db.Column(db.Integer,db.ForeignKey("Customer.Cust_id"),nullable= False)
    Customer_id = db.Column(db.Integer,db.ForeignKey("Professionals.Prof_id"),nullable= False)
    quantity = db.Column(db.Integer,nullable = False)

class Category(db.Model):
    id = db.Column(db.Integer,primary_key=True)
    name = db.Column(db.String(32))
    List_of_prof= db.relationship('product',backref='category',lazy=True)

class Orders(db.Model):
    id = db.Column(db.Integer,primary_key=True)
    professional_id = db.Column(db.Integer,db.ForeignKey("Customer.Cust_id"),nullable= False)
    Customer_id = db.Column(db.Integer,db.ForeignKey("Professionals.Prof_id"),nullable= False)
    quantity = db.Column(db.Integer,nullable = False)
    Order_date = db.Column(db.DateTime, nullable = False)

