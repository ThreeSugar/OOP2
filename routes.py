#on the command line, please change directory with 'cd' to wherever this app is
#then enter 'python routes.py' on the command line to activate website

import os
from flask import Flask, render_template, url_for, request, session, redirect, send_from_directory, flash
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.exc import IntegrityError
from werkzeug.utils import secure_filename
from flask_bootstrap import Bootstrap
from models import LoginForm, RegisterForm, User, db, Video, SelectForm, EditForm
from flask_login import LoginManager, login_user, login_required, logout_user, current_user
from flask_admin import Admin
from flask_admin.contrib.sqla import ModelView
from flask_admin.contrib.fileadmin import FileAdmin

import pyrebase


app = Flask(__name__)
admin = Admin(app, name = 'LifeStyle28', template_mode = 'bootstrap3')


Bootstrap(app)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///db/database.db'
# 'postgresql://postgres:class@localhost/flaskvids'


app.secret_key = "development-key"
db.init_app(app)

APP_ROOT = os.path.dirname(os.path.abspath(__file__))
STATIC_ROOT = os.path.join(APP_ROOT, 'static')



#FIREBASE

config = {
    "apiKey": "AIzaSyC0TLL0UpuWJJpBcTjpv336tZg95SKqR88",
    "authDomain": "webapp-4eb51.firebaseapp.com",
    "databaseURL": "https://webapp-4eb51.firebaseio.com",
    "storageBucket": "webapp-4eb51.appspot.com",
    "serviceAccount": "firebase.json" #this is to register as an admin with full read/write access
  }

firebase = pyrebase.initialize_app(config)
firedb = firebase.database()  

#FIREBASE AUTH

auth = firebase.auth()
user = auth.sign_in_with_email_and_password("john@john.com", "password")


#FIREBASE TEST
#@app.route('/firebase')
#def firebase():
    #lana = {"name": "Lana Kane", "agency": "Figgis Agency"}
    #firedb.child("agents").child("Lana").set(lana, user['idToken'])
    #return 'Hello World!'


#ADMIN

admin.add_view(ModelView(User, db.session))
path = os.path.join(os.path.dirname(__file__), 'static/assets')
admin.add_view(FileAdmin(path, name='Videos'))

###


#HOMEPAGE (DO NOT TOUCH)
@app.route('/')
@app.route('/index')
def index():
    return render_template('index.html')

###

#LOGIN/REGISTER/SIGNUP (DO NOT TOUCH)
@app.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        if user is not None and user.check_password(form.password.data):
                login_user(user)
                return redirect(url_for('dashboard'))
        else:
            flash('Invalid username or password!')
            return render_template('login.html', form=form)

    return render_template('login.html', form=form)


@app.route('/signup', methods=['GET', 'POST'])
def signup():
    form = RegisterForm()

    if current_user.is_authenticated == True:
        return redirect(url_for('index'))

    if form.validate_on_submit():
        new_user = User(firstname=form.firstname.data, lastname= form.lastname.data, 
        username=form.username.data, email=form.email.data, password = form.password.data)

        try:
            db.session.add(new_user)
            db.session.commit()

        except IntegrityError: #because of db's unique constraint
            flash('Email or Username has already been taken!')
            return render_template('signup.html', form = form)

        return redirect(url_for('login'))

    return render_template('signup.html', form = form)


@app.route('/dashboard')
@login_required
def dashboard():
    return render_template('dashboard.html')

@app.route('/dashboard/video')
@login_required
def dashboardvid():
    return render_template('viddash.html')

@app.route('/dashboard/video/manage')
@login_required
def vidmanage():
    videos = Video.query.all()
    return render_template('vidmanage.html', videos = videos)

@app.route('/dashboard/video/manage/edit/<int:id>', methods=['GET', 'POST'])
@login_required
def videdit(id):
    video = Video.query.get_or_404(id)
    form = EditForm(obj=video, desc = video.description, options = video.category) #default values for form so that users don't have to retype everything
    if form.validate_on_submit():
        video.title = form.title.data
        video.description = form.desc.data
        video.category = form.options.data
        db.session.commit()
        flash('Video successfully edited!')
        return redirect(url_for('vidmanage')) #render template will cause a 'function not iterable error'

    return render_template('videdit.html', form = form)


    

@app.route('/dashboard/video/manage/delete/<int:id>')
@login_required
def viddelete(id):
    video = Video.query.get_or_404(id)
    db.session.delete(video)
    db.session.commit()
    flash('You have successfully deleted the video.')
    return redirect(url_for('vidmanage'))

@app.route('/dashboard/video/upload', methods=['GET', 'POST'])
@login_required
def upload():
    form = SelectForm()
    target = os.path.join(APP_ROOT, 'static/assets')
    print(target)
    print(request.files.getlist('file'))
    
    
    for file in request.files.getlist('file'):
        print(file)
        filename = file.filename
        destination = '/'.join([target, filename])

        try:
            new_vid = Video(link= filename, username = current_user.username, title =  form.title.data, description = form.desc.data, category= form.options.data)
            db.session.add(new_vid)
            db.session.commit()
            print('Accept incoming file: ', filename)
            print('Save it to: ', destination)
            file.save(destination)
            return redirect(url_for('vidmanage'))
        
        except IntegrityError: 
            db.session.rollback()
            flash('Video name already exists!')
            return render_template('dashvid.html', form=form)


    return render_template('dashvid.html', form=form)     

@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('index'))

####


#VIDEO

@app.route('/video')
def video():
    return render_template('videos.html')

@app.route('/video/beginners')
def beginnervideo():
    return render_template('beginnervid.html')

@app.route('/video/advanced')
def advancedvideo():
    return render_template('advancedvid.html')

@app.route('/video/explore')
def explorevideo():
    return render_template('freevid.html')

@app.route('/video/explore/view')
def viewvideo():
    return render_template('viewvid.html')

@app.route('/video/test')
def videos():
    return render_template('upload.html')

# @app.route('/video/display')
# def display_vid():
#     video = []
#     for instance in db.session.query(Video).order_by(Video.id):
#         print(instance.link)
#         video.append(instance.link)

#     print(video)
#     return render_template('displayvid.html', video = video)

@app.route('/video/<videoid>')
def videoz(videoid):
    videoid = Video.query.filter_by(id = videoid).first()
    title = videoid.title
    link = videoid.link
    name = videoid.username
    cat = videoid.category
    desc = videoid.description
    date = videoid.date

    return render_template('displayvid1.html', link=link, name=name, cat=cat, desc=desc, date=date, title=title)


####


### (DO NOT TOUCH)

if __name__ == '__main__':
    login_manager = LoginManager()
    login_manager.init_app(app)

    @login_manager.user_loader
    def load_user(uid):
        return User.query.get(int(uid))

    app.run(debug=True)


