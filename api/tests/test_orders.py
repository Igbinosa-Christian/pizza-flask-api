# pip install pytest to run test

import unittest
from .. import create_app
from ..config.config import config_dict
from ..utils import db
from flask_jwt_extended import create_access_token
from ..models.users import User
from ..models.orders import Order


class OrderTestCase(unittest.TestCase):

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



    # Test to get all orders
    def test_get_all_orders(self):

        # for jwt_required
        token = create_access_token(identity='TestUser')

        headers = {
            "Authorization": f"Bearer {token}"
        }

        response = self.client.get('orders/orders', headers=headers)

        assert  response.status_code == 200

        assert response.json == []



    # Test to create an order
    def test_create_order(self):

        data = {
            "size": "SMALL",
            "quantity": 1,
            "flavour": "Apple"
        }

        # for jwt_required
        token = create_access_token(identity='TestUser')

        headers = {
            "Authorization": f"Bearer {token}"
        }


        response = self.client.post('orders/orders', json=data, headers=headers)

        assert  response.status_code == 201

        orders = Order.query.all()

        assert len(orders) == 1



    
    # Test for get an order by ID
    def test_get_single_order(self):

        data = {
            "size": "SMALL",
            "quantity": 1,
            "flavour": "Apple"
        }


        # for jwt_required
        token = create_access_token(identity='TestUser')

        headers = {
            "Authorization": f"Bearer {token}"
        }
        
        response1 = self.client.post('orders/orders', json=data, headers=headers)
        response = self.client.get('orders/order/1', headers=headers)

        assert response.status_code == 200



       

