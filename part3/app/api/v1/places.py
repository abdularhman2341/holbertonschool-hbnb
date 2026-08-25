from flask_jwt_extended import (
    get_jwt,
    get_jwt_identity,
    jwt_required
)
from flask_restx import Namespace, Resource, fields
from app.services.facade import HBnBFacade


api = Namespace('places', description='Place operations')
facade = HBnBFacade()


place_model = api.model('Place', {
    'title': fields.String(
        required=True,
        description='Title of the place'
    ),
    'description': fields.String(
        description='Description of the place'
    ),
    'price': fields.Float(
        required=True,
        description='Price per night'
    ),
    'latitude': fields.Float(
        required=True,
        description='Latitude of the place'
    ),
    'longitude': fields.Float(
        required=True,
        description='Longitude of the place'
    ),
    'amenities': fields.List(
        fields.String,
        required=True,
        description='List of amenity IDs'
    )
})


@api.route('/')
class PlaceList(Resource):
    @jwt_required()
    @api.expect(place_model)
    @api.response(201, 'Place successfully created')
    @api.response(400, 'Invalid input data')
    @api.response(401, 'Authentication required')
    def post(self):
        """Register a new place."""
        place_data = api.payload or {}

        place_data['owner_id'] = get_jwt_identity()

        try:
            new_place = facade.create_place(place_data)
        except (ValueError, TypeError) as e:
            return {'error': str(e)}, 400

        return {
            'id': new_place.id,
            'title': new_place.title,
            'description': new_place.description,
            'price': new_place.price,
            'latitude': new_place.latitude,
            'longitude': new_place.longitude,
            'owner_id': new_place.owner_id
        }, 201

    @api.response(200, 'List of places retrieved successfully')
    def get(self):
        """Retrieve a list of all places."""
        places = facade.get_all_places()

        return [
            {
                'id': place.id,
                'title': place.title,
                'price': place.price,
                'latitude': place.latitude,
                'longitude': place.longitude
            }
            for place in places
        ], 200


@api.route('/<string:place_id>')
class PlaceResource(Resource):
    @api.response(200, 'Place details retrieved successfully')
    @api.response(404, 'Place not found')
    def get(self, place_id):
        """Retrieve details for a specific place."""
        place = facade.get_place(place_id)

        if not place:
            return {'error': 'Place not found'}, 404

        owner = facade.get_user(place.owner_id)
        reviews = facade.get_reviews_by_place(place_id)

        return {
            'id': place.id,
            'title': place.title,
            'description': place.description,
            'price': place.price,
            'latitude': place.latitude,
            'longitude': place.longitude,
            'owner': {
                'id': owner.id,
                'first_name': owner.first_name,
                'last_name': owner.last_name
            } if owner else None,
            'amenities': [
                {
                    'id': amenity.id,
                    'name': amenity.name
                }
                for amenity in place.amenities
            ],
            'reviews': [
                {
                    'id': review.id,
                    'text': review.text,
                    'rating': review.rating,
                    'user_id': review.user_id
                }
                for review in reviews
            ]
        }, 200

    @jwt_required()
    @api.expect(place_model)
    @api.response(200, 'Place updated successfully')
    @api.response(400, 'Invalid input data')
    @api.response(401, 'Authentication required')
    @api.response(403, 'Unauthorized action')
    @api.response(404, 'Place not found')
    def put(self, place_id):
        """Update a place's information."""
        place = facade.get_place(place_id)

        if not place:
            return {'error': 'Place not found'}, 404

        current_user = get_jwt_identity()
        claims = get_jwt()
        is_admin = claims.get('is_admin', False)

        if not is_admin and place.owner_id != current_user:
            return {'error': 'Unauthorized action'}, 403

        place_data = api.payload or {}

        place_data.pop('owner_id', None)

        try:
            facade.update_place(place_id, place_data)
        except (ValueError, TypeError) as e:
            return {'error': str(e)}, 400

        return {'message': 'Place updated successfully'}, 200