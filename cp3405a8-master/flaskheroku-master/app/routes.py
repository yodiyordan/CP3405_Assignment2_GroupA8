import os
from flask import render_template, flash, redirect, request, url_for
from app import app
from app.forms import LoginForm, User, RegForm, SignupForm
from urllib.parse import quote_plus
from pymongo import MongoClient
from werkzeug.security import generate_password_hash
from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user, current_user



client = MongoClient(os.environ.get('MLABURI'))
collection = client[os.environ.get('MLABDB')].herokudb

login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'

@login_manager.user_loader
def load_user(user):
    u = collection.find_one({"user": user})
    if not u:
        return None
    return User(u['user'])


@app.route('/')
@app.route('/index')
def index():
    if current_user.is_authenticated == True:
        user = current_user
    else:
        user = "guest"
    posts = collection.find()
    
    return render_template('index.html', title='Home', user=user, posts=posts)

@app.route('/register', methods=['GET', 'POST'])
def register():
    form = RegForm()
    if request.method == 'POST':
        if form.validate():
            existing_user = User.objects(email=form.email.data).first()
            if existing_user is None:
                hashpass = generate_password_hash(form.password.data, method='sha256')
                hey = User(form.email.data,hashpass).save()
                login_user(hey)
                return redirect(url_for('dashboard'))
    return render_template('register.html', form=form)

@app.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated == True:
        return redirect(url_for('dashboard'))
    form = LoginForm()
    if request.method == 'POST' and form.validate_on_submit():
        user = collection.find_one({"user": form.username.data})
        if user and User.validate_login(user['password'], form.password.data):
            user_obj = User(user['user'])
            login_user(user_obj)
            flash("Logged in successfully!", category='success')
            return redirect(request.args.get("next") or url_for("dashboard"))
        flash("Wrong username or password!", category='error')
    return render_template('login.html', title='login', form=form)


@app.route('/signup', methods=['GET','POST'])
def signup():
    form = SignupForm()
    if request.method == 'POST': # and form.validate_on_submit():
        # check if user_name or email is taken
        user = collection.find_one({"_id": form.username.data})
        if user and User.validate_login(user['password'], form.password.data):
            flash("User already exist!", category='error')
            return render_template('signup.html', title='Register', form=form)

        try:
            # create new user
            pass_hash = generate_password_hash(form.password.data, method='pbkdf2:sha256')
            collection.insert_one({"user": form.username.data, "password": pass_hash, "name": form.first_name.data, "surname": form.last_name.data, "email": form.email.data})
            # log the user in
            user = collection.find_one({"user": form.username.data})
            user_obj = User(user['user'])
            login_user(user_obj)
            flash("Logged in successfully!", category='success')
            return redirect(request.args.get("next") or url_for("dashboard"))
        except Exception as e:
            flash("Exception ! :" + str(e),  category='error')

    return render_template('signup.html', title='Register', form=form)

@app.route('/dashboard')
@login_required
def dashboard():
    return render_template('dashboard.html', name=current_user.email)

@app.route('/logout', methods = ['GET'])
@login_required
def logout():
    logout_user()
    client.close(); 
    return redirect(url_for('login'))