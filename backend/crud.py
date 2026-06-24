from sqlalchemy.orm import Session
import models
import schemas

def create_memory(db: Session, memory: schemas.MemoryCreate):
    """
    Saves a new memory to the database.
    """
    db_memory = models.Memory(
        title=memory.title,
        url=memory.url,
        content=memory.content
    )
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
