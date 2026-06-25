from fastapi import FastAPI, Depends, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
from typing import List
import models
import schemas
import crud
from database import engine, Base, get_db
from embeddings import get_embedding, generate_snippet
from llm import generate_chat_response

# Initialize FastAPI app
app = FastAPI(title="Internet Memory API")

# Enable CORS for localhost development
# chrome-extension:// origins are supported since we allow any origin with credentials=False.
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=False,
    allow_methods=["*"],
    allow_headers=["*"],
)

from sqlalchemy import text

# Automatically create database tables and run simple migrations on startup
try:
    with engine.begin() as conn:
        conn.execute(text("CREATE EXTENSION IF NOT EXISTS vector;"))
        # Run column migration on memories table if it already exists
        conn.execute(text("ALTER TABLE memories ADD COLUMN IF NOT EXISTS summary TEXT;"))
        conn.execute(text("ALTER TABLE memories ADD COLUMN IF NOT EXISTS tags JSON;"))
        conn.execute(text("ALTER TABLE memories ADD COLUMN IF NOT EXISTS importance_score INTEGER;"))
    Base.metadata.create_all(bind=engine)
    print("Database tables created successfully!")
except Exception as e:
    print(f"Error creating database tables: {e}")


@app.get("/")
def read_root():
    return {"message": "Internet Memory API is running"}

@app.post("/memory", response_model=schemas.MemoryResponse, status_code=status.HTTP_201_CREATED)
def create_memory(memory: schemas.MemoryCreate, db: Session = Depends(get_db)):
    """
    Saves a webpage's captured metadata (title, URL, content) as a new memory.
    """
    try:
        return crud.create_memory(db=db, memory=memory)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Database insertion failed: {str(e)}"
        )

@app.get("/memory", response_model=List[schemas.MemoryResponse])
def read_memories(db: Session = Depends(get_db)):
    """
    Retrieves all stored web page memories.
    """
    try:
        return crud.get_memories(db=db)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to fetch memories: {str(e)}"
        )

@app.get("/memory/{id}", response_model=schemas.MemoryResponse)
def read_memory(id: int, db: Session = Depends(get_db)):
    """
    Retrieves a single memory record by its ID.
    """
    db_memory = crud.get_memory(db=db, memory_id=id)
    if db_memory is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Memory record not found"
        )
    return db_memory

@app.delete("/memory/{id}")
def delete_memory(id: int, db: Session = Depends(get_db)):
    """
    Deletes a memory record by its ID.
    """
    success = crud.delete_memory(db=db, memory_id=id)
    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Memory record not found"
        )
    return {"message": "Memory successfully deleted"}


@app.get("/search", response_model=List[schemas.MemorySearchResponse])
def search_memories(q: str, limit: int = 10, db: Session = Depends(get_db)):
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
        
        # Perform vector similarity search using pgvector
        search_results = crud.search_memories(db=db, query_vector=query_embedding, limit=limit)
        
        # Format response with snippets and similarity scores
        formatted_results = []
        for memory, distance in search_results:
            # Cosine similarity score = 1.0 - cosine distance
            similarity_score = 1.0 - distance
            
            # Generate snippet centered around query keywords
            snippet = generate_snippet(memory.content, q)
            
            formatted_results.append(
                schemas.MemorySearchResponse(
                    title=memory.title,
                    url=memory.url,
                    snippet=snippet,
                    similarity_score=similarity_score
                )
            )
            
        return formatted_results
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Semantic search failed: {str(e)}"
        )


@app.post("/chat", response_model=schemas.ChatResponse)
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
        search_results = crud.search_memories(db=db, query_vector=query_embedding, limit=5)
        
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



