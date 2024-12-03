from flask_sqlalchemy import SQLAlchemy
from app import app
import os
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
    role = db.Column(db.String(16), nullable=False, default='customer')
    



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
    address = db.Column(db.String(32))
    Pin_Code = db.Column(db.String(8))
    experience = db.Column(db.String(8))
    category_id = db.Column(db.Integer,db.ForeignKey('category.id'),nullable=False)
    status = db.Column(db.String(16), nullable=False, default='pending')
    role = db.Column(db.String(16), nullable=False, default='service_professional')
    category = db.relationship('Category', backref='professionals', lazy=True)
    
    date_created = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    document = db.Column(db.String(256), nullable=True)  # New column to store document path

    # Optional: A method to get the file path or handle the document
    def get_document_url(self):
        return os.path.join('uploads', self.document) if self.document else None
    def get_date_created(self):
        return self.date_created.strftime('%Y-%m-%d %H:%M:%S')
    
    
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

categories = ['Plumbing', 'Electrical', 'Cleaning', 'Gardening', 'Carpentry']

# Check if categories already exist to avoid duplicates

    
class Orders(db.Model):
    id = db.Column(db.Integer,primary_key=True)
    professional_id = db.Column(db.Integer,db.ForeignKey("customer.id"),nullable= False)
    Customer_id = db.Column(db.Integer,db.ForeignKey("professionals.id"),nullable= False)
    quantity = db.Column(db.Integer,nullable = False)
    Order_date = db.Column(db.DateTime, nullable = False)

with app.app_context():
    db.create_all()
    
    
    existing_categories = {category.name for category in Category.query.all()}

    for category_name in categories:
        if category_name not in existing_categories:
            new_category = Category(name=category_name)
            db.session.add(new_category)

    db.session.commit()
    print("Categories seeded successfully.")
    
    # create admin if admin does not exist 
    existing_admin = Customer.query.filter_by(admin=True).first()
    if not existing_admin:
        password_hash = generate_password_hash('admin')
        admin_user = Customer(
            Email_id='admin@123.com',  # Admin email
            passhash=password_hash,
            name='Admin',
            role ='Admin',
            admin=True
        )
        db.session.add(admin_user)
        db.session.commit()
        print("Admin created successfully.")
    else:
        print("Admin already exists. No changes made.")

