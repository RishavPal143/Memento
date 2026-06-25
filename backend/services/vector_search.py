from sqlalchemy import select
from sqlalchemy.orm import Session
import sys
import os

# Add parent directory to path to ensure proper imports
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import models


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
