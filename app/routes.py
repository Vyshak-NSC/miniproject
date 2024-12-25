from functools import wraps
from app import app, db, login_manager
from app.models import User, Category, Target, Notification
from app.forms import CategoryForm, EditCategory, SignupForm, LoginForm, TargetForm
from app.extensions import fetch_articles
from flask import render_template, url_for, request, flash, redirect
from flask_login import login_user, current_user, logout_user
from datetime import datetime, timedelta

import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart




def authenticated_only(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not current_user.is_authenticated:
            return redirect(url_for("login"))
        return f(*args, **kwargs)

    return decorated_function


@app.route('/')
@app.route('/index')
def index():
    '''
    Use:
        Default page| Landing page
    Function:
        Signup
        Login
    '''
    
    signup_form = SignupForm()
    login_form = LoginForm()
    return render_template('index.html',signup_form=signup_form, login_form=login_form)


@login_manager.unauthorized_handler
def unauthorized_callback():
    '''
    Use:
        Handles session expiry
    Function:
        redirect to index upon user session expiry
    '''
    logout_user()
    return redirect(url_for("index"))


@app.route('/login', methods=['GET', 'POST'])
def login():
    '''
    Use:
        Handles user login
    Function:
        Verify user credentials
        Login user
    '''
    # If alread logged in, redirect to user dashboard
    if current_user.is_authenticated:
        return redirect(url_for('dashboard'))  # Redirect to the homepage if the user is already logged in

    form = LoginForm()
    #  Process the form data and check for validity
    if form.validate_on_submit():
        user = User.query.filter_by(username=form.username.data).first()
        if user is None or not user.check_password(form.password.data):
            flash("Invalid username or password", "error")
            return redirect(url_for('index')) #  Return to the login page with error message
        
        # Login user if verified
        login_user(user)
        return redirect(url_for('dashboard'))  # Redirect to the homepage after successful login
    return redirect(url_for('index')) # Return to index on failure


@app.route("/signup", methods=["GET","POST"])
def signup():
    '''
    Use:
        handles user signup
    Function:
        User registraion
        Password verification
        Store user data to database
    '''
    signup_form = SignupForm()
    if signup_form.validate():
        # load data
        username = signup_form.username.data
        password = signup_form.password.data
        email    = signup_form.email.data
        
        existing_user = User.query.filter_by(username=username).first()
        if existing_user:
            flash("Username already exists. Please choose a different one.", "error")
            return redirect("index") #failed

    
        # Create new user
        new_user = User(username=username, email=email)
        new_user.set_password(password)
        # add to database
        db.session.add(new_user)
        db.session.commit()

        # Login user after signup
        login_user(new_user)
        return redirect(url_for('dashboard')) #success
    else:
        flash("Invalid input. Please try again.", "error")
        return redirect("index")

## Handles user logout
@authenticated_only
@app.route('/logout')
def logout():
    '''
    Use:
        Handles user Logout
    Function:
        Logout user via flask-login
    '''
    if current_user.is_authenticated:
        logout_user()
    return redirect(url_for('index'))


# User dashboard
@authenticated_only
@app.route('/dashboard')
def dashboard():
    '''
    Use:
        Dashboard page for logged-in users
    Functions: 
        Diplsay expense
        Display graphical representation
    '''
    if current_user.is_authenticated:
        categories = Category.query.filter_by(user_id=current_user.id).all()
        categories = current_user.categories
        category_data = {category.name: category.value for category in categories}
    else:
        return redirect(url_for('index'))
    
    spent,earned = 0,0
    for category in categories:
        if category.exp_type == 'spent':
            spent += category.value
        elif category.exp_type == 'earned':
            earned += category.value
    return render_template("dashboard.html", categories=categories, category_data=category_data, spent = spent,earned=earned)


@app.route('/about')
def about():
    '''
    Use:
        Diplsay  information about the app and its creators
    Function:
        None
    '''
    return render_template('about.html')


@app.route("/services")
def services():
    '''
    Use:
        Display services provide by the site
    Function:
        None
    '''
    return render_template("services.html")


@authenticated_only
@app.route('/articles')
def articles():
    '''
    Use:
        Display articles related to expense management.
    Function:
        Fetch articles from newsapi
        Display summary and link to article
    '''
    if not current_user.is_authenticated:
        return redirect(url_for("login"))
    API_KEY = "ab9bcd20cb7240e9bfc2830e7b4f1546"
    QUERY = "money saving tips"
    articles = fetch_articles(API_KEY, QUERY)
    return render_template("articles.html", articles=articles)


@authenticated_only
@app.route('/notifications')
def notifications():
    '''
    Use:
        Get all notifications of the current logged in user
    Function:
        Display goal exceed notification
        Display  spending below average notification
    '''
    if not current_user.is_authenticated:
        return redirect(url_for("login"))
    notif = Notification.query.all()

    return render_template( "notification.html",notif=notif)

@authenticated_only
@app.route('/categories')
def categories():
    '''
    Use:
        Manage expense categories
    Function:
        Edit|Remove new expense category

    '''
    category_form = CategoryForm()
    edit_cat_form = EditCategory()
    if not current_user.is_authenticated:
        return redirect(url_for("login"))
    categories = current_user.categories #Category.query.filter_by(user_id=current_user.id).all()
    return render_template('categories.html', categories=categories, category_form=category_form, edit_cat_form=edit_cat_form)

@authenticated_only
@app.route('/add_category', methods=['POST'])
def add_category():
    '''
    Use:
        Adds a new expense category to database for currently logged user
    Function:
        Create new category and value
    '''
    if not current_user.is_authenticated:
        return redirect(url_for("login"))
    name = request.form["name"]
    value = request.form["value"]
    exp_type = request.form["exp_type"]

    
    # if user is logged in, add new category and value
    if name != '' and value != '' and type != '':
        new_category =  Category(name=name, value=value, exp_type=exp_type,  user=current_user)
        db.session.add(new_category)
        db.session.commit()
    # redirect to categories page
    
    
    return redirect(url_for('categories'))


@authenticated_only
@app.route("/edit_category", methods=["POST"])
def edit_category():
    """
    Use:
        Edit expense category value
    Function:
        Update category value in database
    """
    if not current_user.is_authenticated:
        return redirect(url_for("login"))

    category_id = request.form.get("id")
    new_name = request.form.get("name")
    new_value = request.form.get("value")
    add_value = request.form.get("addval")
    action = request.form.get("action")
    new_exp_type = request.form.get("exp_type")  # Corrected variable name

    category = Category.query.get(category_id)
    if action == "delete":
        db.session.delete(category)
        db.session.commit()
        flash("Category deleted successfully", "success")

    elif category:
        if new_value:
            category.value = float(new_value)
        if add_value:
            category.value += float(add_value)
        category.name = new_name
        category.exp_type = new_exp_type  # Corrected variable name
        db.session.commit()
        
    targetval=None
    targetval = db.session.query(Target).filter_by(name=Category.name).first()
    if targetval is not None:
        targetval=targetval.value
        if category.value >= targetval:
            print(current_user.email)
            send_email(to_email=current_user.email, limitname=new_name, current_value=category.value, limit_value=targetval)
            print('\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n edit category value exceeded')
    return redirect(url_for("categories"))


@authenticated_only
@app.route('/target')
def  target():
    '''
    Use:
        Show user's set financial goal
    Function:
        Set max expense goal for day|week|month|year
        Notify if  spending is below previous record
        Notify upon limit exceed
    '''
    target_form = TargetForm()
    target_list = [('',)] + db.session.query(Category.name).distinct().all()
    target_form.name.choices = [(tname[0], tname[0]) for tname in target_list]
    
    if not current_user.is_authenticated:
        return redirect(url_for("login"))
    target_table = current_user.target
    return render_template("target.html", target_form=target_form, target_table=target_table, target_list=target_list)


@app.route('/profile')
def profile():
    '''
    Use:
        Show user's profile
    Function:
        Diplay user profile
    '''
    return render_template('profile.html', user=current_user.username)



@authenticated_only
@app.route("/set_target", methods=["POST"])
def set_target():
    if not current_user.is_authenticated:
        return redirect(url_for("login"))
    target_form = TargetForm()
    # if target_form.validate():
    name = target_form.name.data
    value = target_form.value.data
    
    if name.lower() == "daily":
        end_date = datetime.today() + timedelta(days=1)
    elif name.lower() == "weekly":
        end_date = datetime.today() + timedelta(weeks=1)
    elif name.lower() == "monthly":
        end_date = datetime.today().replace(day=1) + timedelta(days=31)  # Assuming 31 days in a month
    elif name.lower() == "yearly":
        end_date = datetime.today().replace(month=1, day=1) + timedelta(days=365)  # Assuming 365 days in a year
    else:
        end_date = datetime.today() + timedelta(days=1)  # Default to one day

    # start_date = datetime.today()
    targetval=None
    
    new_target = Target(name=name, value=value,start_date=datetime.today(), end_date=end_date, user=current_user)
    db.session.add(new_target)
    db.session.commit()
    currentval = Category.query.filter_by(user_id=current_user.id, name=name).first().value
    if currentval >= float(value):
        send_email(to_email=current_user.email, limitname=name, current_value=currentval, limit_value=value)
        print('\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n new target limi exceeded')
    
    return redirect(url_for('target'))


@authenticated_only
@app.route("/edit_target", methods=["POST"])
def edit_target():
    """
    Edit the target details
    """
    if not current_user.is_authenticated:
        return redirect(url_for("login"))
    
    target_id = request.form.get("id")
    new_name = request.form.get("name")
    new_value = request.form.get("value")
    action = request.form.get("action")
    target = Target.query.get(target_id)
    currentval = Category.query.filter_by(user_id=current_user.id, name=target.name).first().value
    
    if target:
        if action == "delete":
            db.session.delete(target)
            db.session.commit()
            flash("Target deleted successfully", "success")
        elif action == "save":
            target.name = new_name
            target.value = new_value
            db.session.commit()
            
            if currentval>=float(target.value):
                send_email(to_email=current_user.email, limitname=target.name, current_value=currentval, limit_value=target.value)
                print('\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n edit target exeeded')
    
            flash("Target updated successfully", "success")

    return redirect(url_for("target"))





# Email configuration
EMAIL_ADDRESS = 'FinanceTrackerSNC@gmail.com'
EMAIL_PASSWORD = 'bnxu shtx nher udvd' 
SMTP_SERVER = 'smtp.gmail.com'
SMTP_PORT = 587


def send_email(to_email, limitname, current_value, limit_value, subject="Expense Manager Notifier"):
    msg = MIMEMultipart()
    msg['From'] = EMAIL_ADDRESS
    msg['To'] = to_email
    msg['Subject'] = subject
    val = int(current_value)-int(limit_value)
    body = f"""
    <html>
    <body>
    <p>Your expenses have exceeded the set limit!</p>
    <table style="border-collapse: collapse; text-align: left;">
        <tr>
            <td>Category</td>
            <td><b>:</b></td>
            <td><b>{limitname.capitalize()}</b></td>
        </tr>
        <tr>
            <td>Limit Set</td>
            <td><b>:</b></td>
            <td><b>{limit_value}</b></td>
        </tr>
        <tr>
            <td>Current Value</td>
            <td><b>:</b></td>
            <td><b>{current_value}</b></td>
        </tr>
        <tr>
            <td>Limit Exceeded By</td>
            <td><b>:</b></td>
            <td><b>{val}</b></td>
        </tr>
    </table>
    </body>
    </html>
    """

    msg.attach(MIMEText(body, 'html'))

    with smtplib.SMTP(SMTP_SERVER, SMTP_PORT) as server:
        server.starttls()
        server.login(EMAIL_ADDRESS, EMAIL_PASSWORD)
        server.send_message(msg)
        print("Message sent")
