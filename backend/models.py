from datetime import datetime
from sqlalchemy import Column, DateTime, Integer, Text, ForeignKey, JSON
from sqlalchemy.orm import relationship
from pgvector.sqlalchemy import Vector
from database import Base

class Memory(Base):
    __tablename__ = "memories"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(Text, nullable=True)
    url = Column(Text, nullable=False)
    content = Column(Text, nullable=True)
    summary = Column(Text, nullable=True)
    tags = Column(JSON, nullable=True)
    importance_score = Column(Integer, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)

    # One-to-one relationship with Embedding
    embedding = relationship("Embedding", back_populates="memory", uselist=False, cascade="all, delete-orphan")



class Embedding(Base):
    __tablename__ = "embeddings"

    id = Column(Integer, primary_key=True, index=True)
    memory_id = Column(Integer, ForeignKey("memories.id", ondelete="CASCADE"), nullable=False, unique=True)
    embedding = Column(Vector(1536), nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)

    memory = relationship("Memory", back_populates="embedding")

