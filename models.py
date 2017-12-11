from flask import Flask
from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, BooleanField, SelectField, TextAreaField
from flask_wtf.file import FileRequired, FileAllowed
from wtforms.validators import InputRequired, Email, Length
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.orm import relationship
from sqlalchemy.sql.functions import func
from werkzeug import generate_password_hash, check_password_hash
from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user, current_user, \
AnonymousUserMixin


db = SQLAlchemy()
login_manager = LoginManager()
login_manager.init_app(Flask(__name__))
login_manager.login_view = 'login'

#LOGIN
class User(UserMixin, db.Model):
    __tablename__ = 'users'
    uid = db.Column(db.Integer, primary_key = True)
    firstname = db.Column(db.String(100))
    lastname = db.Column(db.String(100))
    username = db.Column(db.String(100), unique= True)
    email = db.Column(db.String(120), unique = True)
    pwdhash = db.Column(db.String(54))

    def __init__(self, username = '', firstname= '', lastname= '', email= '', password= ''):
        self.firstname = firstname.title()
        self.lastname = lastname.title()
        self.username = username
        self.email = email.lower()
        self.set_password(password)

 #init has default arguments passed in for flask-admin to do its CRUD magic for the model.

    def set_password(self, password):
            self.pwdhash = generate_password_hash(password)

    def check_password(self, password):
            return check_password_hash(self.pwdhash, password)

    def get_id(self): #because I used uid instead of id, so I have to overwrite get_id from flask_login
        try:
            return unicode(self.uid)  # python 2
        except NameError:
            return str(self.uid)  # python 3

class Anonymous(AnonymousUserMixin):
    def __init__(self):
        self.username = "Guest"



class LoginForm(FlaskForm):
    email = StringField('Email', validators=[InputRequired(), Email(message='Invalid Email'), Length(max=50)])
    password = PasswordField('Password', validators=[InputRequired(), Length(min=8, max=80)])
    remember = BooleanField('Remember Me')

class RegisterForm(FlaskForm):
    firstname = StringField('First Name')
    lastname = StringField('Last Name')
    email = StringField('Email', validators=[InputRequired(), Email(message='Invalid Email'), Length(max=50)])
    username = StringField('Username', validators=[InputRequired(), Length(min=4, max=15)])
    password = PasswordField('Password', validators=[InputRequired(), Length(min=8, max=80)])


#VIDEO 

class Video(db.Model):
    __tablename__ = 'video'
    id = db.Column(db.Integer, primary_key = True)
    username = db.Column(db.String(100))
    title = db.Column(db.String(100))
    description = db.Column(db.String(500))
    link = db.Column(db.String(200), unique= True)
    category = db.Column(db.String(100))
    date = db.Column(db.DateTime(timezone=True), server_default=func.now())

class VideoComment(db.Model):
    id = db.Column(db.Integer, primary_key = True)
    videoid = db.Column(db.Integer)
    username = db.Column(db.String(100))
    comment = db.Column(db.String(3000))
    #date = db.Column(db.DateTime(timezone=True), server_default=func.now())

class VideoLikes(db.Model):
    id = db.Column(db.Integer, primary_key = True)
    videoid = db.Column(db.Integer)
    likes = db.Column(db.Integer)
    username = db.Column(db.String(100))

class VideoDislikes(db.Model):
    id = db.Column(db.Integer, primary_key = True)
    videoid = db.Column(db.Integer)
    dislikes = db.Column(db.Integer)
    username = db.Column(db.String(100))

class VideoSaved(db.Model):
    id = db.Column(db.Integer, primary_key = True)
    username = db.Column(db.String(100))
    savedname = db.Column(db.String(100))
    videoid = db.Column(db.Integer)
    title = db.Column(db.String(100))
    description = db.Column(db.String(500))
    link = db.Column(db.String(200))
    category = db.Column(db.String(100))
    saveddate = db.Column(db.DateTime(timezone=True), server_default=func.now())
    date = db.Column(db.DateTime(timezone=True), server_default=func.now())

class VideoViews(db.Model):
    id = db.Column(db.Integer, primary_key = True)
    username = db.Column(db.String(100))
    videoid = db.Column(db.Integer)
    views = db.Column(db.Integer)

class SelectForm(FlaskForm):
    title = StringField('Title', validators=[InputRequired(), Length(min=4, max=90)])
    options = SelectField(u'Categories', choices=[('educational', 'Educational'), ('exercise', 'Exercise'), ('food', 'Food'), ('music', 'Music')])
    desc = TextAreaField('Description', validators=[InputRequired(), Length(min=8, max=300)])

class EditForm(FlaskForm):
    title = StringField('Title', validators=[InputRequired(), Length(min=4, max=90)])
    desc = TextAreaField('Description', validators=[InputRequired(), Length(min=8, max=300)])
    options = SelectField(u'Categories', choices=[('educational', 'Educational'), ('exercise', 'Exercise'), ('food', 'Food'), ('music', 'Music')])

class VideoSearch(FlaskForm):
    search = StringField(validators=[InputRequired(), ])


#INBOX

class UserMail(db.Model):
    id = db.Column(db.Integer, primary_key = True)
    sender = db.Column(db.String(100))
    target = db.Column(db.String(100))
    subject = db.Column(db.String)
    message = db.Column(db.Text)
    seen = db.Column(db.Boolean)
    flag = db.Column(db.Boolean)
    date = db.Column(db.DateTime(timezone=True), server_default=func.now())


class SendMessage(FlaskForm):
    to = StringField('To', validators=[InputRequired(), Length(min=4, max=90)])
    subject = StringField('Subject', validators=[InputRequired()])
    message = TextAreaField('Message')


#PROFILE
class Profile(db.Model):
      id = db.Column(db.Integer, primary_key = True)
      userid = db.Column(db.Integer, unique=True)
      username = db.Column(db.String, unique=True)
      desc = db.Column(db.String)
      interests = db.Column(db.String)
      location = db.Column(db.String(90))

class EditProfile(FlaskForm):
    desc = TextAreaField('Description', validators=[InputRequired(), Length(min=4)])
    interests = TextAreaField('Interests', validators=[InputRequired(), Length(min=4, max=3000)])
    location = StringField('Location', validators=[InputRequired(), Length(min=4, max=90)])

#FIREBASE FORM
class FireForm(FlaskForm):
    place = StringField('Place', validators=[InputRequired(), ])
    email = StringField('Email', validators=[InputRequired(), Email(message='Invalid Email'), Length(max=50)])



   





