"""
User Database Model
"""
from sqlalchemy import Column, Integer, String, Boolean, DateTime
from sqlalchemy.sql import func
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()


class User(Base):
    """User model for authentication and subscription management."""

    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    email = Column(String(255), unique=True, index=True, nullable=False)
    hashed_password = Column(String(255), nullable=False)

    # Profile
    full_name = Column(String(200))

    # Subscription
    subscription_tier = Column(String(50), default="free")  # free, pro, enterprise
    stripe_customer_id = Column(String(200))
    subscription_end_date = Column(DateTime)

    # Usage tracking
    daily_search_count = Column(Integer, default=0)
    last_search_date = Column(DateTime)

    # Status
    is_active = Column(Boolean, default=True)
    is_verified = Column(Boolean, default=False)

    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    def __repr__(self):
        return f"<User(id={self.id}, email={self.email})>"


class SearchHistory(Base):
    """Search history for users."""

    __tablename__ = "search_history"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, index=True, nullable=False)
    query = Column(String(500), nullable=False)
    filters = Column(String(1000))  # JSON string of filters

    created_at = Column(DateTime(timezone=True), server_default=func.now())

    def __repr__(self):
        return f"<SearchHistory(id={self.id}, query={self.query})>"


class FavoriteCase(Base):
    """User's favorite cases."""

    __tablename__ = "favorite_cases"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, index=True, nullable=False)
    case_id = Column(Integer, index=True, nullable=False)

    created_at = Column(DateTime(timezone=True), server_default=func.now())

    def __repr__(self):
        return f"<FavoriteCase(user_id={self.user_id}, case_id={self.case_id})>"
