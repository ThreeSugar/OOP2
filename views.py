from OOPP import app, db
from models import Item
from flask import render_template, redirect, url_for, request

@app.route('/')
def index():
    return render_template("index.html")

@app.route('/item/<int:item_id>')
def item(item_id):
    item = Item.query.filter_by(id=item_id).one()

    return render_template('item.html', item=item)

@app.route('/adminadd')
def additem():
    return render_template("adminadd.html")

@app.route('/adminview')
def additem():
    return render_template("adminview.html")

@app.route('/testitem', methods=['POST'])
def testitem():
    name = request.form['name']
    info = request.form['info']
    price = request.form['price']
    description = request.form['description']

    item = Item(name=name, info=info, price=price, description=description)

    db.session.add(item)
    db.session.commit()

    return redirect(url_for('shop'))

@app.route('/shop')
def shop():
    items = Item.query.all()

    return render_template("shop.html", items=items)

@app.route('/cart')
def cart():
    return render_template("cart.html")
	
@app.route('/test')
def test_cart():
     return "test placeholder."
     