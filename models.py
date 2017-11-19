from flask import Flask
from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, BooleanField, SelectField, FileField
from flask_wtf.file import FileRequired, FileAllowed
from wtforms.validators import InputRequired, Email, Length
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.sql.functions import func
from werkzeug import generate_password_hash, check_password_hash
from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user, current_user


db = SQLAlchemy()
login_manager = LoginManager()
login_manager.init_app(Flask(__name__))
login_manager.login_view = 'login'


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

class Video(db.Model):
    __tablename__ = 'video'
    id = db.Column(db.Integer, primary_key = True)
    username = db.Column(db.String(100))
    link = db.Column(db.String(200), unique= True)
    category = db.Column(db.String(100))
    date = db.Column(db.DateTime(timezone=True), server_default=func.now())


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

class SelectForm(FlaskForm):
    videos = FileField(validators=[FileRequired(), FileAllowed(['mp4', 'webm', 'opgg'])])
    options = SelectField(u'Categories', choices=[('edu', 'Educational'), ('exercise', 'Exercise'), ('food', 'Food'), ('music', 'Music')])