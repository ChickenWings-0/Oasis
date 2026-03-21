from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from .database import engine, Base
from .config import settings
from .models import Project, Branch, Commit, Merge  # Import models to register them

# Create database tables
Base.metadata.create_all(bind=engine)

# Initialize FastAPI app
app = FastAPI(
    title="Project Service",
    description="Microservice for managing projects, branches, commits, and merges",
    version="1.0.0"
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/health", tags=["Health"])
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "service": "project_service",
        "environment": settings.environment
    }


@app.on_event("startup")
async def startup_event():
    """Log startup information"""
    print(f"Project Service started in {settings.environment} environment")
    print(f"Database: {settings.project_database_url}")


# TODO: Add routers
# from .routes import project_routes, branch_routes, commit_routes, merge_routes
# app.include_router(project_routes.router)
# app.include_router(branch_routes.router)
# app.include_router(commit_routes.router)
# app.include_router(merge_routes.router)
