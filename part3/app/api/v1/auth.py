from flask import Blueprint, request, jsonify
from flask_jwt_extended import create_access_token
from app.services.facade import HBnBFacade

auth_bp = Blueprint('auth', __name__)
facade = HBnBFacade()


@auth_bp.route('/login', methods=['POST'])
def login():
    """Authenticate user and return JWT access token."""
    data = request.get_json()
    if not data or not data.get('email') or not data.get('password'):
        return jsonify({'error': 'Missing email or password'}), 400

    user = facade.get_user_by_email(data['email'])
    if not user or not user.verify_password(data['password']):
        return jsonify({'error': 'Invalid credentials'}), 401

    access_token = create_access_token(
    identity=user.id,
    additional_claims={"is_admin": user.is_admin}
)
    return jsonify({'access_token': access_token}), 200
