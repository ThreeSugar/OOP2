from OOPP import app, db
from models import Item, Cart, Comments
from flask import render_template, redirect, url_for, request

@app.context_processor
def utility_processor():
    def show_cart_price():
        price = 0
        cart = Cart.query.all()
        for c in cart:
            price += c.subtotal

        return "{0:.2f}".format(price)
    def cart_count():
        count = 0
        cart = Cart.query.all()
        for c in cart:
            count += 1
        return count
    return dict(show_cart_price=show_cart_price, cart_count=cart_count)

@app.route('/')
def index():
    return render_template("index.html")

@app.route('/shop')
def shop():
    items = Item.query.all()

    return render_template("shop.html", items=items)

@app.route('/shop/<int:item_id>/add')
def addCart(item_id):

    item1 = Item.query.filter_by(id=item_id).first()
    quantity = 1
    subtotal = item1.price
    cart = Cart(item_id=item_id, name=item1.name, quantity=quantity, price=item1.price, subtotal=subtotal)
    db.session.add(cart)
    db.session.commit()

    # check = Cart.query.filter(item_id == item_id).all()
    # cartid = Cart.query.filter_by(item_id=item_id).first()
    # if check is None:
    #     item1 = Item.query.filter_by(id=item_id).first()
    #     quantity = 1
    #     subtotal = item1.price
    #     cart = Cart(item_id=item_id, name=item1.name, quantity=quantity, price=item1.price, subtotal=subtotal)
    #     db.session.add(cart)
    #     db.session.commit()
    # else:
    #     cartitem = Cart.query.filter_by(name=cartid.name).first()
    #     cartitem.quantity += 1
    #     cartitem.subtotal = cartitem.price * cartitem.quantity
    #     db.session.commit()

    return redirect(url_for('shop'))

@app.route('/cart')
def cart():
    cart = Cart.query.all()

    return render_template("cart.html", cart=cart)

# @app.route('/cart/update/<int:item_id>')
# def update(item_id):
#     cartid = Cart.query.filter_by(item_id=item_id).first()
#     i = cartid.quantity
#
#
#     for c in Cart:
#         cartid = Cart.query.filter_by(item_id=item_id).first()
#
#
#     return render_template("cart.html")

@app.route('/adminadd')
def adminadd():
    return render_template("adminadd.html")

@app.route('/addItem', methods=['POST'])
def addItem():
    name = request.form['name']
    info = request.form['info']
    price = request.form['price']
    description = request.form['description']


    item = Item(name=name, info=info, price=price, description=description)

    db.session.add(item)
    db.session.commit()

    return redirect(url_for('shop'))

# @app.route('/view/<id>')
# def viewitem(id):
#      item =Cart.query.filter_by(itemid=id).first()
#      itemname = item.name
#      render template(template.html, itemname=item)


@app.route('/item/<int:item_id>')
def item(item_id):
    item = Item.query.filter_by(id=item_id).one()

    comment = Comments.query.filter(Comments.item_id == item_id).all()

    return render_template('item.html', item=item, comment=comment)

@app.route('/item/<int:item_id>/add', methods=['POST'])
def addComment(item_id):

    name = request.form['name']
    rating = request.form['rating']
    comment = request.form['comment']

    addComment = Comments(item_id=item_id, name=name, rating=rating, comment=comment)
    db.session.add(addComment)
    db.session.commit()

    return redirect(url_for('item', item_id=item_id))

@app.route('/adminview')
def adminview():
    return render_template("adminview.html")

@app.route('/test')
def test_cart():
     return "test placeholder."
     