# FastAPI app entry point
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from backend.user_services.database import engine, Base
from backend.user_services.models import User
from backend.user_services.friends.friend_model import Friendship
from backend.user_services.registration.reg_routes import router as registration_router
from backend.user_services.login.log_routes import router as login_router
from backend.user_services.login.google_routes import router as google_login_router
from backend.user_services.profiles.prof_routes import router as profile_router
from backend.user_services.friends.friend_routes import router as friends_router

# Create database tables
Base.metadata.create_all(bind=engine)

# Initialize FastAPI app
app = FastAPI(
    title="Authentication API",
    description="FastAPI Authentication System with JWT and PostgreSQL",
    version="1.0.0"
)

# CORS configuration
origins = [
    "http://localhost",
    "http://localhost:3000",
    "http://localhost:8000",
    "http://localhost:8001",
    "http://localhost:5500",
    "http://127.0.0.1",
    "http://127.0.0.1:3000",
    "http://127.0.0.1:8000",
    "http://127.0.0.1:8001",
    "http://127.0.0.1:5500",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(registration_router)
app.include_router(login_router)
app.include_router(google_login_router)
app.include_router(profile_router)
app.include_router(friends_router)

# Health check endpoint
@app.get(
    "/health",
    tags=["health"],
    summary="Health check",
    description="Check if the API is running"
)
def health_check():
    """Health check endpoint"""
    return {"status": "healthy", "message": "API is running on port 8001"}

@app.get(
    "/",
    tags=["root"],
    summary="Root endpoint",
    description="Welcome message"
)
def read_root():
    """Root endpoint"""
    return {
        "message": "Welcome to Authentication API",
        "docs": "Visit /docs for API documentation",
        "version": "1.0.0",
        "port": 8001
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        app,
        host="0.0.0.0",
        port=8001,
        reload=True
    )