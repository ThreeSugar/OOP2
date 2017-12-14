from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_admin import Admin


app = Flask(__name__)
app.config['SECRET_KEY'] = 'secretkey'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:////Users/raymondtay/PycharmProjects/OOPP/database.db'
db = SQLAlchemy(app)
admin = Admin(app)

from views import *

if __name__ == '__main__':
    app.run(debug=True)
