from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List
import sys
import os

# Add parent directory to path to ensure proper imports
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import schemas
from database import get_db
from embeddings import get_embedding, generate_snippet
from services.vector_search import search_memories

router = APIRouter(tags=["Search"])


@router.get("/search", response_model=List[schemas.MemorySearchResponse])
def search_memories_endpoint(q: str, limit: int = 10, db: Session = Depends(get_db)):
    """
    Performs semantic search across stored web page memories using vector similarity (cosine distance).
    """
    # Clamp limit between 5 and 20 as requested (top 5-20 most relevant memories)
    limit = max(5, min(20, limit))
    
    if not q.strip():
        return []
        
    try:
        # Convert search query into embedding vector
        query_embedding = get_embedding(q)
        
        # Perform vector similarity search using services/vector_search
        search_results = search_memories(db=db, query_vector=query_embedding, limit=limit)
        
        # Format response with snippets and similarity scores
        formatted_results = []
        for memory, distance in search_results:
            # Cosine similarity score = 1.0 - cosine distance
            similarity_score = 1.0 - distance
            
            # Generate snippet centered around query keywords
            snippet = generate_snippet(memory.content, q)
            
            formatted_results.append(
                schemas.MemorySearchResponse(
                    id=memory.id,
                    title=memory.title,
                    url=memory.url,
                    snippet=snippet,
                    similarity_score=similarity_score,
                    summary=memory.summary,
                    tags=memory.tags,
                    importance_score=memory.importance_score,
                    created_at=memory.created_at
                )
            )
            
        return formatted_results
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Semantic search failed: {str(e)}"
        )
