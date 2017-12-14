from OOPP import db, admin
from flask_admin.contrib.sqla import ModelView

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

class ItemView(ModelView):
        form_choices = {
            'category': [
                ('Dairy', 'Dairy'),
                ('Meat', 'Meat'),
                ('Dry/Baking Goods', 'Dry/Baking Goods'),
                ('Produce', 'Produce')
            ]
        }
admin.add_view(ItemView(Item, db.session))
admin.add_view(ModelView(Cart, db.session))
admin.add_view(ModelView(Comments, db.session))

