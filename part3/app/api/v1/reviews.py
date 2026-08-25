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


review_update_model = api.model('ReviewUpdate', {
    'text': fields.String(
        description='Text of the review'
    ),
    'rating': fields.Integer(
        description='Rating from 1 to 5'
    )
})


@api.route('/')
class ReviewList(Resource):
    @jwt_required()
    @api.expect(review_model)
    @api.response(201, 'Review successfully created')
    @api.response(400, 'Invalid input data')
    @api.response(401, 'Authentication required')
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

    @api.response(200, 'List of reviews retrieved successfully')
    def get(self):
        """Retrieve a list of all reviews."""
        reviews = facade.get_all_reviews()

        return [
            {
                'id': review.id,
                'text': review.text,
                'rating': review.rating,
                'user_id': review.user_id,
                'place_id': review.place_id
            }
            for review in reviews
        ], 200


@api.route('/<string:review_id>')
class ReviewResource(Resource):
    @api.response(200, 'Review details retrieved successfully')
    @api.response(404, 'Review not found')
    def get(self, review_id):
        """Retrieve a review by ID."""
        review = facade.get_review(review_id)

        if not review:
            return {'error': 'Review not found'}, 404

        return {
            'id': review.id,
            'text': review.text,
            'rating': review.rating,
            'user_id': review.user_id,
            'place_id': review.place_id
        }, 200

    @jwt_required()
    @api.expect(review_update_model)
    @api.response(200, 'Review updated successfully')
    @api.response(400, 'Invalid input data')
    @api.response(401, 'Authentication required')
    @api.response(404, 'Review not found')
    def put(self, review_id):
        """Update a review."""
        review = facade.get_review(review_id)

        if not review:
            return {'error': 'Review not found'}, 404

        review_data = api.payload or {}

        try:
            updated_review = facade.update_review(
                review_id,
                review_data
            )
        except (ValueError, TypeError) as e:
            return {'error': str(e)}, 400

        return {
            'id': updated_review.id,
            'text': updated_review.text,
            'rating': updated_review.rating,
            'user_id': updated_review.user_id,
            'place_id': updated_review.place_id
        }, 200

    @jwt_required()
    @api.response(200, 'Review deleted successfully')
    @api.response(401, 'Authentication required')
    @api.response(404, 'Review not found')
    def delete(self, review_id):
        """Delete a review."""
        review = facade.get_review(review_id)

        if not review:
            return {'error': 'Review not found'}, 404

        facade.delete_review(review_id)

        return {'message': 'Review deleted successfully'}, 200