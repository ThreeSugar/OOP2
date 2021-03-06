from flask import Flask, url_for
from models import db, User
import unittest
from flask_testing import TestCase
from flask_sqlalchemy import SQLAlchemy
from io import BytesIO




class MyTest(TestCase):

    def create_app(self):
        # pass in test configuration
        app = Flask(__name__)
        app.config['TESTING'] = True
        app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///db/test.db'
        app.secret_key = "development-key"
        db.init_app(app)
        return app

    def setUp(self):
        db.create_all()

    def tearDown(self):
        db.session.remove()
        db.drop_all()

    def test_user(self):
        user = User()
        db.session.add(user)
        db.session.commit()
        # this works
        assert user in db.session

class TestUpload(MyTest):
    def test_uploads(self):
        #request.info
        #junit
        data = dict(
        file=(BytesIO(b'My file contents'), "video.mp4"))
        response = self.client.post(url_for('upload'), content_type='multipart/form-data', data=data)
        assert response
       


if __name__ == '__main__':
    unittest.main()