"""FastAPI application entry point."""
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.core.config import settings
from app.api.routes import generate, sessions

# Create FastAPI app
app = FastAPI(
    title=settings.APP_NAME,
    description="AI-Powered Python Code Generator with LLM Agents",
    version="0.1.0",
    debug=settings.DEBUG,
)

# Configure CORS (Directive 12 - Port 5173)
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(generate.router, prefix="/api", tags=["generate"])
app.include_router(sessions.router, prefix="/api", tags=["sessions"])


@app.get("/api/health")
async def health_check():
    """Health check endpoint."""
    return {
        "status": "healthy",
        "app": settings.APP_NAME,
        "version": "0.1.0",
    }


@app.get("/")
async def root():
    """Root endpoint."""
    return {
        "message": "AI-Powered Python Code Generator API",
        "docs": "/docs",
        "health": "/api/health",
    }
