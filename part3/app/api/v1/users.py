from flask_jwt_extended import get_jwt_identity, jwt_required
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
    )
})


user_update_model = api.model('UserUpdate', {
    'first_name': fields.String(description='First name'),
    'last_name': fields.String(description='Last name'),
    'email': fields.String(description='Email address'),
    'password': fields.String(description='User password')
})


@api.route('/')
class UserList(Resource):
    @api.expect(user_model, validate=True)
    def post(self):
        """Register a new user."""
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
            'email': user.email
        }, 201

    def get(self):
        """Retrieve all users without password field."""
        users = facade.get_all_users()

        return [
            {
                'id': user.id,
                'first_name': user.first_name,
                'last_name': user.last_name,
                'email': user.email
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
            'email': user.email
        }, 200

    @jwt_required()
    @api.expect(user_update_model)
    @api.response(200, 'User updated successfully')
    @api.response(400, 'Invalid input data')
    @api.response(401, 'Authentication required')
    @api.response(403, 'Unauthorized action')
    @api.response(404, 'User not found')
    def put(self, user_id):
        """Update the authenticated user's information."""
        user = facade.get_user(user_id)

        if not user:
            return {'error': 'User not found'}, 404

        current_user = get_jwt_identity()

        if current_user != user_id:
            return {'error': 'Unauthorized action'}, 403

        data = api.payload or {}

        if 'email' in data or 'password' in data:
            return {
                'error': 'You cannot modify email or password'
            }, 400

        if 'is_admin' in data:
            return {'error': 'Unauthorized action'}, 403

        try:
            updated_user = facade.update_user(user_id, data)
        except (ValueError, TypeError) as e:
            return {'error': str(e)}, 400

        return {
            'id': updated_user.id,
            'first_name': updated_user.first_name,
            'last_name': updated_user.last_name,
            'email': updated_user.email
        }, 200