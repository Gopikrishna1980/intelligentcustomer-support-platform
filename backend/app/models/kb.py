"""
Knowledge Base Models - Help articles and documentation
"""
from sqlalchemy import Column, String, Text, Boolean, DateTime, ForeignKey, Integer
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from datetime import datetime
import uuid

from app.core.database import Base


class KnowledgeCategory(Base):
    __tablename__ = "kb_categories"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name = Column(String(200), nullable=False)
    slug = Column(String(250), unique=True, index=True, nullable=False)
    description = Column(Text)
    icon = Column(String(50))  # Icon name or emoji
    color = Column(String(7), default="#3B82F6")
    
    # Hierarchy
    parent_id = Column(UUID(as_uuid=True), ForeignKey("kb_categories.id"))
    order = Column(Integer, default=0)
    
    # Visibility
    is_published = Column(Boolean, default=True)
    
    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    articles = relationship("KnowledgeArticle", back_populates="category")
    parent = relationship("KnowledgeCategory", remote_side=[id], backref="subcategories")
    
    def __repr__(self):
        return f"<KBCategory {self.name}>"


class KnowledgeArticle(Base):
    __tablename__ = "kb_articles"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    
    # Content
    title = Column(String(500), nullable=False)
    slug = Column(String(550), unique=True, index=True, nullable=False)
    content = Column(Text, nullable=False)
    summary = Column(Text)
    
    # SEO
    meta_description = Column(String(160))
    keywords = Column(String(500))  # Comma-separated
    
    # Category
    category_id = Column(UUID(as_uuid=True), ForeignKey("kb_categories.id"))
    
    # Author
    author_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False)
    
    # Status
    is_published = Column(Boolean, default=False)
    is_featured = Column(Boolean, default=False)
    
    # Metrics
    view_count = Column(Integer, default=0)
    helpful_count = Column(Integer, default=0)
    not_helpful_count = Column(Integer, default=0)
    search_score = Column(Integer, default=0)  # For ranking in search
    
    # AI features
    ai_embedding = Column(Text)  # Vector embedding for semantic search (stored as JSON)
    ai_summary = Column(Text)  # AI-generated summary
    related_keywords = Column(Text)  # AI-extracted keywords
    
    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow, index=True)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    published_at = Column(DateTime)
    
    # Relationships
    category = relationship("KnowledgeCategory", back_populates="articles")
    author = relationship("User")
    
    def __repr__(self):
        return f"<KBArticle {self.title}>"
    
    @property
    def helpfulness_ratio(self) -> float:
        """Calculate helpfulness ratio"""
        total = self.helpful_count + self.not_helpful_count
        if total == 0:
            return 0.0
        return self.helpful_count / total
