from app.models.place import Place
from app.persistence.repository import SQLAlchemyRepository


class PlaceRepository(SQLAlchemyRepository):
    """Repository for place-specific database operations."""

    def __init__(self):
        super().__init__(Place)