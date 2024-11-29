from flask import Flask , render_template,redirect,url_for,request,flash 

from models import db, Customer, Professionals, Orders, Cart,Category,Admin

from app import app

@app.route('/')
def home():
    return render_template('Home.html')

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
            flash("Login successful!", "success")
            return redirect('/customer_home')  # Redirect to a single dashboard
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
    flash('Customer successfully registered')
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
def CS_Home():
    return render_template('customer_home.html')

@app.route('/contact')
def Contact():
    return render_template('contact.html')

