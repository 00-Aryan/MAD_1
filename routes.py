from functools import wraps
from flask import Flask , render_template,redirect,url_for,request,flash ,session

from models import db, Customer, Professionals, Orders, Cart,Category

from app import app

def auth_required(fnc):
    @wraps(fnc) #ity changes the name of the function returned to the name of the fucntion passed 
    def inner(*args , **kwargs) : #argument and keyword arguments  
        if 'user_id' not in session:
            flash('You must provide a user', 'danger')
            return redirect(url_for('Login'))
        return fnc(*args, **kwargs)
    return inner
@app.route('/')
@auth_required
def home():
    return render_template('home.html', user = Customer.query.get(session['user_id']))

@app.route('/profile')
@auth_required
def profile():
    return render_template('profile.html', user = Customer.query.get(session['user_id']))

@app.route('/profile' , methods = ['POST'])
@auth_required
def post_profile():
    user = Customer.query.get(session['user_id'])
    Email_id =request.form.get('email')
    name = request.form.get('name')
    address = request.form.get('address')
    pin_code = request.form.get('pin_code')
    password = request.form.get('password')
    cpassword = request.form.get('cpassword')
    if Email_id =='' or password =='' or cpassword =='' :
        flash('Email id and password can not be empty', 'danger')
        return redirect(url_for('profile'))
    if not user.check_password(cpassword):
        flash('Incorrect password', 'danger')
        return redirect(url_for('profile'))
    if Customer.query.filter_by(Email_id=Email_id).first() and Email_id != user.Email_id :
        flash('username already exists Choose a new Email', 'danger')
        return redirect(url_for('profile'))
    user.username = Email_id
    user.name = name
    user.address = address
    user.pin_code = pin_code
    user.password = password   
    db.session.commit()
    flash('Profile updated successfully','success')
    return redirect(url_for('profile'))
# @app.route("/services")
# def services():
#     return render_template('Services Page')


# @app.route('/login')
# def Login():
#     return render_template('login.html')

# @app.route('/login', methods=['GET', 'POST'])
# def Login():
#     if request.method == 'POST':
#         email = request.form.get('Email_id')
#         password = request.form.get('password_hash')
#         user = Customer.query.filter_by(Email_id = email).first()  # Ensure this function is implemented correctly

#         if user and user.check_password(password):
#             if user.role == 'customer':
#                 return redirect('/customer_home')
#             elif user.role == 'Service professional':
#                 return redirect('/SP_home')
#             elif user.role == 'admin':
#                 return redirect('/admin-panel')
#             else:
#                 flash("Unexpected role. Contact support.")
#                 return redirect('/login')
#         else:
#             flash("Invalid email or password.")
#             return redirect('/login')
#     return render_template('login.html')

@app.route('/login', methods=['GET', 'POST'])
def Login():
    if request.method == 'POST':
        email = request.form.get('email')  # Match form field name
        password = request.form.get('password')  # Match form field name
        # print(f"Username: {email}, Password: {password}")
        

        user = Customer.query.filter_by(Email_id=email).first()
        # print(user)

        if user and user.check_password(password):
            session['user_id'] = user.id
            if user.admin:
                # Admin user
                return redirect(url_for('Admin') ) # Redirect to the admin panel
            else:
                # Regular customer
                return redirect(url_for('CS_Home'))
        else:
            flash("Invalid email or password.", "danger")
            return redirect('/login')
    return render_template('login.html')

# Route for customer registration form (GET)
@app.route('/register/customer', methods=['GET'])
def CS_register():
    return render_template('Customer_Registration.html')

# Route for handling customer registration (POST)
@app.route('/register/customer', methods=['POST'])
def post_register_customer():
    username = request.form.get('email')
    password = request.form.get('password')
    name = request.form.get('name')
    Address = request.form.get('address')
    pin_code = request.form.get('Pin_Code')

    # Validate inputs
    print(f"Username: {username}, Password: {password}, Name: {name}, Address: {Address}")
    
    if not username or not password or not name:
        flash("All fields are required", "danger")
        return redirect(url_for('CS_register'))
    
    user = Customer(Email_id = username, passhash = password, name = name , address = Address , Pin_Code = pin_code)
    user.set_password(password)
    db.session.add(user)
    db.session.commit()
    flash('Customer successfully registered','success')
    return redirect(url_for('Login'))  # Redirect to a success or login page

# Route for service provider registration form
@app.route('/register/SP', methods=['GET'])
def SP_register():
    return render_template('SP_Registration.html')

# Service provider home route
@app.route('/ServiceProf_Home', methods=['GET'])
def SP_Home():
    return render_template('SP_home.html')


@app.route('/customer_home')
@auth_required
def CS_Home():
    user = Customer.query.get(session['user_id'])
    return render_template('customer_home.html', user=user)

@app.route('/contact')
def Contact():
    return render_template('contact.html')

@app.route('/admin')
def Admin():
    return render_template('admin.html')

@app.route('/logout')
def Logout():
    # Log out logic here
    session.pop('user_id', None)
    return redirect(url_for('Login')) 

@app.route('/cart')
@auth_required
def cart():
    return "cart"

@app.route('/orders')
@auth_required
def orders():
    return "orders"

