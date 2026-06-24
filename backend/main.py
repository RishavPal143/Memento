from fastapi import FastAPI, Depends, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
from typing import List
import models
import schemas
import crud
from database import engine, Base, get_db

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

# Automatically create database tables on startup
try:
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

