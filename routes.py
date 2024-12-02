from functools import wraps
from flask import Flask , render_template,redirect,url_for,request,flash ,session

from models import db, Customer, Professionals, Orders, Cart,Category , Services

from app import app

def auth_required(fnc):
    @wraps(fnc)  # Preserve the original function's metadata
    def inner(*args, **kwargs):
        if 'user_id' in session:
            return fnc(*args, **kwargs)
        # Exclude routes like Login or Register to avoid unnecessary redirects
        if request.endpoint == 'Login' or request.endpoint == 'Register':
            return fnc(*args, **kwargs)
        flash('Please login to continue', 'warning')
        return redirect(url_for('Login'))
    return inner

@app.route('/')
@auth_required
def home():
    user = Customer.query.get(session['user_id'])
    prof = Professionals.query.get(session['prof_id']) #session.geT IS to avoid keyerror
    if prof :
        return render_template('professional_home.html', prof = prof)
    if user and user.admin :
        return redirect(url_for('Admin'))
    else:
        return render_template('customer_home.html', user=user)


@app.route('/profile')
@auth_required
def profile():
    user = Customer.query.get(session['user_id'])
    return render_template('profile.html', user = user)

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

        # Check for customer
        user = Customer.query.filter_by(Email_id=email).first()

        # If not a customer, check for service professional
        if not user:
            user = Professionals.query.filter_by(Email_id=email).first()

        # Validate user and password
        if user and user.check_password(password):  # Ensure `check_password` is implemented
            session['user_id'] = user.id

            # Redirect based on user role
            if isinstance(user, Customer):
                if user.admin:  # Admin role
                    return redirect(url_for('Admin'))
                else:  # Regular customer
                    return redirect(url_for('CS_Home'))
            elif isinstance(user, Professionals):
                # Set prof_id for professionals
                session['prof_id'] = user.id

                # Redirect based on professional status
                if user.status == "approved":
                    return redirect(url_for('SP_Home'))
                elif user.status == "pending":
                    flash("Your account is pending approval.", "warning")
                elif user.status == "rejected":
                    flash("Your account has been rejected. Please contact support.", "danger")
                return redirect(url_for('Login'))
        else:
            flash("Invalid email or password.", "danger")
            return redirect(url_for('Login'))

    # Render login page for GET requests
    return render_template('login.html')



# Registering 


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
@app.route('/register/SP', methods=[ 'POST'])
def post_sp_register():
    if request.method == 'POST':
        # Retrieve form data
        username = request.form.get('email')
        password = request.form.get('password')
        name = request.form.get('name')
        description = request.form.get('description')
        service_type = request.form.get('service_type')
        category_id = request.form.get('category_id')
        status = request.form.get('status')

        # Input validation
        if not username or not password or not name:
            flash("All fields are required", "danger")
            return redirect(url_for('SP_register'))

        # Create a new Professional instance
        professional = Professionals(
            Email_id=username,
            name=name,
            description=description,
            service_type=service_type,
            category_id=category_id,
            status= status 
        )
        professional.set_password(password)  # Assuming set_password hashes the password

        # Save to the database
        db.session.add(professional)
        db.session.commit()

        # Success message
        flash('Registration successful! Pending admin approval.', 'success')
        return redirect(url_for('home'))

    # If GET request, render the registration form with categories
    categories = Category.query.all()
    return render_template('register_service_pro.html', categories=categories)

@app.route('/contact')
def Contact():
    return render_template('contact.html')

#Admin  Controller



@app.route('/admin/professionals/approve/<int:professional_id>', methods=['POST'])
def approve_professional(professional_id):
    professional = Professionals.query.get(professional_id)
    professional.status = 'approved'
    db.session.commit()
    flash(f"{professional.name} has been approved.", "success")
    return redirect(url_for('Admin'))

@app.route('/admin/services/block_user/<user_type>/<int:user_id>', methods=['POST'])
def block_user(user_type, user_id):
    return "blocked"

@app.route('/admin/professionals/reject/<int:professional_id>', methods=['POST'])
def reject_professional(professional_id):
    # Get the professional by ID
    professional = Professionals.query.get_or_404(professional_id)

    # Update 'rejected'
    professional.status = 'rejected'

    # Commit to database
    db.session.commit()

    # Flash a success message
    flash(f"{professional.name} has been rejected.", "danger")

    return redirect(url_for('Admin'))


@app.route('/admin')
@auth_required
def Admin():
    user = Customer.query.get(session['user_id'])
    return render_template('admin.html', user = user)

@app.route('/admin/services', methods=['GET', 'POST'])
@auth_required
def AdminServices():
    user = Customer.query.get(session['user_id'])
    if request.method == 'POST':
        # Retrieve form data
        service_name = request.form.get('service_name')
        base_price = request.form.get('base_price')
        description = request.form.get('Description')
        # time_required = request.form.get('time_required')
        
        # Validate inputs
        if not all([service_name, base_price, description]):
            flash('All fields are required!', 'danger')
            return redirect(url_for('AdminServices'))
        
        # Create a new service
        new_service = Services(
            service_name=service_name,
            base_price=float(base_price),
            description=description,
            
        )
        db.session.add(new_service)
        db.session.commit()
        flash('Service created successfully!', 'success')
        return redirect(url_for('AdminServices'))
    services = Services.query.all()
    professionals = Professionals.query.filter_by(status='pending').all()
    print(f"Professionals: {professionals}")
    return render_template('adminServiceHandling.html',services = services,user = user, professionals=professionals)
    # Fetch all services for display (GET request)



@app.route('/admin/services/delete/<int:service_id>', methods=['POST'])
@auth_required
def delete_service(service_id):
    # Query the service by its ID
    service_to_delete = Services.query.get(service_id)
    
    if not service_to_delete:
        flash('Service not found!', 'danger')
        return redirect(url_for('AdminServices'))
    
    # Delete the service from the database
    db.session.delete(service_to_delete)
    db.session.commit()
    flash('Service deleted !', 'danger')
    
    return redirect(url_for('AdminServices'))

@app.route('/admin/summary')
@auth_required
def summary():  
    user = Customer.query.get(session['user_id'])
    return render_template('adminSummary.html', user = user)

@app.route('/admin/Professionals')
def AdminProfessional():
    return render_template('adminProfessionalHandling.html')




#Customer Management
@app.route('/customer_home')
@auth_required
def CS_Home():
    user = Customer.query.get(session['user_id'])
    return render_template('customer_home.html', user=user)




#Professional Management

@app.route('/professional_home')
@auth_required
def SP_Home():
    user = Professionals.query.get(session.get('prof_id'))
    return render_template('professional_home.html', user=user)


# @app.route('/admin/services')
# @auth_required
# def AdminServices():
#     user = Customer.query.get(session['user_id'])
#     return render_template('adminServiceHandling.html', user = user)



@app.route('/edit_service/<int:service_id>', methods=[ 'POST'])
@auth_required
def edit_service_page():
    return "edited"
    







@app.route('/logout')
def Logout():
    # Log out logic here
    session.pop('user_id', None)
    session.pop('prof_id', None)
    return redirect(url_for('Login')) 

@app.route('/cart')
@auth_required
def cart():
    return "cart"

@app.route('/orders')
@auth_required
def orders():
    return "orders"

