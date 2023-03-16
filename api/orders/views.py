from flask_restx import Namespace, Resource, fields
from ..models.orders import Order
from http import HTTPStatus
from flask_jwt_extended import jwt_required, get_jwt_identity
from ..models.users import User
from ..utils import db


# Resource allows to do something like methodview(smorest)

# Namespace is same as blueprint(smorest)
order_namespace = Namespace('orders', description='name space for orders')



# For sterialization(Order)
order_model = order_namespace.model(
    'Order', {
        'id': fields.Integer(),
        'size': fields.String(
            required=True, description='Size of order', enum= ['SMALL', 'MEDIUM', 'LARGE', 'EXTRA_LARGE']
        ),
        'order_status': fields.String(
            required=True, description='Status of order', enum= ['PENDING', 'IN_TRANSIT', 'DELIVERED',]
        ),
        'flavour': fields.String(required=True, description='Order flavour'),
        'quantity': fields.Integer(required=True, description='Quantity of order')
    }
)




# For sterialization(OrderStatus)
order_status_model = order_namespace.model(
    'OrderStatus', {
        'order_status': fields.String(
            required=True, description='Status of order', enum= ['PENDING', 'IN_TRANSIT', 'DELIVERED',]
        )
    }
)





@order_namespace.route('/orders')
class OrderGetCreate(Resource):

    # @order_namespace.doc is for Swagger UI Documentation for frontend guys
    @jwt_required()
    @order_namespace.marshal_with(order_model)
    @order_namespace.doc(
        description="Get all orders",
    )
    def get(self):
        """
        Get all orders
        
        """
        orders = Order.query.all()

        return orders, HTTPStatus.OK


    @order_namespace.expect(order_model)
    @order_namespace.marshal_with(order_model)
    @order_namespace.doc(
        description="Place an order"
    )
    @jwt_required()
    def post(self):
        """
        Create an order
    
        """

        # To get user of order
        username = get_jwt_identity()
        current_user = User.query.filter_by(username=username).first()

        data = order_namespace.payload # Can use this instead of request.get_json()

        new_order = Order(
            size= data['size'],
            quantity = data['quantity'],
            flavour = data['flavour']   
        )

        new_order.user = current_user

        new_order.save()

        return new_order, HTTPStatus.CREATED




@order_namespace.route('/order/<int:order_id>')
class GetUpdateDelete(Resource):
 
    @order_namespace.marshal_with(order_model)
    @order_namespace.doc(
        description="Get an order by ID"
    )
    @jwt_required()
    def get(self, order_id):
        """
        Get an order by ID
   
        """
        order = Order.get_by_id(order_id)

        return order, HTTPStatus.OK


    @order_namespace.expect(order_model)
    @order_namespace.marshal_with(order_model)
    @order_namespace.doc(
        description="Update an order by ID"
    )
    @jwt_required()
    def put(self, order_id):
        """
        Update an order by ID

        """
        order_to_update = Order.get_by_id(order_id)

        data = order_namespace.payload

        order_to_update.quantity = data["quantity"] 
        order_to_update.size = data["size"]
        order_to_update.flavour = data["flavour"]


        db.session.commit()

        return order_to_update, HTTPStatus.OK



    @jwt_required()
    @order_namespace.doc(
        description="Delete an order by ID"
    )
    def delete(self, order_id):
        """
        Delete an order by ID 

        """ 
        order_to_delete = Order.get_by_id(order_id)

        current_user = get_jwt_identity()
        user = User.query.filter_by(username=current_user).first()
        user_id = user.id

        user = order_to_delete.customer

        if user_id == user:
            db.session.delete(order_to_delete)
            db.session.commit()

            return {"message":"Order Deleted"}, HTTPStatus.OK

        else:
            return {"message":"Unauthorized Access"}


    
@order_namespace.route('/user/<int:user_id>/order/<int:order_id>')
class GetSpecificOrderByUser(Resource):

    @jwt_required()
    @order_namespace.marshal_with(order_model)
    @order_namespace.doc(
        description="Get a specific order by User ID and order ID"
    )
    def get(self, user_id, order_id):
        """
        Get specific order by user ID and order ID

        """
        user = User.get_by_id(user_id)

        order = Order.query.filter_by(id=order_id).filter_by(user=user).first()
       
        return order, HTTPStatus.OK



    
@order_namespace.route('/user/<int:user_id>/orders')
class UserOrders(Resource):

    @jwt_required()
    @order_namespace.marshal_list_with(order_model)
    @order_namespace.doc(
        description="Get all orders by a user through ID"
    )
    def get(self, user_id):
        """
        Get all orders by a user through ID

        """
        user = User.get_by_id(user_id)

        orders = user.orders

        return orders, HTTPStatus.OK


   
@order_namespace.route('/order/status/<int:order_id>')
class UpdateOrdersStatus(Resource):

    @order_namespace.expect(order_status_model)
    @order_namespace.marshal_with(order_model)
    @order_namespace.doc(
        description="Update the status of an order"
    )
    @jwt_required()
    def patch(self, order_id):
        """
        Update an order status

        """
        data = order_namespace.payload

        order_to_update = Order.get_by_id(order_id)

        order_to_update.order_status = data["order_status"]

        db.session.commit()

        return order_to_update, HTTPStatus.OK
