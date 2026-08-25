from flask_jwt_extended import get_jwt, jwt_required
from flask_restx import Namespace, Resource, fields
from app.services.facade import HBnBFacade


api = Namespace('amenities', description='Amenity operations')
facade = HBnBFacade()


amenity_model = api.model('Amenity', {
    'name': fields.String(
        required=True,
        description='Name of the amenity'
    )
})


@api.route('/')
class AmenityList(Resource):
    @jwt_required()
    @api.expect(amenity_model, validate=True)
    @api.response(201, 'Amenity successfully created')
    @api.response(400, 'Invalid input data')
    @api.response(401, 'Authentication required')
    @api.response(403, 'Admin privileges required')
    def post(self):
        """Create a new amenity."""
        claims = get_jwt()

        if not claims.get('is_admin', False):
            return {'error': 'Admin privileges required'}, 403

        amenity_data = api.payload or {}

        try:
            amenity = facade.create_amenity(amenity_data)
        except (ValueError, TypeError) as e:
            return {'error': str(e)}, 400

        return {
            'id': amenity.id,
            'name': amenity.name
        }, 201

    def get(self):
        """Retrieve all amenities."""
        amenities = facade.get_all_amenities()

        return [
            {
                'id': amenity.id,
                'name': amenity.name
            }
            for amenity in amenities
        ], 200


@api.route('/<string:amenity_id>')
class AmenityResource(Resource):
    def get(self, amenity_id):
        """Retrieve an amenity by ID."""
        amenity = facade.get_amenity(amenity_id)

        if not amenity:
            return {'error': 'Amenity not found'}, 404

        return {
            'id': amenity.id,
            'name': amenity.name
        }, 200

    @jwt_required()
    @api.expect(amenity_model, validate=True)
    @api.response(200, 'Amenity updated successfully')
    @api.response(400, 'Invalid input data')
    @api.response(401, 'Authentication required')
    @api.response(403, 'Admin privileges required')
    @api.response(404, 'Amenity not found')
    def put(self, amenity_id):
        """Update an amenity."""
        claims = get_jwt()

        if not claims.get('is_admin', False):
            return {'error': 'Admin privileges required'}, 403

        amenity = facade.get_amenity(amenity_id)

        if not amenity:
            return {'error': 'Amenity not found'}, 404

        amenity_data = api.payload or {}

        try:
            updated_amenity = facade.update_amenity(
                amenity_id,
                amenity_data
            )
        except (ValueError, TypeError) as e:
            return {'error': str(e)}, 400

        return {
            'id': updated_amenity.id,
            'name': updated_amenity.name
        }, 200