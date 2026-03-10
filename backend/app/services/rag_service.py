"""
RAG Service - Retrieval Augmented Generation for Knowledge Base
"""
from typing import List, Dict, Optional
from openai import OpenAI
from pinecone import Pinecone, ServerlessSpec
import json

from app.core.config import settings


class RAGService:
    """Semantic search for knowledge base using Pinecone vector database"""
    
    def __init__(self):
        self.openai_client = OpenAI(api_key=settings.OPENAI_API_KEY)
        self.embedding_model = "text-embedding-ada-002"
        self.dimension = 1536  # Ada-002 embedding dimension
        
        # Initialize Pinecone only if API key is provided
        self.pinecone_enabled = bool(settings.PINECONE_API_KEY and settings.PINECONE_ENVIRONMENT)
        
        if self.pinecone_enabled:
            try:
                self.pc = Pinecone(api_key=settings.PINECONE_API_KEY)
                self.index_name = "kb-articles"
                
                # Create index if it doesn't exist
                if self.index_name not in self.pc.list_indexes().names():
                    self.pc.create_index(
                        name=self.index_name,
                        dimension=self.dimension,
                        metric="cosine",
                        spec=ServerlessSpec(
                            cloud="aws",
                            region=settings.PINECONE_ENVIRONMENT or "us-west-2"
                        )
                    )
                
                self.index = self.pc.Index(self.index_name)
            except Exception as e:
                print(f"Pinecone initialization error: {str(e)}")
                self.pinecone_enabled = False
    
    async def generate_embedding(self, text: str) -> List[float]:
        """
        Generate vector embedding for text using OpenAI
        
        Args:
            text: Text to embed
        
        Returns:
            List of floats (1536 dimensions)
        """
        try:
            # Clean and truncate text (max 8191 tokens for ada-002)
            text = text.strip().replace("\n", " ")[:8000]
            
            response = self.openai_client.embeddings.create(
                model=self.embedding_model,
                input=text
            )
            
            return response.data[0].embedding
        
        except Exception as e:
            print(f"Embedding generation error: {str(e)}")
            # Return zero vector as fallback
            return [0.0] * self.dimension
    
    async def index_article(
        self,
        article_id: str,
        title: str,
        content: str,
        metadata: Optional[Dict] = None
    ) -> bool:
        """
        Index knowledge base article in Pinecone
        
        Args:
            article_id: Unique article ID
            title: Article title
            content: Article content
            metadata: Additional metadata (category, tags, etc.)
        
        Returns:
            True if successful, False otherwise
        """
        if not self.pinecone_enabled:
            return False
        
        try:
            # Combine title and content for better search
            text_to_embed = f"{title}\n\n{content}"
            
            # Generate embedding
            embedding = await self.generate_embedding(text_to_embed)
            
            # Prepare metadata
            meta = metadata or {}
            meta.update({
                "article_id": article_id,
                "title": title,
                "content_preview": content[:500]  # Store preview in metadata
            })
            
            # Upsert to Pinecone
            self.index.upsert(
                vectors=[(article_id, embedding, meta)]
            )
            
            return True
        
        except Exception as e:
            print(f"Article indexing error: {str(e)}")
            return False
    
    async def search_similar(
        self,
        query: str,
        top_k: int = 5,
        filter_dict: Optional[Dict] = None
    ) -> List[Dict]:
        """
        Search for similar articles using semantic search
        
        Args:
            query: Search query (natural language)
            top_k: Number of results to return
            filter_dict: Metadata filters (e.g., {"category": "technical"})
        
        Returns:
            List of matching articles with scores
        """
        if not self.pinecone_enabled:
            return []
        
        try:
            # Generate query embedding
            query_embedding = await self.generate_embedding(query)
            
            # Search in Pinecone
            results = self.index.query(
                vector=query_embedding,
                top_k=top_k,
                include_metadata=True,
                filter=filter_dict
            )
            
            # Format results
            articles = []
            for match in results.matches:
                articles.append({
                    "article_id": match.id,
                    "score": round(match.score, 4),
                    "title": match.metadata.get("title", ""),
                    "content_preview": match.metadata.get("content_preview", ""),
                    "metadata": match.metadata
                })
            
            return articles
        
        except Exception as e:
            print(f"Search error: {str(e)}")
            return []
    
    async def update_embedding(
        self,
        article_id: str,
        title: str,
        content: str,
        metadata: Optional[Dict] = None
    ) -> bool:
        """
        Update article embedding (same as index, Pinecone upsert handles updates)
        """
        return await self.index_article(article_id, title, content, metadata)
    
    async def delete_from_index(self, article_id: str) -> bool:
        """
        Remove article from vector index
        
        Args:
            article_id: Article ID to delete
        
        Returns:
            True if successful
        """
        if not self.pinecone_enabled:
            return False
        
        try:
            self.index.delete(ids=[article_id])
            return True
        except Exception as e:
            print(f"Delete error: {str(e)}")
            return False
    
    async def batch_index(self, articles: List[Dict]) -> Dict[str, any]:
        """
        Index multiple articles in batch
        
        Args:
            articles: List of dicts with keys: article_id, title, content, metadata
        
        Returns:
            Dict with success count and errors
        """
        if not self.pinecone_enabled:
            return {"success": 0, "errors": len(articles)}
        
        success_count = 0
        errors = []
        vectors_to_upsert = []
        
        for article in articles:
            try:
                article_id = article['article_id']
                title = article['title']
                content = article['content']
                metadata = article.get('metadata', {})
                
                # Generate embedding
                text_to_embed = f"{title}\n\n{content}"
                embedding = await self.generate_embedding(text_to_embed)
                
                # Prepare metadata
                meta = metadata.copy()
                meta.update({
                    "article_id": article_id,
                    "title": title,
                    "content_preview": content[:500]
                })
                
                vectors_to_upsert.append((article_id, embedding, meta))
                success_count += 1
            
            except Exception as e:
                errors.append({
                    "article_id": article.get('article_id', 'unknown'),
                    "error": str(e)
                })
        
        # Batch upsert to Pinecone
        if vectors_to_upsert:
            try:
                self.index.upsert(vectors=vectors_to_upsert)
            except Exception as e:
                print(f"Batch upsert error: {str(e)}")
                return {"success": 0, "errors": len(articles)}
        
        return {
            "success": success_count,
            "errors": len(errors),
            "error_details": errors
        }
    
    async def get_relevant_context(
        self,
        query: str,
        top_k: int = 3
    ) -> str:
        """
        Get relevant KB articles as context for AI chatbot
        
        Args:
            query: User's question
            top_k: Number of articles to retrieve
        
        Returns:
            Formatted context string
        """
        articles = await self.search_similar(query, top_k=top_k)
        
        if not articles:
            return "No relevant articles found."
        
        context_parts = []
        for i, article in enumerate(articles, 1):
            context_parts.append(
                f"Article {i}: {article['title']}\n"
                f"Relevance: {article['score']:.2%}\n"
                f"Content: {article['content_preview']}...\n"
            )
        
        return "\n".join(context_parts)


# Global RAG service instance
rag_service = RAGService()
