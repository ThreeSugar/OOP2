import os
import unittest

from flask import Flask
from models import User
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.exc import IntegrityError

class TestCase(unittest.TestCase):
    def setUp(self):
        app = Flask(__name__)
        with app.app_context():
            db = SQLAlchemy(app)
            app.config['TESTING'] = True
            app.config['WTF_CSRF_ENABLED'] = False
            app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///db/database.db'
            self.app = app.test_client()
            db.create_all()

    def tearDown(self):
        app = Flask(__name__)
        db = SQLAlchemy(app)        
        db.session.remove
        db.drop_all()

    def test_main_page(self):
        response = self.app.get('/', follow_redirects=True)
        self.assertEqual(response.status_code, 200)

    # def test_user(self):
    #     assert User.query.get(int(uid))


if __name__ == '__main__':
    unittest.main()

