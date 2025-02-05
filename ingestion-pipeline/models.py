# models.py
from sqlalchemy import Column, String, Boolean, Text, DateTime, func
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()

class ResourceLink(Base):
    __tablename__ = "resource_links"
    
    link = Column(Text, primary_key=True)
    bot_name = Column(String(100), primary_key=True)
    file_type = Column(String(10), nullable=False)  # 'pdf' or 'blog'
    processing_status = Column(String(20), default="pending", nullable=False)
    is_embedded = Column(Boolean, default=False, nullable=False)
    error_message = Column(Text)
    submitted_at = Column(DateTime(timezone=True), server_default=func.now())
