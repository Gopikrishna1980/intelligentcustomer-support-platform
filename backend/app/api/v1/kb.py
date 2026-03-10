"""
Knowledge Base API endpoints
"""
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from sqlalchemy import func, or_
from typing import List, Optional
from datetime import datetime
from uuid import UUID
import re

from app.core.database import get_db
from app.api.dependencies import get_current_user, get_current_agent
from app.models.user import User
from app.models.kb import KnowledgeArticle, KnowledgeCategory
from app.schemas.kb import (
    KnowledgeCategoryCreate,
    KnowledgeCategoryUpdate,
    KnowledgeCategoryResponse,
    KnowledgeArticleCreate,
    KnowledgeArticleUpdate,
    KnowledgeArticleResponse,
    KnowledgeArticleListResponse,
    KnowledgeArticleSearchRequest,
    KnowledgeArticleSearchResult,
    KnowledgeArticleVote
)
from app.schemas.common import SuccessResponse
from app.services.ai_service import ai_service
from app.services.rag_service import rag_service

router = APIRouter()


def generate_slug(text: str) -> str:
    """Generate URL-friendly slug from text"""
    slug = text.lower()
    slug = re.sub(r'[^\w\s-]', '', slug)
    slug = re.sub(r'[\s_-]+', '-', slug)
    slug = re.sub(r'^-+|-+$', '', slug)
    return slug


@router.get("/categories", response_model=List[KnowledgeCategoryResponse])
async def list_categories(
    include_unpublished: bool = False,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    List all KB categories with hierarchy
    """
    query = db.query(KnowledgeCategory)
    
    # Only agents can see unpublished categories
    if not include_unpublished or not current_user.is_agent:
        query = query.filter(KnowledgeCategory.is_published == True)
    
    categories = query.order_by(KnowledgeCategory.order, KnowledgeCategory.name).all()
    
    # Build hierarchy
    category_dict = {}
    for cat in categories:
        article_count = db.query(func.count(KnowledgeArticle.id)).filter(
            KnowledgeArticle.category_id == cat.id,
            KnowledgeArticle.is_published == True
        ).scalar()
        
        category_dict[cat.id] = {
            **cat.__dict__,
            "subcategories": [],
            "article_count": article_count
        }
    
    # Organize into hierarchy
    root_categories = []
    for cat_id, cat_data in category_dict.items():
        if cat_data.get("parent_id"):
            parent = category_dict.get(cat_data["parent_id"])
            if parent:
                parent["subcategories"].append(cat_data)
        else:
            root_categories.append(cat_data)
    
    return root_categories


@router.post("/categories", response_model=KnowledgeCategoryResponse, status_code=status.HTTP_201_CREATED)
async def create_category(
    category_data: KnowledgeCategoryCreate,
    current_user: User = Depends(get_current_agent),
    db: Session = Depends(get_db)
):
    """
    Create KB category (agents only)
    """
    slug = generate_slug(category_data.name)
    
    # Check if slug exists
    existing = db.query(KnowledgeCategory).filter(KnowledgeCategory.slug == slug).first()
    if existing:
        slug = f"{slug}-{secrets.token_hex(4)}"
    
    new_category = KnowledgeCategory(
        name=category_data.name,
        slug=slug,
        description=category_data.description,
        icon=category_data.icon,
        color=category_data.color,
        parent_id=category_data.parent_id,
        order=category_data.order,
        is_published=category_data.is_published
    )
    
    db.add(new_category)
    db.commit()
    db.refresh(new_category)
    
    return {**new_category.__dict__, "subcategories": None, "article_count": 0}


@router.get("/articles", response_model=List[KnowledgeArticleListResponse])
async def list_articles(
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    category_id: Optional[UUID] = None,
    search: Optional[str] = None,
    featured_only: bool = False,
    include_unpublished: bool = False,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    List KB articles with filters
    """
    query = db.query(KnowledgeArticle)
    
    # Only agents can see unpublished
    if not include_unpublished or not current_user.is_agent:
        query = query.filter(KnowledgeArticle.is_published == True)
    
    if category_id:
        query = query.filter(KnowledgeArticle.category_id == category_id)
    
    if featured_only:
        query = query.filter(KnowledgeArticle.is_featured == True)
    
    if search:
        query = query.filter(
            or_(
                KnowledgeArticle.title.ilike(f"%{search}%"),
                KnowledgeArticle.content.ilike(f"%{search}%"),
                KnowledgeArticle.keywords.ilike(f"%{search}%")
            )
        )
    
    # Pagination
    skip = (page - 1) * page_size
    articles = query.order_by(KnowledgeArticle.view_count.desc()).offset(skip).limit(page_size).all()
    
    # Format response
    result = []
    for article in articles:
        category = db.query(KnowledgeCategory).filter(KnowledgeCategory.id == article.category_id).first()
        author = db.query(User).filter(User.id == article.author_id).first()
        
        result.append({
            **article.__dict__,
            "category_name": category.name if category else "Unknown",
            "author_name": author.full_name if author else "Unknown",
            "helpfulness_ratio": article.helpfulness_ratio
        })
    
    return result


@router.post("/articles/search", response_model=List[KnowledgeArticleSearchResult])
async def search_articles(
    search_request: KnowledgeArticleSearchRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Semantic search for KB articles using RAG
    """
    if search_request.use_semantic_search:
        # Use Pinecone vector search
        filter_dict = {}
        if search_request.category_id:
            filter_dict["category_id"] = str(search_request.category_id)
        
        rag_results = await rag_service.search_similar(
            search_request.query,
            top_k=search_request.top_k,
            filter_dict=filter_dict
        )
        
        # Get full article details
        results = []
        for rag_result in rag_results:
            article_id = rag_result['article_id']
            article = db.query(KnowledgeArticle).filter(
                KnowledgeArticle.id == article_id,
                KnowledgeArticle.is_published == True
            ).first()
            
            if article:
                category = db.query(KnowledgeCategory).filter(
                    KnowledgeCategory.id == article.category_id
                ).first()
                
                results.append({
                    "article_id": article.id,
                    "title": article.title,
                    "slug": article.slug,
                    "summary": article.summary,
                    "content_preview": rag_result['content_preview'],
                    "category_name": category.name if category else "Unknown",
                    "relevance_score": rag_result['score'],
                    "view_count": article.view_count,
                    "helpful_count": article.helpful_count
                })
        
        return results
    else:
        # Regular text search
        query = db.query(KnowledgeArticle).filter(
            KnowledgeArticle.is_published == True
        )
        
        if search_request.category_id:
            query = query.filter(KnowledgeArticle.category_id == search_request.category_id)
        
        query = query.filter(
            or_(
                KnowledgeArticle.title.ilike(f"%{search_request.query}%"),
                KnowledgeArticle.content.ilike(f"%{search_request.query}%")
            )
        )
        
        articles = query.limit(search_request.top_k).all()
        
        results = []
        for article in articles:
            category = db.query(KnowledgeCategory).filter(
                KnowledgeCategory.id == article.category_id
            ).first()
            
            results.append({
                "article_id": article.id,
                "title": article.title,
                "slug": article.slug,
                "summary": article.summary,
                "content_preview": article.content[:200],
                "category_name": category.name if category else "Unknown",
                "relevance_score": 0.5,  # Default for non-semantic search
                "view_count": article.view_count,
                "helpful_count": article.helpful_count
            })
        
        return results


@router.get("/articles/{slug}", response_model=KnowledgeArticleResponse)
async def get_article(
    slug: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Get article by slug and increment view count
    """
    article = db.query(KnowledgeArticle).filter(KnowledgeArticle.slug == slug).first()
    
    if not article:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Article not found"
        )
    
    # Check if published (unless agent)
    if not article.is_published and not current_user.is_agent:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Article not found"
        )
    
    # Increment view count
    article.view_count += 1
    db.commit()
    
    # Get category and author
    category = db.query(KnowledgeCategory).filter(KnowledgeCategory.id == article.category_id).first()
    author = db.query(User).filter(User.id == article.author_id).first()
    
    return {
        **article.__dict__,
        "category_name": category.name if category else "Unknown",
        "author_name": author.full_name if author else "Unknown",
        "helpfulness_ratio": article.helpfulness_ratio
    }


@router.post("/articles", response_model=KnowledgeArticleResponse, status_code=status.HTTP_201_CREATED)
async def create_article(
    article_data: KnowledgeArticleCreate,
    current_user: User = Depends(get_current_agent),
    db: Session = Depends(get_db)
):
    """
    Create KB article (agents only)
    """
    import secrets
    
    slug = generate_slug(article_data.title)
    
    # Check if slug exists
    existing = db.query(KnowledgeArticle).filter(KnowledgeArticle.slug == slug).first()
    if existing:
        slug = f"{slug}-{secrets.token_hex(4)}"
    
    # Generate AI summary if not provided
    if not article_data.summary:
        summary = await ai_service.generate_kb_summary(article_data.content)
    else:
        summary = article_data.summary
    
    new_article = KnowledgeArticle(
        title=article_data.title,
        slug=slug,
        content=article_data.content,
        summary=summary,
        meta_description=article_data.meta_description or summary[:160],
        keywords=article_data.keywords,
        category_id=article_data.category_id,
        author_id=current_user.id,
        is_published=article_data.is_published,
        is_featured=article_data.is_featured,
        ai_summary=summary
    )
    
    db.add(new_article)
    db.commit()
    db.refresh(new_article)
    
    # Index in Pinecone for semantic search
    category = db.query(KnowledgeCategory).filter(KnowledgeCategory.id == article_data.category_id).first()
    await rag_service.index_article(
        str(new_article.id),
        new_article.title,
        new_article.content,
        metadata={
            "category_id": str(article_data.category_id),
            "category_name": category.name if category else "Unknown"
        }
    )
    
    return {
        **new_article.__dict__,
        "category_name": category.name if category else "Unknown",
        "author_name": current_user.full_name,
        "helpfulness_ratio": 0.0
    }


@router.post("/articles/{article_id}/vote", response_model=SuccessResponse)
async def vote_article(
    article_id: UUID,
    vote_data: KnowledgeArticleVote,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Vote on article helpfulness
    """
    article = db.query(KnowledgeArticle).filter(KnowledgeArticle.id == article_id).first()
    
    if not article:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Article not found"
        )
    
    if vote_data.is_helpful:
        article.helpful_count += 1
        message = "Thank you for your feedback!"
    else:
        article.not_helpful_count += 1
        message = "Thank you for your feedback. We'll work on improving this article."
    
    db.commit()
    
    return SuccessResponse(message=message)
