from flask import request
from flask_restx import Namespace, Resource, fields
from ..models.users import User
from ..models.blacklist import TokenBlocklist
from werkzeug.security import check_password_hash, generate_password_hash
from http import HTTPStatus  # for server response
from ..utils import db
from flask_jwt_extended import create_access_token, create_refresh_token, jwt_required, get_jwt_identity, get_jwt
import redis # for logout
from flask import jsonify

# Resource allows to do something like methodview

# Namespace is same as blueprint
auth_namespace = Namespace('auth', description='name space for authentication')


# For sterialization(creating a user)
signup_model = auth_namespace.model(
    'Signup', {
        'username': fields.String(required=True, description='A username'),
        'email': fields.String(required=True, description='An email'),
        'password': fields.String(required=True, description='A password')
    }
)



# For sterialization(User)
user_model = auth_namespace.model(
    'User', {
        'id': fields.Integer(),
        'username': fields.String(required=True, description='A username'),
        'email': fields.String(required=True, description='An email'),
        'password_hash': fields.String(required=True, description='A password hash'),
        'is_active': fields.Boolean(description='Shows if user is active or not'),
        'is_staff': fields.Boolean(description='Shows if user is staff or not')
    }
)



# For sterialization(Login)
login_model = auth_namespace.model(
    'Login', {
        'email': fields.String(required=True, description='An email'),
        'password': fields.String(required=True, description='A password'),
    }
)


@auth_namespace.route('/signup')
class SignUp(Resource):

    @auth_namespace.expect(signup_model)
    @auth_namespace.doc(
        description="Create a User"
    )
    @auth_namespace.expect(signup_model)
    @auth_namespace.marshal_with(user_model)  # to sterialize new_user and be able to return it as json with user_with schema
    def post(self):
        """
        Create a user
        
        """
        data = request.get_json()

        new_user = User(
            username=data.get('username'), email=data.get('email'),
            password_hash=generate_password_hash(data.get('password'))
        )

        # save is a function to add user to db created in user model 
        new_user.save()

        return new_user, HTTPStatus.CREATED




@auth_namespace.route('/login')
class Login(Resource):

    @auth_namespace.expect(login_model)
    @auth_namespace.doc(
        description="Login a User"
    )
    def post(self):
        """
        Login user with JWT
        
        """

        data = request.get_json()

        email = data.get('email')
        password = data.get('password')

        user = User.query.filter_by(email=email).first()


        if (user is not None) and check_password_hash(user.password_hash, password):
            access_token = create_access_token(identity=user.username)
            refresh_token = create_refresh_token(identity=user.username)

            response = {
                'access_token': access_token,
                'refresh_token': refresh_token
            }

            return response, HTTPStatus.CREATED 



# To create a new token with same user identity
@auth_namespace.route('/refresh')
class Refresh(Resource):

    @jwt_required(refresh=True)
    def post(self):
        username = get_jwt_identity()

        access_token = create_access_token(identity=username)

        return {'access_token': access_token}, HTTPStatus.OK



@auth_namespace.route('/logout')
class Logout(Resource):


    @jwt_required(verify_type=False)
    def post(self):
        token = get_jwt()
        jti = token["jti"]
        ttype = token["type"]
        db.session.add(TokenBlocklist(jti=jti, type=ttype))
        db.session.commit()

        return jsonify(msg=f"{ttype.capitalize()} token successfully revoked")
 