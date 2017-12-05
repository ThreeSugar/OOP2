from flask import Flask
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)
db = SQLAlchemy(app)

class Item(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50))
    info = db.Column(db.String(50))
    price = db.Column(db.Float)
    description = db.Column(db.Text(50))

    def __init__(self, name = '', info = '', price= '', description= ''):
        self.name = name
        self.info = info
        self.price = price
        self.description = description
        

class Cart(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    itemid = db.Column(db.Integer, unique= True)
    name = db.Column(db.String(50))
    price = db.Column(db.Float)