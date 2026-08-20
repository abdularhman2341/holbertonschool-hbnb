from flask_jwt_extended import get_jwt_identity, jwt_required
from flask_restx import Namespace, Resource, fields
from app.services.facade import HBnBFacade


api = Namespace('reviews', description='Review operations')

facade = HBnBFacade()

review_model = api.model('Review', {
    'text': fields.String(
        required=True,
        description='Text of the review'
    ),
    'rating': fields.Integer(
        required=True,
        description='Rating from 1 to 5'
    ),
    'place_id': fields.String(
        required=True,
        description='ID of the place'
    )
})


@api.route('/')
class ReviewList(Resource):
    @jwt_required()
    @api.expect(review_model)
    def post(self):
        """Create a review for a place."""
        review_data = api.payload or {}

        review_data['user_id'] = get_jwt_identity()

        try:
            new_review = facade.create_review(review_data)
        except (ValueError, TypeError) as e:
            return {'error': str(e)}, 400

        return {
            'id': new_review.id,
            'text': new_review.text,
            'rating': new_review.rating,
            'user_id': new_review.user_id,
            'place_id': new_review.place_id
        }, 201