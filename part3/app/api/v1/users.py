from flask_jwt_extended import (
    get_jwt,
    get_jwt_identity,
    jwt_required
)
from flask_restx import Namespace, Resource, fields
from app.services.facade import HBnBFacade


api = Namespace('users', description='User operations')
facade = HBnBFacade()


user_model = api.model('User', {
    'first_name': fields.String(
        required=True,
        description='First name'
    ),
    'last_name': fields.String(
        required=True,
        description='Last name'
    ),
    'email': fields.String(
        required=True,
        description='Email address'
    ),
    'password': fields.String(
        required=True,
        description='User password'
    ),
    'is_admin': fields.Boolean(
        description='Administrator status'
    )
})


user_update_model = api.model('UserUpdate', {
    'first_name': fields.String(description='First name'),
    'last_name': fields.String(description='Last name'),
    'email': fields.String(description='Email address'),
    'password': fields.String(description='User password'),
    'is_admin': fields.Boolean(description='Administrator status')
})


@api.route('/')
class UserList(Resource):
    @jwt_required()
    @api.expect(user_model, validate=True)
    @api.response(201, 'User successfully created')
    @api.response(400, 'Invalid input data')
    @api.response(401, 'Authentication required')
    @api.response(403, 'Admin privileges required')
    def post(self):
        """Create a new user as an administrator."""
        claims = get_jwt()

        if not claims.get('is_admin', False):
            return {'error': 'Admin privileges required'}, 403

        data = api.payload or {}

        existing_user = facade.get_user_by_email(data['email'])
        if existing_user:
            return {'error': 'Email already registered'}, 400

        try:
            user = facade.create_user(data)
        except (ValueError, TypeError) as e:
            return {'error': str(e)}, 400

        return {
            'id': user.id,
            'first_name': user.first_name,
            'last_name': user.last_name,
            'email': user.email,
            'is_admin': user.is_admin
        }, 201

    def get(self):
        """Retrieve all users without password field."""
        users = facade.get_all_users()

        return [
            {
                'id': user.id,
                'first_name': user.first_name,
                'last_name': user.last_name,
                'email': user.email,
                'is_admin': user.is_admin
            }
            for user in users
        ], 200


@api.route('/<string:user_id>')
class UserResource(Resource):
    def get(self, user_id):
        """Get user details by ID without password."""
        user = facade.get_user(user_id)

        if not user:
            return {'error': 'User not found'}, 404

        return {
            'id': user.id,
            'first_name': user.first_name,
            'last_name': user.last_name,
            'email': user.email,
            'is_admin': user.is_admin
        }, 200

    @jwt_required()
    @api.expect(user_update_model)
    @api.response(200, 'User updated successfully')
    @api.response(400, 'Invalid input data')
    @api.response(401, 'Authentication required')
    @api.response(403, 'Unauthorized action')
    @api.response(404, 'User not found')
    def put(self, user_id):
        """Update user information."""
        user = facade.get_user(user_id)

        if not user:
            return {'error': 'User not found'}, 404

        current_user = get_jwt_identity()
        claims = get_jwt()
        is_admin = claims.get('is_admin', False)
        data = api.payload or {}

        if not is_admin:
            if current_user != user_id:
                return {'error': 'Unauthorized action'}, 403

            if 'email' in data or 'password' in data:
                return {
                    'error': 'You cannot modify email or password'
                }, 400

            if 'is_admin' in data:
                return {
                    'error': 'Admin privileges required'
                }, 403

        if is_admin and 'email' in data:
            existing_user = facade.get_user_by_email(
                data['email']
            )

            if existing_user and existing_user.id != user_id:
                return {'error': 'Email already in use'}, 400

        try:
            updated_user = facade.update_user(user_id, data)
        except (ValueError, TypeError) as e:
            return {'error': str(e)}, 400

        return {
            'id': updated_user.id,
            'first_name': updated_user.first_name,
            'last_name': updated_user.last_name,
            'email': updated_user.email,
            'is_admin': updated_user.is_admin
        }, 200