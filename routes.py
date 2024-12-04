from functools import wraps
import os
from flask import Flask , render_template,redirect,url_for,request,flash ,session , send_from_directory

from datetime import datetime

from models import db, Customer, Professional, Orders, Cart,Category , Service , ServiceRequest

from app import app

UPLOAD_FOLDER = app.config['UPLOAD_FOLDER']

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

@app.route('/uploads/<filename>')
def uploads(filename):
    upload_folder = os.path.join(app.root_path, 'uploads')  # Adjust the folder path as per your setup
    print(os.path.join(app.root_path, 'uploads'))
    return send_from_directory(upload_folder, filename)

@app.route('/')
@auth_required
def home():
    user = Customer.query.get(session['user_id'])
    prof = Professional.query.get(session.get('prof_id')) #session.geT IS to avoid keyerror
    # print(f"Session Data: {session}")
    if prof :
        return render_template('professional_home.html', prof = prof)
    elif user and user.admin :
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

@app.route('/sp/profile')
@auth_required
def sp_profile():
    user_id = session.get('user_id')
    user = Professional.query.get(user_id)  # Fetch the professional user
    if not user:
        flash('Service Professional not found', 'danger')
        return redirect(url_for('home'))  # Redirect to home if the professional is not found
    return render_template('sp_profile.html', user=user)

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

        # Check for customer first
        user = Customer.query.filter_by(Email_id=email).first()

        # If not a customer, check for service professional
        if not user:
            user = Professional.query.filter_by(Email_id=email).first()

        # Validate user and password
        if user and user.check_password(password):  # Ensure `check_password` is implemented
            session['user_id'] = user.id

            # Redirect based on user role
            if isinstance(user, Customer):
                if user.admin:  # Admin role
                    return redirect(url_for('Admin'))  # Admin dashboard
                else:  # Regular customer
                    return redirect(url_for('CS_Home'))  # Customer homepage
            
            elif isinstance(user, Professional):
                # Set professional session details (optional, if needed for other functionality)
                session['prof_id'] = user.id

                # Redirect based on professional status
                if user.status == "approved":
                    return redirect(url_for('SP_Home'))  # Service professional homepage
                elif user.status == "pending":
                    flash("Your account is pending approval.", "warning")
                    return redirect(url_for('Login'))  # Stay on login page
                elif user.status == "rejected":
                    flash("Your account has been rejected. Please contact support.", "danger")
                    return redirect(url_for('Login'))  # Stay on login page
        else:
            flash("Invalid email or password.", "danger")
            return redirect(url_for('Login'))  # Invalid credentials, stay on login page

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
# @app.route('/register/SP', methods=['GET'])
# def SP_register():
#     categories = Category.query.all()
#     return render_template('SP_Registration.html', category=categories)

# Service provider home route
# @app.route('/register/SP', methods=[ 'POST'])
# def post_sp_register():
#     if request.method == 'POST':
#         # Retrieve form data
        # username = request.form.get('email')
        # password = request.form.get('password')
        # name = request.form.get('name')
        # description = request.form.get('description')
        # service_type = request.form.get('service_type')
        # category_id = request.form.get('category_id')
        # status = request.form.get('status')

#         # Input validation
#         if not username or not password or not name:
#             flash("All fields are required", "danger")
#             return redirect(url_for('SP_register'))

#         # Create a new Professional instance
#         professional = Professionals(
            # Email_id=username,
            # name=name,
            # description=description,
            # service_type=service_type,
            # category_id=category_id,
            # status= status 
#         )
#         professional.set_password(password)  # Assuming set_password hashes the password

#         # Save to the database
#         db.session.add(professional)
#         db.session.commit()

#         # Success message
#         flash('Registration successful! Pending admin approval.', 'success')
#         return redirect(url_for('home'))

#     # If GET request, render the registration form with categories
#     categories = Category.query.all()
#     return render_template('register_service_pro.html', categories=categories)

@app.route('/register/SP', methods=['GET', 'POST'])
def post_sp_register():
    if request.method == 'POST':
        # Process form data
        username = request.form.get('email')
        password = request.form.get('password')
        name = request.form.get('name')
        description = request.form.get('description')
        service_type = request.form.get('service_type')
        category_id = request.form.get('category_id')
        status = request.form.get('status')
        experience = request.form.get('experience')
        address = request.form.get('address')
        pin_code = request.form.get('Pin_Code')
        
        
        document = request.files.get('document')
        document_filename = None
        
        if document and document.filename != '':  # Check if file is uploaded
            document_filename = document.filename
            document.save(os.path.join(app.config['UPLOAD_FOLDER'], document_filename))
            
        
        # Create a new professional
        new_professional = Professional(
            Email_id=username,
            name=name,
            description=description,
            service_type=service_type,
            category_id=category_id,
            status= status,
            experience=experience,
            address=address,
            Pin_Code=pin_code,
            document=document_filename,  # Store the filename in the database
        
        )
        new_professional.set_password(password)
        db.session.add(new_professional)
        db.session.commit()
        flash("Service professional registered successfully, awaiting approval.", "success")
        return redirect(url_for('Login'))  # Redirect after registration
        
    # GET request, fetch categories from the database
    categories = Category.query.all()
    
    # print(f"Categories fetched: {categories}")
    return render_template('SP_Registration.html', categories=categories)



@app.route('/contact')
def Contact():
    return render_template('contact.html')

#Admin  Controller



@app.route('/admin/professionals/approve/<int:professional_id>', methods=['POST'])
def approve_professional(professional_id):
    professional = Professional.query.get(professional_id)
    professionals = Professional.query.all()
    professional.status = 'approved'
    db.session.commit()
    flash(f"{professional.name} has been approved.", "success")
    
    return redirect(url_for('AdminProfessional'))

@app.route('/admin/services/block_user/<user_type>/<int:user_id>', methods=['POST'])
def block_user(user_type, user_id):
    return "blocked"

@app.route('/admin/professionals/reject/<int:professional_id>', methods=['POST'])
def reject_professional(professional_id):
    professionals = Professional.query.all()
    # Get the professional by ID
    professional = Professional.query.get_or_404(professional_id)

    # Update 'rejected'
    professional.status = 'rejected'

    # Commit to database
    db.session.commit()

    # Flash a success message
    flash(f"{professional.name} has been rejected.", "danger")

    return redirect(url_for('AdminProfessional'),professional = professional)


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
        name = request.form.get('name')
        base_price = request.form.get('base_price')
        description = request.form.get('description')
        category_id = request.form.get('category_id')
        # time_required = request.form.get('time_required')
        print(f"Name: {name}")
        print(f"Base Price: {base_price}")
        print(f"Description: {description}")
        print(f"Category ID: {category_id}")

        
        # Validate inputs
        if not all([name, base_price, description,category_id]):
            flash('All fields are required!', 'danger')
            return redirect(url_for('AdminServices'))
        
        # Create a new service
        new_service = Service(
            name=name,
            base_price=float(base_price),
            description=description,
            category_id=int(category_id)
            
        )
        db.session.add(new_service)
        db.session.commit()
        flash('Service created successfully!', 'success')
        return redirect(url_for('AdminServices'))
    services = Service.query.all()
    professionals = Professional.query.filter_by(status='pending').all()
    categories = Category.query.all()
    print(f"Professionals: {professionals}")
    return render_template('adminServiceHandling.html',services = services,user = user, professionals=professionals , categories=categories)
    # Fetch all services for display (GET request)



@app.route('/admin/services/delete/<int:service_id>', methods=['POST'])
@auth_required
def delete_service(service_id):
    # Query the service by its ID
    service_to_delete = Service.query.get(service_id)
    
    if not service_to_delete:
        flash('Service not found!', 'danger')
        return redirect(url_for('AdminServices'))
    
    # Delete the service from the database
    db.session.delete(service_to_delete)
    db.session.commit()
    flash('Service deleted !', 'danger')
    
    return redirect(url_for('AdminServices'))


@app.route('/admin/services/edit/<int:service_id>', methods=['GET', 'POST'])
@auth_required
def edit_service(service_id):
    service = Service.query.get(service_id)
    if not service:
        flash("Service not found.", "danger")
        return redirect(url_for('AdminServices'))
    
    if request.method == 'POST':
        # Update service details
        service.name = request.form.get('name')
        service.base_price = request.form.get('base_price')
        service.description = request.form.get('description')
        service.category_id = request.form.get('category_id')
        
        if not all([service.name, service.base_price, service.description, service.category_id]):
            flash("All fields are required.", "danger")
            return redirect(url_for('edit_service', service_id=service_id))
        
        db.session.commit()
        flash("Service updated successfully.", "success")
        return redirect(url_for('AdminServices'))
    
    # Render edit form
    categories = Category.query.all()
    return render_template('service_edit.html', service=service, categories=categories)



@app.route('/admin/summary')
@auth_required
def summary():  
    user = Customer.query.get(session['user_id'])
    return render_template('admin_summary.html', user = user)

@app.route('/admin/Professionals',methods=['GET', 'POST'])
@auth_required
def AdminProfessional():
    services = Service.query.all()
    user = Customer.query.get(session['user_id'])
    professionals = Professional.query.filter_by(status='pending').all()
    professionals = Professional.query.all()
    return render_template('adminProfessionalHandling.html',user = user , services=services, professionals=professionals)

@app.route('/delete_professional/<int:professional_id>', methods=['POST'])
def delete_professional(professional_id):
    # Fetch the professional from the database
    professional = Professional.query.get(professional_id)
    
    if professional:
        try:
            db.session.delete(professional)  # Delete the professional record
            db.session.commit()  # Commit changes to the database
            flash('Professional deleted successfully!', 'success')
        except Exception as e:
            db.session.rollback()  # Rollback in case of error
            flash('An error occurred. Could not delete the professional.', 'danger')
    else:
        flash('Professional not found.', 'warning')
    
    # Redirect to a page that lists all professionals or to an appropriate page
    return redirect(url_for('view_professionals'))  # Replace with your actual view route


@app.route('/professionals')
def view_professionals():
    user = Customer.query.get(session['user_id'])
    professionals = Professional.query.all()
    return render_template('adminProfessionalHandling.html', user = user, professionals=professionals)

@app.route('/admin/service-requests')
@auth_required
def service_requests():
    user = Customer.query.get(session['user_id'])
    service_requests = ServiceRequest.query.all()
    return render_template('admin_service_requests.html',user = user, service_requests=service_requests)

@app.route('/admin/service-requests/<int:request_id>/<string:status>', methods=['POST'])
@auth_required
def update_request_status(request_id, status):
    service_request = ServiceRequest.query.get(request_id)
    if not service_request:
        flash('Service request not found', 'danger')
        return redirect(url_for('service_requests'))

    service_request.status = status
    db.session.commit()

    flash(f'Service request has been {status}.', 'success')
    return redirect(url_for('service_requests'))



@app.route('/admin_dashboard')
@auth_required

def admin_dashboard():
    user = Customer.query.get(session['user_id'])
    return render_template('admin_dashboard.html', user=user)


@app.route('/book-services', methods=['GET', 'POST'])
def book_services():
    if request.method == 'POST':
        service_id = request.form.get('service_id')
        if not service_id:
            flash("Service ID is required.", "danger")
            return redirect(url_for('book_services'))  # Redirect if no service is selected

        # Fetch the service based on the service_id from the form
        service = Service.query.get(service_id)
        if not service:
            flash("Service not found.", "danger")
            return redirect(url_for('book_services'))  # Redirect if the service doesn't exist

        # Assuming the user is logged in and their ID is stored in the session
        customer_id = session.get('user_id')  # Use 'user_id' from session (this should be a customer ID)
        if not customer_id:
            flash("You need to be logged in to book a service.", "danger")
            return redirect(url_for('login'))  # Redirect to login if user is not logged in

        # Create a new service request
        new_request = ServiceRequest(
            customer_id=customer_id,  # Link the service request to the logged-in customer
            service_id=service_id,     # Link the service request to the selected service
            customer_name=service.name,  # Optional: Use the service name or other relevant data
            service_type=service.name,  # Store the service type or any other relevant info
            status='pending'           # Set the initial status of the request to "pending"
        )

        db.session.add(new_request)  # Add the new request to the session
        db.session.commit()  # Commit the transaction to the database

        flash("Service requested successfully!", "success")
        return redirect(url_for('customer_service_requests'))  # Redirect to the page where the user can see their requests

    # Fetch all services grouped by categories
    categories = Category.query.all()  # Assuming a Category model exists
    user = Customer.query.get(session['user_id'])  # Get the logged-in customer
    return render_template('book_services.html', user=user, categories=categories)

@app.route('/customer/service-requests/delete/<int:request_id>', methods=['POST'])
# @auth_required
def delete_service_request(request_id):
    print(f"Attempting to delete service request with ID: {request_id}")
    customer = Customer.query.get(session['user_id'])  # Get logged-in customer
    user  = session.get('user_id')
    # Fetch the specific service request
    service_request = ServiceRequest.query.get_or_404(request_id)
    
    # Ensure the request belongs to the logged-in customer
    if service_request.customer_id != customer.id:
        flash("You do not have permission to delete this request.", "danger")
        return redirect(url_for('customer_service_requests'))

    # Delete the request from the database
    db.session.delete(service_request)
    db.session.commit()
    flash("Service request deleted successfully!", "success")
    # user = Customer.query.get(session['user_id'])
    return redirect(url_for('customer_service_requests') )


@app.route('/admin/service-requests/edit/<int:request_id>', methods=['GET', 'POST'])
@auth_required
def edit_Aservice_request(request_id):
    service_request = ServiceRequest.query.get(request_id)
    if not service_request:
        flash('Service Request not found!', 'danger')
        return redirect(url_for('service_requests'))

    if request.method == 'POST':
        # Get the date from the form and convert it to a date object
        requested_date_str = request.form.get('requested_date')
        requested_date = datetime.strptime(requested_date_str, '%Y-%m-%d').date() if requested_date_str else None
        
        # Update the service request details
        service_request.status = request.form.get('status')
        service_request.requested_date = requested_date
        service_request.remarks = request.form.get('remarks')  # Assuming remarks field exists

        db.session.commit()
        flash('Service Request updated successfully!', 'success')
        return redirect(url_for('service_requests'))

    # Format the requested_date for the input field (Y-m-d format)
    formatted_date = service_request.requested_date.strftime('%Y-%m-%d') if service_request.requested_date else ''
    return render_template('edit_Aservice_request.html', service_request=service_request, formatted_date=formatted_date)

@app.route('/customer/service-requests/edit/<int:request_id>', methods=['GET', 'POST'])
@auth_required
def edit_Cservice_request(request_id):
    customer = Customer.query.get(session['user_id'])  # Get logged-in customer
    
    # Fetch the specific service request
    service_request = ServiceRequest.query.get_or_404(request_id)
    
    # Ensure the request belongs to the logged-in customer
    if service_request.customer_id != customer.id:
        flash("You do not have permission to edit this request.", "danger")
        return redirect(url_for('customer_service_requests'))
    
    # Handle the form submission to edit the request
    if request.method == 'POST':
        
        requested_date_str = request.form.get('requested_date')
        requested_date = datetime.strptime(requested_date_str, '%Y-%m-%d').date() if requested_date_str else None
        
        service_request.status = request.form['status']
        service_request.requested_date = requested_date
        service_request.remarks = request.form['remarks']
        
        db.session.commit()
        flash("Service request updated successfully!", "success")
        return redirect(url_for('customer_service_requests'))

    # Render the edit form with existing data
    user = Customer.query.get(session['user_id'])
    return render_template('edit_Cservice_request.html', service_request=service_request,user = user)



@app.route('/admin/service-requests/close/<int:request_id>', methods=['POST'])
@auth_required
def close_service_request(request_id):
    service_request = ServiceRequest.query.get(request_id)
    if not service_request:
        flash('Service Request not found!', 'danger')
        return redirect(url_for('service_requests'))

    # Close the service request
    service_request.status = 'closed'
    db.session.commit()
    flash('Service Request closed successfully!', 'success')
    return redirect(url_for('service_requests'))


@app.route('/service-history')
def service_history():
    # Get customer ID from session (assume the user is logged in)
    customer_id = session.get('user_id')
    
    if not customer_id:
        return redirect(url_for('login'))  # Redirect if not logged in

    # Fetch service requests for the customer
    customer = Customer.query.get(customer_id)
    if not customer:
        return redirect(url_for('Login'))  # Redirect if customer is not found

    service_requests = ServiceRequest.query.filter_by(customer_id=customer.id).all()
    
    ratings = {service.id: service.rating for service in service_requests if service.rating is not None}
    
    total_ratings = sum(ratings.values())
    return render_template('service_history.html', service_requests=service_requests, ratings=ratings, total_ratings=total_ratings)
#Customer Management
@app.route('/customer_home')
@auth_required
def CS_Home():
    user = Customer.query.get(session['user_id'])
    return render_template('customer_home.html', user=user)

@app.route('/customer/service-requests', methods=['GET','POST'])
@auth_required  
def customer_service_requests():
    
    customer = Customer.query.get(session['user_id'])  # Fetch logged-in customer.
    service_requests = ServiceRequest.query.filter_by(customer_id=customer.id).all()  # Fetch the requests for the customer.
    user = Customer.query.get(session['user_id'])
    return render_template('customer_service_requests.html',user = user, service_requests=service_requests )


@app.route('/admin/customers', methods=['GET', 'POST'])
@auth_required
def manage_customers():
    user = Customer.query.get(session['user_id'])
    if not user or not user.admin:
        flash("You don't have permission to access this page.", "danger")
        return redirect(url_for('home'))
    
    if request.method == 'POST':
        # Adding a new customer
        customer_id = request.form.get('customer_id')
        if customer_id:  # Editing an existing customer
            customer = Customer.query.get(customer_id)
            if customer:
                customer.name = request.form.get('name')
                customer.Email_id = request.form.get('email')
                customer.address = request.form.get('address')
                customer.Pin_Code = request.form.get('pin_code')
                db.session.commit()
                flash('Customer updated successfully!', 'success')
            else:
                flash('Customer not found!', 'danger')
        else:  # Adding a new customer
            email = request.form.get('email')
            if Customer.query.filter_by(Email_id=email).first():
                flash('Email already exists!', 'danger')
            else:
                new_customer = Customer(
                    name=request.form.get('name'),
                    Email_id=email,
                    address=request.form.get('address'),
                    Pin_Code=request.form.get('pin_code'),
                )
                new_customer.set_password(request.form.get('password'))
                db.session.add(new_customer)
                db.session.commit()
                flash('Customer added successfully!', 'success')
                
    
    customers = Customer.query.filter_by(admin=False).all()
    return render_template('manage_customer.html', user=user, customers=customers)



@app.route('/admin/customers/edit/<int:customer_id>', methods=['GET', 'POST'])
@auth_required
def edit_customer(customer_id):
    user = Customer.query.get(session['user_id'])
    if not user or not user.admin:
        flash("You don't have permission to access this page.", "danger")
        return redirect(url_for('home'))
    
    customer = Customer.query.get_or_404(customer_id)  # Fetch customer or return 404 if not found
    
    if request.method == 'POST':
        # Update the customer information
        customer.name = request.form.get('name')
        customer.Email_id = request.form.get('email')
        customer.address = request.form.get('address')
        customer.Pin_Code = request.form.get('pin_code')
        db.session.commit()
        flash('Customer updated successfully!', 'success')
        return redirect(url_for('manage_customers'))  # Redirect back to the customer list page
    
    return render_template('edit_customer.html', customer=customer)  # Render the edit form



@app.route('/service-remarks')
@auth_required
def service_remarks():
    user = Customer.query.get(session['user_id'])
    return render_template('service_remarks.html', user=user)


#Professional Management

@app.route('/professional_home')
@auth_required
def SP_Home():
    user = Professional.query.get(session.get('prof_id'))
    return render_template('professional_home.html', user=user)

@app.route('/professional/dashboard')
@auth_required
def prof_dashboard():
    user = Professional.query.get(session.get('prof_id'))
    return render_template('professional_dashboard.html', user=user)

# @app.route('category/add')
# @auth_required
# def add_category():



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
    session.clear()
    flash("You have been logged out.", "info")
    return redirect(url_for('Login'))

@app.route('/cart')
@auth_required
def cart():
    return "cart"

@app.route('/orders')
@auth_required
def orders():
    return "orders"

