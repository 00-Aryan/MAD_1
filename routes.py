from functools import wraps
from flask import Flask , render_template,redirect,url_for,request,flash ,session

from models import db, Customer, Professionals, Orders, Cart,Category , Services

from app import app

def auth_required(fnc):
    @wraps(fnc) #it changes the name of the function returned to the name of the fucntion passed 
    def inner(*args , **kwargs) : #argument and keyword arguments  
        if 'user_id' in session:
            return fnc(*args, **kwargs)
        else:
            flash('Please login to continue')
            return redirect(url_for('Login'))
    return inner

@app.route('/')
@auth_required
def home():
    user = Customer.query.get(session['user_id'])
    if user.admin :
        return redirect(url_for('Admin'))
    else:
        return render_template('customer_home.html', user=user)

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
        email = request.form.get('email')  # Email from login form
        password = request.form.get('password')  # Password from login form

        # Check if the user is a customer
        user = Customer.query.filter_by(Email_id=email).first()

        # If not a customer, check for service professional
        if not user:
            user = Professionals.query.filter_by(Email_id=email).first() #Email_id is from models and email is from the name attribute in html page

        # Check if the user exists and password is correct
        if user and user.check_password(password):  # Ensure `check_password` is implemented
            session['user_id'] = user.id

            # Redirect based on user role
            if isinstance(user, Customer):
                if user.admin:  # Admin role
                    return redirect(url_for('Admin'))
                else:  # Regular customer
                    return redirect(url_for('CS_Home'))
            elif isinstance(user, Professionals):  # Service professional
                if user.approved:  # Only approved professionals are allowed
                    return redirect(url_for('SP_Home'))
                else:
                    flash("Your account is pending approval.", "warning")
                    return redirect(url_for('Login'))
        else:
            flash("Invalid email or password.", "danger")
            return redirect(url_for('Login'))

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
    # print(f"Username: {username}, Password: {password}, Name: {name}, Address: {Address}")
    
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
    categories = Category.query.all()
    return render_template('SP_Registration.html')

# Service provider home route
@app.route('/register/SP', methods=['POST'])
def post_sp_register():
    username = request.form.get('email')
    password = request.form.get('password')
    name = request.form.get('name')
    description = request.form.get('description')
    service_type = request.form.get('service_type')
    category_id = request.form.get('category_id')
    print(f"Username: {username}, Password: {password}, name: {name} , description: {description}, service_type: {service_type}")
    
    if not username or not password or not name:
        flash("All fields are required", "danger")
        return redirect(url_for('SP_register'))
    Professional= Professionals(Email_id = username, passhash = password, name = name, description=description, service_type=service_type , category_id=category_id)
    Professional.set_password(password)
    db.session.add(Professional)
    db.session.commit()
    flash('professional successfully registered','success')
    return redirect(url_for('Login'))

@app.route('/customer_home')
@auth_required
def CS_Home():
    user = Customer.query.get(session['user_id'])
    return render_template('customer_home.html', user=user)

@app.route('/contact')
def Contact():
    return render_template('contact.html')

@app.route('/admin')
@auth_required
def Admin():
    user = Customer.query.get(session['user_id'])
    return render_template('admin.html', user = user)

# @app.route('/admin/services')
# @auth_required
# def AdminServices():
#     user = Customer.query.get(session['user_id'])
#     return render_template('adminServiceHandling.html', user = user)

services= []
@app.route('/admin/services', methods=['GET', 'POST'])
@auth_required
def AdminServices():
    if request.method == 'POST':
        # Retrieve form data
        service_name = request.form.get('service_name')
        base_price = request.form.get('base_price')
        description = request.form.get('Description')
        
        service = Services(service_name = service_name, base_price = base_price, description = description)
        return redirect(url_for('AdminServices'))
    
    # Display the page with current services
    return render_template('adminServiceHandling.html', services=services)


@app.route('/delete_service/<int:service_id>', methods=['POST'])
@auth_required
def delete_service(service_id):
    global services  # Use the global list of services
    # Find the service to delete
    services = [service for service in services if service["id"] != service_id]
    return redirect(url_for('AdminServices'))  # Redirect to the services page

@app.route('/edit_service/<int:service_id>', methods=[ 'POST'])
@auth_required
def edit_service_page():
    return "edited"
    

@app.route('/admin/Professionals')
def AdminProfessional():
    return render_template('adminProfessionalHandling.html')





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

