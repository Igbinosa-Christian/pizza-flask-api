# pip install pytest to run test

import unittest
from .. import create_app
from ..config.config import config_dict
from ..utils import db
from werkzeug.security import generate_password_hash
from ..models.users import User

class UserTestCase(unittest.TestCase):

    def setUp(self):
        self.app = create_app(config=config_dict['test'])

        # To allow us use context
        self.appctx = self.app.app_context()

        # To push data to database
        self.appctx.push()

        # To work with test client
        self.client = self.app.test_client()

        db.create_all()

        

    # To reset everything before running setUp again
    def tearDown(self):
        db.drop_all()

        self.appctx.pop()

        self.app = None

        self.client = None


        
    def test_user_registration(self):
        data = {
            "username": "TestUser",
            "email": "test@gmail.com",
            "password": "password"
        }

        response = self.client.post('/auth/signup', json=data)

        user = User.query.filter_by(email='test@gmail.com').first()

        assert user.username == 'TestUser'


        assert response.status_code == 201



    def test_user_login(self):
        data = {
            "email": "test@gmail.com",
            "password": "password"
        }

        response = self.client.post('/auth/login', json=data)

        assert response.status_code == 200


    
    