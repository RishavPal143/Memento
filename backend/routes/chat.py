from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
import sys
import os

# Add parent directory to path to ensure proper imports
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import schemas
from database import get_db
from embeddings import get_embedding, generate_snippet
from services.vector_search import search_memories
from services.llm import generate_chat_response

router = APIRouter(tags=["Chat"])


@router.post("/chat", response_model=schemas.ChatResponse)
def chat_with_memories(request: schemas.ChatRequest, db: Session = Depends(get_db)):
    """
    Semantic Chat endpoint that retrieves relevant memories, sends them
    along with the user query to the LLM, and returns a synthesized answer with source citations.
    """
    query = request.query
    if not query.strip():
        return schemas.ChatResponse(answer="Please provide a valid query.", sources=[])
        
    try:
        # 1. Convert query to embedding
        query_embedding = get_embedding(query)
        
        # 2. Retrieve top 5 relevant memories
        search_results = search_memories(db=db, query_vector=query_embedding, limit=5)
        
        # 3. Format the search results as sources
        sources = []
        sources_for_llm = []
        for memory, distance in search_results:
            similarity_score = 1.0 - distance
            snippet = generate_snippet(memory.content, query)
            
            source_response = schemas.MemorySearchResponse(
                title=memory.title,
                url=memory.url,
                snippet=snippet,
                similarity_score=similarity_score
            )
            sources.append(source_response)
            
            # Format dictionaries to pass to the LLM utility
            sources_for_llm.append({
                "title": memory.title,
                "url": memory.url,
                "snippet": snippet
            })
            
        # 4. Generate final natural language answer via LLM
        answer = generate_chat_response(query=query, sources=sources_for_llm)
        
        return schemas.ChatResponse(
            answer=answer,
            sources=sources
        )
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Chat agent session failed: {str(e)}"
        )
