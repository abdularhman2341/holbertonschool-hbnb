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