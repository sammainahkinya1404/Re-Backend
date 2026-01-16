# backend/main.py
from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from api import chat, leads
from database.session import init_databases
from config import get_settings

settings = get_settings()

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    print("[*] Starting Kenya Real Estate Sales Agent...")
    init_databases()
    print("[OK] App ready!")
    yield
    # Shutdown (if needed)
    print("[*] Shutting down...")

# Initialize FastAPI app
app = FastAPI(
    title=settings.APP_NAME,
    description="AI-powered real estate sales agent for Kenya satellite towns",
    version="1.0.0",
    lifespan=lifespan
)

# CORS middleware (allow frontend to connect)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, specify your frontend URL
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(chat.router)
app.include_router(leads.router)

# Health check endpoint
@app.get("/")
async def root():
    return {
        "message": "Kenya Real Estate Sales Agent API",
        "status": "running",
        "version": "1.0.0"
    }

@app.get("/health")
async def health_check():
    return {"status": "healthy"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        reload=settings.DEBUG
    )