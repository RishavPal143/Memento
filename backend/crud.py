from sqlalchemy import select
from sqlalchemy.orm import Session
import models
import schemas

from embeddings import clean_and_truncate_text, get_embedding
from llm import analyze_memory_content

def create_memory(db: Session, memory: schemas.MemoryCreate):
    """
    Saves a new memory to the database, cleans and truncates its content,
    generates an embedding vector, and stores both in a single transaction.
    """
    # Clean and truncate content
    cleaned_content = clean_and_truncate_text(memory.content)

    # Generate embedding vector
    embedding_vector = get_embedding(cleaned_content)

    # Generate AI metadata enhancements (summary, tags, importance score)
    metadata = analyze_memory_content(memory.title, cleaned_content)

    # Create memory record with cleaned content and AI metadata
    db_memory = models.Memory(
        title=memory.title,
        url=memory.url,
        content=cleaned_content,
        summary=metadata.get("summary"),
        tags=metadata.get("tags"),
        importance_score=metadata.get("importance_score")
    )
    
    # Create embedding record and link it to the memory
    db_embedding = models.Embedding(embedding=embedding_vector)
    db_memory.embedding = db_embedding


    # Add to DB session and commit atomically
    db.add(db_memory)
    db.commit()
    db.refresh(db_memory)
    
    return db_memory

def get_memories(db: Session, skip: int = 0, limit: int = 100):
    """
    Retrieves all memories from the database with pagination support.
    """
    return db.query(models.Memory).offset(skip).limit(limit).all()

def get_memory(db: Session, memory_id: int):
    """
    Retrieves a single memory by ID.
    """
    return db.query(models.Memory).filter(models.Memory.id == memory_id).first()

def delete_memory(db: Session, memory_id: int):
    """
    Deletes a memory by ID. Returns True if deleted, False if not found.
    """
    db_memory = db.query(models.Memory).filter(models.Memory.id == memory_id).first()
    if db_memory:
        db.delete(db_memory)
        db.commit()
        return True
    return False


def search_memories(db: Session, query_vector: list[float], limit: int = 10):
    """
    Performs a vector similarity search using pgvector, sorting by cosine distance
    and returning a list of tuples containing (Memory, distance).
    """
    distance_expr = models.Embedding.embedding.cosine_distance(query_vector)
    
    # Select the Memory model and the calculated cosine distance
    stmt = select(models.Memory, distance_expr.label("distance"))\
        .join(models.Embedding, models.Memory.id == models.Embedding.memory_id)\
        .order_by(distance_expr)\
        .limit(limit)
        
    return db.execute(stmt).all()

