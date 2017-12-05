from flask import Flask, render_template, redirect
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.sql import select
from flask_admin import Admin
from flask_admin.contrib.sqla import ModelView
from models import Item, Cart

app = Flask(__name__)
admin = Admin(app, name = 'LifeStyle28', template_mode = 'bootstrap3')
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///db/database.db'
app.secret_key = "development-key"

db = SQLAlchemy(app)
admin.add_view(ModelView(Item, db.session))

@app.route('/')
def shopping():
    items = Item.query.all()
    cart = Cart.query.all()
    return render_template('shopping.html', items=items, cart=cart)

@app.route('/add/<int:id>')
def add(id):
    items = Item.query.all()
    itemz = Item.query.filter_by(id=id).first()
    addtocart = Cart(itemid = id, name=itemz.name, price=itemz.price)
    db.session.add(addtocart)
    db.session.commit()
    cart = Cart.query.all()
    return render_template('shopping.html', items=items, cart=cart)

@app.route('/delete')
def delete():
    db.session.query(Cart).delete()
    db.session.commit()
    items = Item.query.all()
    return render_template('shopping.html', items=items)

if __name__ == '__main__':
    app.run(debug=True)
