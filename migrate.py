from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.sql.functions import func
from flask_script import Manager
from flask_migrate import Migrate, MigrateCommand
from flask_login import UserMixin


app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///db/database.db'

#'postgresql://postgres:class@localhost/flaskvids'

db = SQLAlchemy(app)
migrate = Migrate(app, db)

## ADD MODELS HERE FOR MIGRATION TO DB!

class User(UserMixin, db.Model):
    __tablename__ = 'users'
    uid = db.Column(db.Integer, primary_key = True)
    firstname = db.Column(db.String(100))
    lastname = db.Column(db.String(100))
    username = db.Column(db.String(100), unique= True)
    email = db.Column(db.String(120), unique = True)
    pwdhash = db.Column(db.String(54))

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

class VideoLikes(db.Model):
    id = db.Column(db.Integer, primary_key = True)
    videoid = db.Column(db.Integer)
    likes = db.Column(db.Integer)
    username = db.Column(db.String(100), unique=True)

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

class Profile(db.Model):
      id = db.Column(db.Integer, primary_key = True)
      userid = db.Column(db.Integer, unique=True)
      desc = db.Column(db.String)
      interests = db.Column(db.String)
      location = db.Column(db.String(90))

class UserMail(db.Model):
    id = db.Column(db.Integer, primary_key = True)
    sender = db.Column(db.String(100))
    target = db.Column(db.String(100))
    subject = db.Column(db.String)
    message = db.Column(db.Text)
    date = db.Column(db.DateTime(timezone=True), server_default=func.now())

manager = Manager(app)
manager.add_command('db', MigrateCommand)

if __name__ == '__main__':
    manager.run()

