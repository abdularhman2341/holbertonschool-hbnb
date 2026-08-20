from flask_restx import Namespace, Resource
from app.services.facade import HBnBFacade

api = Namespace('places', description='Place operations')
facade = HBnBFacade()

@api.route('/')
class PlaceList(Resource):
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