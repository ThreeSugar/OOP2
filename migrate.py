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
    link = db.Column(db.String(200), unique= True)
    category = db.Column(db.String(100))
    date = db.Column(db.DateTime(timezone=True), server_default=func.now())
    

manager = Manager(app)
manager.add_command('db', MigrateCommand)

if __name__ == '__main__':
    manager.run()

