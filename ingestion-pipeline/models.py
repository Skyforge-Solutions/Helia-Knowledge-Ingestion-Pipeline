# models.py
from sqlalchemy import Column, String, Boolean, Text, DateTime, func, PrimaryKeyConstraint, UniqueConstraint, Index
from db_setup import Base

class ResourceLink(Base):
    __tablename__ = "resource_links"

    # Use combination of link and bot_name as composite primary key
    link = Column(Text, nullable=False)
    bot_name = Column(String(100), nullable=False)
    file_type = Column(String(50), nullable=False) # "pdf" or "blog"

    # Status flags
    processing_status = Column(String(20), default="pending", nullable=False)
    is_embedded = Column(Boolean, default=False, nullable=False)

    # Error/diagnostic info
    error_message = Column(Text, nullable=True)

    # Date/time of submission
    submitted_at = Column(DateTime(timezone=True), server_default=func.now())

    # Define composite primary key and indexes
    __table_args__ = (
        PrimaryKeyConstraint('link', 'bot_name', name='pk_link_bot'),
        UniqueConstraint('link', 'bot_name', name='uq_link_bot'),
        Index('idx_link_bot', 'link', 'bot_name'),
    )
