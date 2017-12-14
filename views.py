from OOPP import app, db
from models import Item, Cart, Comments
from flask import render_template, redirect, url_for, request
from flask_uploads import UploadSet, configure_uploads, IMAGES
from sqlalchemy.exc import IntegrityError

photos = UploadSet('photos', IMAGES)

app.config['UPLOADED_PHOTOS_DEST'] = '////Users/raymondtay/PycharmProjects/OOPP/static/img/item'
configure_uploads(app, photos)

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

@app.route('/test/<int:item_id>')
def test_cart1(item_id):
    cartid = Cart.query.filter_by(item_id=item_id).first()
    print(cartid)
    print(cartid.name)

    return ('success')

@app.route('/shop/<int:item_id>/add')
def addCart(item_id):

    try:
        items = Item.query.filter_by(id=item_id).first()
        new_item = Cart(item_id=items.id, name=items.name, quantity=1, price=items.price, subtotal=items.price)
        db.session.add(new_item)
        db.session.commit()

    except IntegrityError:
        db.session.rollback()
        items = Item.query.filter_by(id=item_id).first()
        carts = Cart.query.filter_by(id=item_id).first()
        carts.quantity += 1
        carts.subtotal = carts.quantity*carts.price
        db.session.commit()




    return redirect(url_for('shop'))

    # # item1 = Item.query.filter_by(id=item_id).first()
    # # quantity = 1
    # # subtotal = item1.price
    # # cart = Cart(item_id=item_id, name=item1.name, quantity=quantity, price=item1.price, subtotal=subtotal)
    # # db.session.add(cart)
    # # db.session.commit()
    #
    # check = Cart.query.filter_by(item_id = item_id).all()
    # cartid = Cart.query.filter_by(item_id=item_id).first()
    # print(cartid)
    # if check is None:
    #     cartids = Cart.query.filter_by(item_id=item_id).first()
    #     item1 = Item.query.filter_by(id=item_id).first()
    #     quantity = 1
    #     subtotal = item1.price
    #     cart = Cart(item_id=item_id, name=item1.name, quantity=quantity, price=item1.price, subtotal=subtotal)
    #     db.session.add(cart)
    #     db.session.commit()
    # else:
    #     cartname = cartid.name
    #     cartitem = Cart.query.filter_by(name=cartname).first()
    #     cartitem.quantity += 1
    #     cartitem.subtotal = cartitem.price * cartitem.quantity
    #     db.session.commit()
    #
    # return redirect(url_for('shop'))



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
    category = request.form['category']
    calories = request.form['calories']

    item = Item(name=name, info=info, price=price, description=description, category=category, calories=calories)

    db.session.add(item)
    db.session.commit()

    if request.method == 'POST' and 'image' in request.files:
        img = request.files['image']
        img.filename = str(item.id)+".jpg"
        filename = photos.save(img)
        return redirect(url_for('adminadd'))

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
     