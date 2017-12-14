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

@app.route('/shop/filter/<category>')
def filter(category):
    filter = Item.query.filter(Item.category == category).all()
    return render_template("shop.html", items=filter)

@app.route('/shop/<int:item_id>/add')
def addCart(item_id):

    try:
        items = Item.query.filter_by(id=item_id).first()
        new_item = Cart(item_id=items.id, name=items.name, quantity=1, price=items.price, subtotal=items.price)
        db.session.add(new_item)
        db.session.commit()

    except IntegrityError:
        db.session.rollback()
        carts = Cart.query.filter_by(item_id=item_id).first()
        carts.quantity += 1
        carts.subtotal = "{0:.2f}".format(carts.quantity*carts.price)
        db.session.commit()

    return redirect(url_for('shop'))

@app.route('/shop/<int:item_id>/delete')
def deleteCart(item_id):
    items = Cart.query.filter_by(item_id=item_id).first()
    db.session.delete(items)
    db.session.commit()
    return redirect(url_for('cart'))

@app.route('/shop/<int:item_id>/update', methods=['POST'])
def updateCart(item_id):
    items = Cart.query.filter_by(item_id=item_id).first()
    quantity = request.form['newquantity']
    items.quantity = quantity
    items.subtotal = "{0:.2f}".format(float(items.quantity)*items.price)
    db.session.commit()
    return redirect(url_for('cart'))

@app.route('/cart')
def cart():
    cart = Cart.query.all()

    return render_template("cart.html", cart=cart)

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

    item = Item(name=name, info=info, price=price, description=description, category=category, calories=calories, totalratings=0)

    db.session.add(item)
    db.session.commit()

    if request.method == 'POST' and 'image' in request.files:
        img = request.files['image']
        img.filename = str(item.id)+".jpg"
        filename = photos.save(img)
        return redirect(url_for('adminadd'))

    return redirect(url_for('shop'))

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

    item = Item.query.filter_by(id=item_id).first()
    count = Comments.query.filter_by(item_id=item_id).count()

    item.totalratings = int(item.totalratings)+int(rating)
    item.rating = int(item.totalratings / count)
    item.rating_count = count

    db.session.commit()

    return redirect(url_for('item', item_id=item_id))

@app.route('/adminview')
def adminview():
    return render_template("adminview.html")

@app.route('/test')
def test_cart():
     return "test placeholder."
     