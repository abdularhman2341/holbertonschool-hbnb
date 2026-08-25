from app.models.review import Review
from app.persistence.repository import SQLAlchemyRepository


class ReviewRepository(SQLAlchemyRepository):
    """Repository for review-specific database operations."""

    def __init__(self):
        super().__init__(Review)