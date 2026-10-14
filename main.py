import os
from pathlib import Path
from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from fastapi.middleware.cors import CORSMiddleware
import uvicorn

from app.database import init_db, get_all_documents
from app.routers import documents, chat, flashcards, quizzes, summaries, analytics, settings as settings_router
from app.routers.documents import load_sample_documents

BASE_DIR = Path(__file__).resolve().parent
STATIC_DIR = BASE_DIR / "static"

# Ensure DB initialized on module import
init_db()

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup: Initialize database schema
    init_db()
    
    # Pre-seed sample documents if no documents exist yet
    docs = get_all_documents()
    if not docs:
        print("[Startup] Seeding initial sample study materials...")
        load_sample_documents()
        
    yield
    # Shutdown logic if needed

app = FastAPI(
    title="AI Study Buddy Pro",
    description="Intelligent AI Learning Platform with Multi-Modal Study Tools",
    version="2.0.0",
    lifespan=lifespan
)

# CORS Middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include Routers
app.include_router(documents.router)
app.include_router(chat.router)
app.include_router(flashcards.router)
app.include_router(quizzes.router)
app.include_router(summaries.router)
app.include_router(analytics.router)
app.include_router(settings_router.router)

# Health check
@app.get("/api/health")
def health_check():
    return {
        "status": "healthy",
        "app": "AI Study Buddy Pro",
        "version": "2.0.0"
    }

# Mount static files
app.mount("/static", StaticFiles(directory=str(STATIC_DIR)), name="static")

# Serve UI at root
@app.get("/")
def serve_index():
    return FileResponse(str(STATIC_DIR / "index.html"))

if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
