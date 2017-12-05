from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate, MigrateCommand
from flask_script import Manager

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///db/database.db'

db = SQLAlchemy(app)
migrate = Migrate(app, db)

manager = Manager(app)
manager.add_command('db', MigrateCommand)

class Item(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50))
    info = db.Column(db.String(50))
    price = db.Column(db.Float)
    description = db.Column(db.Text(50))

class Cart(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    itemid = db.Column(db.Integer, unique= True)
    name = db.Column(db.String(50))
    price = db.Column(db.Float)

if __name__ == '__main__':
    manager.run()

