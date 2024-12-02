from flask_sqlalchemy import SQLAlchemy
from app import app
db = SQLAlchemy(app) 
from werkzeug.security import generate_password_hash , check_password_hash
from datetime import datetime
# db initialisation has to be done after setting config file 

##models


class Customer(db.Model):
    id = db.Column(db.Integer,primary_key=True)
    Email_id = db.Column(db.String(32),unique=True,nullable = False)
    passhash = db.Column(db.String(562),nullable = False)
    name = db.Column(db.String(32))
    address = db.Column(db.String(32))
    Pin_Code = db.Column(db.String(8))
    admin = db.Column(db.Boolean , default=False, nullable=False)



# @property
# def password(self):
#     raise(AttributeError('password is not readable'))

# @password.setter
# def password(self, password):
#     self.passhash = generate_password_hash(password)

# def check_password(self, password):
#         return check_password_hash(self.passhash, password)
    
# Method to set hashed password
    def set_password(self, password):
        self.passhash = generate_password_hash(password)
    
     # Method to check password during login
    def check_password(self, password):
        return check_password_hash(self.passhash, password)


class Professionals(db.Model):
    id = db.Column(db.Integer,primary_key=True)
    name = db.Column(db.String(84),nullable = False)
    Email_id = db.Column(db.String(32),unique=True,nullable = False)
    passhash = db.Column(db.String(128),nullable = False)
    description = db.Column(db.String(128),nullable = True)
    service_type = db.Column(db.String(128))
    category_id = db.Column(db.Integer,db.ForeignKey('category.id'),nullable=False)
    status = db.Column(db.String(16), nullable=False, default='pending')
    
    def set_password(self, password):
        self.passhash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.passhash, password)

class Cart(db.Model):
    id = db.Column(db.Integer,primary_key = True)
    professional_id = db.Column(db.Integer,db.ForeignKey("professionals.id"),nullable= False)
    Customer_id = db.Column(db.Integer,db.ForeignKey("customer.id"),nullable= False)
    quantity = db.Column(db.Integer,nullable = False)

class Services(db.Model):
    id = db.Column(db.Integer,primary_key=True)
    base_price = db.Column(db.Float,nullable=False)
    service_name = db.Column(db.String(64),nullable = False)
    # Image = db.Column(db.String,nullable=True)
    description = db.Column(db.String(32),nullable= False)
    time_required = db.Column(db.String(32),nullable= True)
    category_id = db.Column(db.Integer, db.ForeignKey('category.id'), nullable=True)
    category =db.relationship('Category', backref='services')
    
class Category(db.Model):
    id = db.Column(db.Integer,primary_key=True)
    name = db.Column(db.String(32),nullable =False)
    # List_of_prof= db.relationship('Services',backref='category',lazy=True)
     # Removed List_of_prof, as backref will automatically create 'services' in Services model


class Orders(db.Model):
    id = db.Column(db.Integer,primary_key=True)
    professional_id = db.Column(db.Integer,db.ForeignKey("customer.id"),nullable= False)
    Customer_id = db.Column(db.Integer,db.ForeignKey("professionals.id"),nullable= False)
    quantity = db.Column(db.Integer,nullable = False)
    Order_date = db.Column(db.DateTime, nullable = False)

with app.app_context():
    db.create_all()
    
    
    
    
    # create admin if admin does not exist 
    existing_admin = Customer.query.filter_by(admin=True).first()
    if not existing_admin:
        password_hash = generate_password_hash('admin')
        admin_user = Customer(
            Email_id='admin@123.com',  # Admin email
            passhash=password_hash,
            name='Admin',
            admin=True
        )
        db.session.add(admin_user)
        db.session.commit()
        print("Admin created successfully.")
    else:
        print("Admin already exists. No changes made.")

