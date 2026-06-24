from datetime import datetime
from sqlalchemy import Column, DateTime, Integer, Text
from database import Base

class Memory(Base):
    __tablename__ = "memories"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(Text, nullable=True)
    url = Column(Text, nullable=False)
    content = Column(Text, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)

