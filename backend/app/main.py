from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
import os
from dotenv import load_dotenv

from app.core.config import settings
from app.core.database import engine
from app.models import base
from app.api.v1.api import api_router

# Load environment variables
load_dotenv()

# Create database tables
try:
    base.Base.metadata.create_all(bind=engine)
    print("Database tables created successfully")
except Exception as e:
    print(f"Failed to create database tables: {e}")
    # Continue without database for now

# Create FastAPI app
app = FastAPI(
    title="Shopify Automation API",
    description="Shopify 자동화 웹 애플리케이션 API",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://127.0.0.1:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include API routes
app.include_router(api_router, prefix="/api/v1")

# Mount static files (commented out for now)
# app.mount("/static", StaticFiles(directory="static"), name="static")

@app.get("/")
async def root():
    """루트 엔드포인트"""
    return {
        "message": "Shopify Automation API",
        "version": "1.0.0",
        "docs": "/docs"
    }

@app.get("/health")
async def health_check():
    """헬스 체크 엔드포인트"""
    return {"status": "healthy"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
