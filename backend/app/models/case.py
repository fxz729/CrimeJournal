"""
Legal Case Database Model
"""
from sqlalchemy import Column, Integer, String, Text, DateTime, Float, Index
from sqlalchemy.sql import func
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()


class Case(Base):
    """Legal case model for storing CourtListener data."""

    __tablename__ = "cases"

    id = Column(Integer, primary_key=True, index=True)
    # CourtListener ID
    courtlistener_id = Column(Integer, unique=True, index=True, nullable=False)

    # Basic Information
    case_name = Column(String(500), nullable=False)
    case_name_full = Column(String(1000))
    court = Column(String(200))  # Court name
    court_id = Column(String(100))  # Court ID

    # Dates
    date_filed = Column(DateTime)
    date_decided = Column(DateTime)

    # Content
    citation = Column(String(200))
    docket_number = Column(String(200))
    source = Column(String(100))  # Source of the case

    # Text content
    plain_text = Column(Text)
    html_text = Column(Text)

    # AI-generated fields
    summary = Column(Text)  # Claude-generated summary
    keywords = Column(Text)  # DeepSeek-extracted keywords (JSON array)
    entities = Column(Text)  # Claude-extracted entities (JSON)

    # Vector embedding (stored as text, will be converted)
    embedding = Column(Text)  # Vector embedding for similarity search

    # Metadata
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    # Indexes for efficient querying
    __table_args__ = (
        Index('idx_case_date_filed', 'date_filed'),
        Index('idx_case_court', 'court'),
    )

    def __repr__(self):
        return f"<Case(id={self.id}, name={self.case_name})>"
