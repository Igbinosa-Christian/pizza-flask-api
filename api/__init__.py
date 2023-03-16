from flask import Flask, abort
from flask_restx import Api
from .auth.views import auth_namespace
from .orders.views import order_namespace
from .config.config import config_dict
from .utils import db
from .models.orders import Order
from .models.users import User
from .models.blacklist import TokenBlocklist
from flask_migrate import Migrate
from flask_jwt_extended import JWTManager
from werkzeug.exceptions import NotFound # For error message
from http import HTTPStatus



def create_app(config=config_dict['dev']):
    app = Flask(__name__)

    # to configure our app to use dev/prod/test
    app.config.from_object(config)

    # to initialize our database
    db.init_app(app)

    # to manage our JWT
    jwt = JWTManager(app)

    @jwt.token_in_blocklist_loader
    def check_if_token_in_blocklist(jwt_header, jwt_payload):
        token_jti = jwt_payload['jti']

        check = TokenBlocklist.query.filter_by(jti=token_jti).first()

        if check:
            return True
        else:
            return False


    @jwt.revoked_token_loader
    def revoke_token_callback(jwt_header, jwt_payload):
        abort (401, description='User has been logged out, token revoked.')
    


    # to allow easy update of database
    migrate = Migrate(app, db)

    
    # Create field to input JWT Required(Bearer Token)
    authorizations = {
        "Bearer Auth":{
            "type": "apiKey",
            "in": "header",
            "name": "Authorization",
            "description": "Add a JWT token to the header for JWT Authoriation by doing Bearer JWT TOKEN"
        }
    }

    # Usually api=Api(app); other details are Swagger UI documentation
    api = Api(app,
              title= 'Pizza Delivery API',
              description= 'A Simple Pizza Delivery REST Api',
              authorizations=authorizations,
              security='Bearer Auth'
    )

    # Register namespaces
    api.add_namespace(order_namespace, path='/orders')
    api.add_namespace(auth_namespace, path='/auth')


    # To handle errors
    @api.errorhandler(NotFound)
    def not_found(error):
        return {"error":"URL Not Found"}, 404

    # to allow us connect to the database to create and do migration in the shell
    @app.shell_context_processor
    def make_shell_context():
        return {
            'db': db,
            'User': User,
            'Order': Order
        }

         # do flask shell after creating this in the terminal
         # do db.create_all()

    return app