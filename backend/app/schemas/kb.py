"""
Knowledge Base Pydantic schemas
"""
from pydantic import BaseModel, Field, validator
from typing import Optional, List
from datetime import datetime
from uuid import UUID


class KnowledgeCategoryBase(BaseModel):
    """Base KB category schema"""
    name: str = Field(..., min_length=2, max_length=100)
    description: Optional[str] = None
    icon: Optional[str] = Field(None, max_length=50)
    color: str = Field("#3B82F6", pattern="^#[0-9A-Fa-f]{6}$")
    parent_id: Optional[UUID] = None
    order: int = Field(0, ge=0)


class KnowledgeCategoryCreate(KnowledgeCategoryBase):
    """Schema for creating KB category"""
    is_published: bool = True


class KnowledgeCategoryUpdate(BaseModel):
    """Schema for updating KB category"""
    name: Optional[str] = Field(None, min_length=2, max_length=100)
    slug: Optional[str] = None
    description: Optional[str] = None
    icon: Optional[str] = None
    color: Optional[str] = Field(None, pattern="^#[0-9A-Fa-f]{6}$")
    parent_id: Optional[UUID] = None
    order: Optional[int] = Field(None, ge=0)
    is_published: Optional[bool] = None


class KnowledgeCategoryResponse(BaseModel):
    """Schema for KB category response"""
    id: UUID
    name: str
    slug: str
    description: Optional[str]
    icon: Optional[str]
    color: str
    parent_id: Optional[UUID]
    order: int
    is_published: bool
    created_at: datetime
    updated_at: datetime
    
    # Subcategories (optional)
    subcategories: Optional[List['KnowledgeCategoryResponse']] = None
    article_count: Optional[int] = None
    
    class Config:
        from_attributes = True


class KnowledgeArticleBase(BaseModel):
    """Base KB article schema"""
    title: str = Field(..., min_length=5, max_length=200)
    content: str = Field(..., min_length=50)
    summary: Optional[str] = Field(None, max_length=500)
    category_id: UUID
    keywords: Optional[str] = None
    meta_description: Optional[str] = Field(None, max_length=160)


class KnowledgeArticleCreate(KnowledgeArticleBase):
    """Schema for creating KB article"""
    is_published: bool = False
    is_featured: bool = False


class KnowledgeArticleUpdate(BaseModel):
    """Schema for updating KB article"""
    title: Optional[str] = Field(None, min_length=5, max_length=200)
    slug: Optional[str] = None
    content: Optional[str] = Field(None, min_length=50)
    summary: Optional[str] = Field(None, max_length=500)
    category_id: Optional[UUID] = None
    keywords: Optional[str] = None
    meta_description: Optional[str] = Field(None, max_length=160)
    is_published: Optional[bool] = None
    is_featured: Optional[bool] = None


class KnowledgeArticleResponse(BaseModel):
    """Schema for KB article response"""
    id: UUID
    title: str
    slug: str
    content: str
    summary: Optional[str]
    meta_description: Optional[str]
    keywords: Optional[str]
    
    # Category and author
    category_id: UUID
    category_name: str
    author_id: UUID
    author_name: str
    
    # Status
    is_published: bool
    is_featured: bool
    
    # Metrics
    view_count: int
    helpful_count: int
    not_helpful_count: int
    helpfulness_ratio: float
    search_score: float
    
    # AI fields
    ai_summary: Optional[str]
    related_keywords: Optional[str]
    
    # Timestamps
    created_at: datetime
    updated_at: datetime
    published_at: Optional[datetime]
    
    class Config:
        from_attributes = True


class KnowledgeArticleListResponse(BaseModel):
    """Schema for KB article list (simplified)"""
    id: UUID
    title: str
    slug: str
    summary: Optional[str]
    category_name: str
    author_name: str
    is_published: bool
    is_featured: bool
    view_count: int
    helpful_count: int
    helpfulness_ratio: float
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True


class KnowledgeArticleSearchRequest(BaseModel):
    """Schema for searching KB articles"""
    query: str = Field(..., min_length=2)
    category_id: Optional[UUID] = None
    top_k: int = Field(10, ge=1, le=50)
    use_semantic_search: bool = True


class KnowledgeArticleSearchResult(BaseModel):
    """Schema for KB article search result"""
    article_id: UUID
    title: str
    slug: str
    summary: Optional[str]
    content_preview: str
    category_name: str
    relevance_score: float
    view_count: int
    helpful_count: int
    
    class Config:
        from_attributes = True


class KnowledgeArticleVote(BaseModel):
    """Schema for voting on article helpfulness"""
    is_helpful: bool


class KnowledgeArticleGenerateRequest(BaseModel):
    """Schema for AI-generating KB article from ticket"""
    ticket_id: UUID
    category_id: UUID
    title: Optional[str] = None


class KnowledgeStats(BaseModel):
    """Schema for KB statistics"""
    total_articles: int
    published_articles: int
    total_categories: int
    total_views: int
    avg_helpfulness_ratio: float
    most_viewed_articles: List[KnowledgeArticleListResponse]
    most_helpful_articles: List[KnowledgeArticleListResponse]


class KnowledgeFilterParams(BaseModel):
    """Schema for filtering KB articles"""
    category_id: Optional[UUID] = None
    author_id: Optional[UUID] = None
    is_published: Optional[bool] = None
    is_featured: Optional[bool] = None
    search: Optional[str] = None
    min_helpfulness: Optional[float] = Field(None, ge=0, le=1)


# Update forward references for recursive models
KnowledgeCategoryResponse.model_rebuild()
