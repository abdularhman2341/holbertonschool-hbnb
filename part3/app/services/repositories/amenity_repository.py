from app.models.amenity import Amenity
from app.persistence.repository import SQLAlchemyRepository


class AmenityRepository(SQLAlchemyRepository):
    """Repository for amenity-specific database operations."""

    def __init__(self):
        super().__init__(Amenity)