from datetime import datetime
from typing import Optional, List
from pydantic import BaseModel

class MemoryBase(BaseModel):
    title: Optional[str] = None
    url: str
    content: Optional[str] = None

class MemoryCreate(MemoryBase):
    pass

class MemoryResponse(MemoryBase):
    id: int
    summary: Optional[str] = None
    tags: Optional[List[str]] = None
    importance_score: Optional[int] = None
    created_at: datetime

    class Config:
        orm_mode = True
        from_attributes = True

class MemorySearchResponse(BaseModel):
    title: Optional[str] = None
    url: str
    snippet: Optional[str] = None
    similarity_score: float

    class Config:
        orm_mode = True
        from_attributes = True


class ChatRequest(BaseModel):
    query: str


class ChatResponse(BaseModel):
    answer: str
    sources: List[MemorySearchResponse]


