from OOPP import db, admin
from flask_admin.contrib.sqla import ModelView

class Item(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50))
    info = db.Column(db.String(50))
    price = db.Column(db.Float)
    description = db.Column(db.Text(50))
    calories = db.Column(db.Integer)
    category = db.Column(db.String(50))

class Cart(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    item_id = db.Column(db.Integer, db.ForeignKey('Item.id'))
    quantity = db.Column(db.Integer)

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

