import re

from app.models.user import User
from app.models.amenity import Amenity
from app.models.place import Place
from app.models.review import Review
from app.persistence.repository import SQLAlchemyRepository
from app.services.repositories.user_repository import UserRepository


class HBnBFacade:
    def __init__(self):
        self.user_repo = UserRepository()
        self.amenity_repo = SQLAlchemyRepository(Amenity)
        self.place_repo = SQLAlchemyRepository(Place)
        self.review_repo = SQLAlchemyRepository(Review)

    @staticmethod
    def _validate_user_data(user_data, partial=False):
        """Validate user payload."""
        def has(field):
            return field in user_data

        if not partial or has('first_name'):
            first_name = user_data.get('first_name')
            if not first_name or not isinstance(first_name, str) \
                    or len(first_name) > 50:
                raise ValueError(
                    "first_name is required (max 50 characters)"
                )

        if not partial or has('last_name'):
            last_name = user_data.get('last_name')
            if not last_name or not isinstance(last_name, str) \
                    or len(last_name) > 50:
                raise ValueError(
                    "last_name is required (max 50 characters)"
                )

        if not partial or has('email'):
            email = user_data.get('email')
            if not email or not isinstance(email, str) \
                    or not re.match(
                        r"^[^@\s]+@[^@\s]+\.[^@\s]+$",
                        email
                    ):
                raise ValueError("A valid email is required")

        if not partial or has('password'):
            password = user_data.get('password')
            if not password or not isinstance(password, str):
                raise ValueError("password is required")

        if has('is_admin'):
            if not isinstance(user_data.get('is_admin'), bool):
                raise ValueError("is_admin must be a boolean")

    @staticmethod
    def _validate_amenity_data(amenity_data):
        """Validate amenity payload."""
        name = amenity_data.get('name')
        if not name or not isinstance(name, str) or len(name) > 50:
            raise ValueError("name is required (max 50 characters)")

    def _validate_place_data(self, place_data, partial=False):
        """Validate place payload.

        When partial is True (PUT), only the provided fields are checked.
        """
        def has(field):
            return field in place_data

        if not partial or has('title'):
            title = place_data.get('title')
            if not title or not isinstance(title, str) or len(title) > 100:
                raise ValueError("title is required (max 100 characters)")

        if not partial or has('price'):
            price = place_data.get('price')
            if not isinstance(price, (int, float)) \
                    or isinstance(price, bool) or price < 0:
                raise ValueError("price must be a non-negative number")

        if not partial or has('latitude'):
            latitude = place_data.get('latitude')
            if not isinstance(latitude, (int, float)) \
                    or isinstance(latitude, bool) \
                    or not -90 <= latitude <= 90:
                raise ValueError("latitude must be between -90 and 90")

        if not partial or has('longitude'):
            longitude = place_data.get('longitude')
            if not isinstance(longitude, (int, float)) \
                    or isinstance(longitude, bool) \
                    or not -180 <= longitude <= 180:
                raise ValueError("longitude must be between -180 and 180")

        if not partial or has('owner_id'):
            owner = self.get_user(place_data.get('owner_id'))
            if not owner:
                raise ValueError("owner_id does not match any existing user")

        if has('amenities'):
            amenities = place_data.get('amenities')
            if not isinstance(amenities, list):
                raise ValueError("amenities must be a list of amenity IDs")
            for amenity_id in amenities:
                if not self.get_amenity(amenity_id):
                    raise ValueError(
                        "amenity '{}' does not exist".format(amenity_id))

    # ----------------------------- User -----------------------------------
    def create_user(self, user_data):
        self._validate_user_data(user_data)
        user = User(**user_data)
        self.user_repo.add(user)
        return user

    def get_user(self, user_id):
        return self.user_repo.get(user_id)

    def get_user_by_email(self, email):
        return self.user_repo.get_user_by_email(email)

    def get_all_users(self):
        return self.user_repo.get_all()

    def update_user(self, user_id, user_data):
        user = self.user_repo.get(user_id)
        if not user:
            return None

        self._validate_user_data(user_data, partial=True)

        data = dict(user_data)
        password = data.pop('password', None)

        if password is not None:
            user.hash_password(password)

        return self.user_repo.update(user_id, data)

    # ---------------------------- Amenity ----------------------------------
    def create_amenity(self, amenity_data):
        self._validate_amenity_data(amenity_data)
        amenity = Amenity(**amenity_data)
        self.amenity_repo.add(amenity)
        return amenity

    def get_amenity(self, amenity_id):
        return self.amenity_repo.get(amenity_id)

    def get_all_amenities(self):
        return self.amenity_repo.get_all()

    def update_amenity(self, amenity_id, amenity_data):
        amenity = self.amenity_repo.get(amenity_id)
        if not amenity:
            return None
        self._validate_amenity_data(amenity_data)
        return self.amenity_repo.update(amenity_id, amenity_data)

    def delete_amenity(self, amenity_id):
        """Delete an amenity by ID."""
        amenity = self.amenity_repo.get(amenity_id)
        if not amenity:
            return None

        self.amenity_repo.delete(amenity_id)
        return amenity

    # ----------------------------- Place ------------------------------------
    def create_place(self, place_data):
        """Create and persist a place with its amenities."""
        self._validate_place_data(place_data)
        data = dict(place_data)
        amenity_ids = data.pop('amenities', [])
        data.setdefault('description', "")

        place = Place(**data)
        place.amenities = [
            self.get_amenity(amenity_id)
            for amenity_id in amenity_ids
        ]

        self.place_repo.add(place)
        return place

    def get_place(self, place_id):
        return self.place_repo.get(place_id)

    def get_all_places(self):
        return self.place_repo.get_all()

    def update_place(self, place_id, place_data):
        """Update a place and its amenities."""
        place = self.place_repo.get(place_id)
        if not place:
            return None

        self._validate_place_data(place_data, partial=True)
        data = dict(place_data)
        amenity_ids = data.pop('amenities', None)

        if amenity_ids is not None:
            place.amenities = [
                self.get_amenity(amenity_id)
                for amenity_id in amenity_ids
            ]

        return self.place_repo.update(place_id, data)

    def delete_place(self, place_id):
        """Delete a place by ID."""
        place = self.place_repo.get(place_id)
        if not place:
            return None

        self.place_repo.delete(place_id)
        return place

    # ----------------------------- Review -----------------------------------
    def _validate_review_data(self, review_data, partial=False):
        """Validate review payload."""

        def has(field):
            return field in review_data

        if not partial or has('text'):
            text = review_data.get('text')
            if not text or not isinstance(text, str):
                raise ValueError("text is required")

        if not partial or has('rating'):
            rating = review_data.get('rating')
            if not isinstance(rating, int) or isinstance(rating, bool) \
                    or not 1 <= rating <= 5:
                raise ValueError(
                    "rating must be an integer between 1 and 5"
                )

        if not partial or has('user_id'):
            user = self.get_user(review_data.get('user_id'))
            if not user:
                raise ValueError(
                    "user_id does not match any existing user"
                )

        if not partial or has('place_id'):
            place = self.get_place(review_data.get('place_id'))
            if not place:
                raise ValueError(
                    "place_id does not match any existing place"
                )

    def create_review(self, review_data):
        """Create and persist a review."""
        self._validate_review_data(review_data)
        review = Review(**review_data)
        self.review_repo.add(review)
        return review

    def get_review(self, review_id):
        return self.review_repo.get(review_id)

    def get_all_reviews(self):
        return self.review_repo.get_all()

    def get_reviews_by_place(self, place_id):
        return [
            review for review in self.review_repo.get_all()
            if review.place_id == place_id
        ]

    def update_review(self, review_id, review_data):
        review = self.review_repo.get(review_id)
        if not review:
            return None

        self._validate_review_data(review_data, partial=True)
        return self.review_repo.update(review_id, review_data)

    def delete_review(self, review_id):
        """Delete a review by ID."""
        review = self.review_repo.get(review_id)
        if not review:
            return None

        self.review_repo.delete(review_id)
        return review
