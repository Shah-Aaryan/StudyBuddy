from fastapi import FastAPI, Depends
from fastapi.middleware.cors import CORSMiddleware
# from fastapi.staticfiles import StaticFiles  # Uncomment if you later use static files
from sqlalchemy.orm import Session
from sqlalchemy import text

import logging

from app.config.settings import settings
from app.models.database import engine, Base, get_db
from app.api.routes import emotions, feedback, analytics, resources, auth ,notification,reports,sessions  # ✅ Import auth


# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Create database tables
Base.metadata.create_all(bind=engine)

# Initialize FastAPI app
app = FastAPI(
    title=settings.PROJECT_NAME,
    version="1.0.0",
    description="AI-powered feedback coach for online learning"
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://localhost:3001"],  # Add your frontend URLs
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Mount static files (optional)
# app.mount("/static", StaticFiles(directory="static"), name="static")

# Include routers
app.include_router(auth.router, prefix=f"{settings.API_V1_STR}/auth", tags=["auth"])  
app.include_router(emotions.router, prefix=f"{settings.API_V1_STR}/emotions", tags=["emotions"])
app.include_router(feedback.router, prefix=f"{settings.API_V1_STR}/feedback", tags=["feedback"])
app.include_router(analytics.router, prefix=f"{settings.API_V1_STR}/analytics", tags=["analytics"])
app.include_router(resources.router, prefix=f"{settings.API_V1_STR}/resources", tags=["resources"])
app.include_router(notification.router, prefix=f"{settings.API_V1_STR}/notifications", tags=["notifications"])
app.include_router(reports.router, prefix=f"{settings.API_V1_STR}/reports", tags=["reports"])
app.include_router(sessions.router, prefix=f"{settings.API_V1_STR}/sessions", tags=["Sessions"])

@app.get("/")
async def root():
    return {"message": "AI Feedback Coach API", "version": "1.0.0"}

@app.get("/health")
async def health_check(db: Session = Depends(get_db)):
    """Health check endpoint"""
    try:
        db.execute(text("SELECT 1"))
        return {"status": "healthy", "database": "connected"}
    except Exception as e:
        logger.error(f"Health check failed: {e}")
        return {"status": "unhealthy", "error": str(e)}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
