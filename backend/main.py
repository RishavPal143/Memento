import asyncio
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy import text

import models
from database import engine, Base
from routes import memory, search, chat, insights
from services.memory_processor import run_intelligence_job_loop

# Initialize FastAPI app
app = FastAPI(title="Internet Memory API")

# Enable CORS for localhost development
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=False,
    allow_methods=["*"],
    allow_headers=["*"],
)

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

# Include Routers
app.include_router(memory.router)
app.include_router(search.router)
app.include_router(chat.router)
app.include_router(insights.router)

# Register background jobs on startup
@app.on_event("startup")
def start_background_jobs():
    asyncio.create_task(run_intelligence_job_loop())

@app.get("/")
def read_root():
    return {"message": "Internet Memory API is running"}




