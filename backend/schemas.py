from datetime import datetime
from typing import Optional
from pydantic import BaseModel

class MemoryBase(BaseModel):
    title: Optional[str] = None
    url: str
    content: Optional[str] = None

class MemoryCreate(MemoryBase):
    pass

class MemoryResponse(MemoryBase):
    id: int
    created_at: datetime

    class Config:
        orm_mode = True
        from_attributes = True
