from flask_sqlalchemy import SQLAlchemy
from app import app
from flask import url_for
import os
db = SQLAlchemy(app)
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime

# Customer Model
class Customer(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    Email_id = db.Column(db.String(32), unique=True, nullable=False)
    passhash = db.Column(db.String(562), nullable=False)
    name = db.Column(db.String(32))
    address = db.Column(db.String(32))
    Pin_Code = db.Column(db.String(8))
    admin = db.Column(db.Boolean, default=False, nullable=False)
    role = db.Column(db.String(16), nullable=False, default='customer')
    
    def set_password(self, password):
        self.passhash = generate_password_hash(password)
    
    def check_password(self, password):
        return check_password_hash(self.passhash, password)


# Professional Model
class Professional(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(84), nullable=False)
    Email_id = db.Column(db.String(32), unique=True, nullable=False)
    passhash = db.Column(db.String(128), nullable=False)
    description = db.Column(db.String(128), nullable=True)
    service_type = db.Column(db.String(128))
    address = db.Column(db.String(32))
    Pin_Code = db.Column(db.String(8))
    experience = db.Column(db.String(8))
    category_id = db.Column(db.Integer, db.ForeignKey('category.id'), nullable=False)
    status = db.Column(db.String(16), nullable=False, default='pending')
    role = db.Column(db.String(16), nullable=False, default='service_professional')
    category = db.relationship('Category', backref='professionals', lazy=True)
    # services = db.relationship('Service', backref='professionals', lazy=True)
    
    date_created = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    document = db.Column(db.String(256), nullable=True)  # New column to store document path

    def get_document_url(self):
        if self.document:
            # Use Flask's url_for to generate the correct URL for the file
            return url_for('static', filename=f'uploads/{self.document}')
        return None
    
    def get_date_created(self):
        return self.date_created.strftime('%Y-%m-%d %H:%M:%S')

    def set_password(self, password):
        self.passhash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.passhash, password)


# Category Model
class Category(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(32), nullable=False)


service_professional_association = db.Table('service_professional_association',
    db.Column('service_id', db.Integer, db.ForeignKey('service.id'), primary_key=True),
    db.Column('professional_id', db.Integer, db.ForeignKey('professional.id'), primary_key=True)
)

# Service Model
class Service(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    base_price = db.Column(db.Float, nullable=False)
    name = db.Column(db.String(64), nullable=False)
    description = db.Column(db.String(32), nullable=False)
    time_required = db.Column(db.String(32), nullable=True)
    ratings = db.Column(db.Integer, nullable=True)
    
    professionals = db.relationship('Professional', secondary=service_professional_association, backref='services')
    
    category_id = db.Column(db.Integer, db.ForeignKey('category.id'), nullable=True)
    category = db.relationship('Category', backref='services')
    professional_id = db.Column(db.Integer, db.ForeignKey('professional.id'), nullable=True) 
    
    


# ServiceRequest Model - Updated to use plural 'professionals'
class ServiceRequest(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    customer_name = db.Column(db.String(100), nullable=False)
    service_type = db.Column(db.String(100), nullable=False)
    requested_date = db.Column(db.Date, default=datetime.utcnow)
    status = db.Column(db.String(20), default='pending')  # pending, approved, rejected
    customer_id = db.Column(db.Integer, db.ForeignKey('customer.id'), nullable=False)
    service_id = db.Column(db.Integer, db.ForeignKey('service.id'), nullable=True)
    professional_id = db.Column(db.Integer, db.ForeignKey('professional.id'), nullable=True)
    remarks = db.Column(db.String(500), nullable=True)

    # Foreign Keys
    customer = db.relationship('Customer', backref='service_requests')
    service = db.relationship('Service', backref='service_requests') 
    professionals = db.relationship('Professional', backref='service_requests', lazy=True)  


# Order Model
class Orders(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    professional_id = db.Column(db.Integer, db.ForeignKey("professional.id"), nullable=False)
    customer_id = db.Column(db.Integer, db.ForeignKey("customer.id"), nullable=False)
    quantity = db.Column(db.Integer, nullable=False)
    order_date = db.Column(db.DateTime, nullable=False)


# Cart Model
class Cart(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    professional_id = db.Column(db.Integer, db.ForeignKey("professional.id"), nullable=False)
    customer_id = db.Column(db.Integer, db.ForeignKey("customer.id"), nullable=False)
    quantity = db.Column(db.Integer, nullable=False)

# Initialize the database
with app.app_context():
    db.create_all()

    # Seed categories if not already present
    categories = ['Plumbing', 'Electrical', 'Cleaning', 'Gardening', 'Carpentry', 'Fashion and styling', 'Beauty Treatment', 'Animal Care']
    existing_categories = {category.name for category in Category.query.all()}

    for category_name in categories:
        if category_name not in existing_categories:
            new_category = Category(name=category_name)
            db.session.add(new_category)

    db.session.commit()
    print("Categories seeded successfully.")

    # Create admin if not exists
    existing_admin = Customer.query.filter_by(admin=True).first()
    if not existing_admin:
        password_hash = generate_password_hash('admin')
        admin_user = Customer(
            Email_id='admin@123.com',
            passhash=password_hash,
            name='Admin',
            role='Admin',
            admin=True
        )
        db.session.add(admin_user)
        db.session.commit()
        print("Admin created successfully.")
    else:
        print("Admin already exists. No changes made.")
