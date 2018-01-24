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
      username = db.Column(db.String)
      desc = db.Column(db.String)
      interests = db.Column(db.String)
      location = db.Column(db.String(90))

class UserMail(db.Model):
    id = db.Column(db.Integer, primary_key = True)
    target = db.Column(db.String(100))
    sender = db.Column(db.String(100))
    subject = db.Column(db.String)
    message = db.Column(db.Text)
    seen = db.Column(db.Boolean)
    flag = db.Column(db.Boolean)
    date = db.Column(db.DateTime(timezone=True), server_default=func.now())

class BlogPost(db.Model):
    id = db.Column(db.Integer, primary_key = True)
    title = db.Column(db.String())
    author = db.Column(db.String())
    image = db.Column(db.String())
    description  = db.Column(db.String())
    content = db.Column(db.String())
    date = db.Column(db.DateTime(timezone=True), server_default=func.now())


class RecipePost(db.Model):
    id = db.Column(db.Integer, primary_key = True)
    title = db.Column(db.String())
    author = db.Column(db.String())
    time = db.Column(db.String())
    image = db.Column(db.String())
    description  = db.Column(db.String())
    difficulty = db.Column(db.String())
    instruction = db.Column(db.String())
    category = db.Column(db.String())
    ingredients = db.Column(db.String())
    nutri = db.Column(db.String())
    date = db.Column(db.DateTime(timezone=True), server_default=func.now())


class Item(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50))
    info = db.Column(db.String(50))
    price = db.Column(db.Float)
    description = db.Column(db.Text)
    calories = db.Column(db.Integer)
    category = db.Column(db.String(50))
    totalratings = db.Column(db.Integer)
    rating = db.Column(db.Integer)
    rating_count = db.Column(db.Integer)

class Cart(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    item_id = db.Column(db.Integer, unique=True)
    name = db.Column(db.Text)
    quantity = db.Column(db.Integer)
    price = db.Column(db.Float)
    subtotal = db.Column(db.Float)

class Comments(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    item_id = db.Column(db.Integer)
    name = db.Column(db.Text)
    rating = db.Column(db.Integer)
    comment = db.Column(db.Text)

class FitnessGen(db.Model):
    id = db.Column(db.Integer, primary_key = True)
    genid = db.Column(db.Integer)
    category = db.Column(db.String)
    workout = db.Column(db.String)

class FitnessLib(db.Model):
    id = db.Column(db.Integer, primary_key = True)
    category = db.Column(db.String)
    title = db.Column(db.String)
    desc = db.Column(db.String)
    vidlink = db.Column(db.String)

class SaveInboxState(db.Model):
    id = db.Column(db.Integer, primary_key = True)
    username = db.Column(db.String)
    subjectasc = db.Column(db.Boolean)
    subjectdesc = db.Column(db.Boolean)
    dateasc = db.Column(db.Boolean)
    datedesc = db.Column(db.Boolean)

class SaveSentState(db.Model):
    id = db.Column(db.Integer, primary_key = True)
    username = db.Column(db.String)
    subjectasc = db.Column(db.Boolean)
    subjectdesc = db.Column(db.Boolean)
    dateasc = db.Column(db.Boolean)
    datedesc = db.Column(db.Boolean)

class SaveFlaggedState(db.Model):
    id = db.Column(db.Integer, primary_key = True)
    username = db.Column(db.String)
    subjectasc = db.Column(db.Boolean)
    subjectdesc = db.Column(db.Boolean)
    dateasc = db.Column(db.Boolean)
    datedesc = db.Column(db.Boolean)

class FitnessPlaylist(db.Model):
    id = db.Column(db.Integer, primary_key = True)
    username = db.Column(db.String)
    title = db.Column(db.String)
    desc = db.Column(db.String)


class SavePlaylistVids(db.Model):
    id = db.Column(db.Integer, primary_key = True)
    playlist_id = db.Column(db.Integer)
    video_id = db.Column(db.Integer)
    order_no = db.Column(db.Integer)
    title = db.Column(db.String)
    desc = db.Column(db.String)   

manager = Manager(app)
manager.add_command('db', MigrateCommand)

if __name__ == '__main__':
    manager.run()

