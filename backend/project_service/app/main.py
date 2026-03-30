from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy import inspect, text
from .database import engine, Base
from .config import settings
from .models import Project, Branch, Commit, Merge, Team, TeamMember, TeamInvite  # Import models to register them

# Create database tables
Base.metadata.create_all(bind=engine)


def _ensure_project_team_column() -> None:
    """Backward-compatible migration for older databases missing projects.team_id."""
    with engine.begin() as connection:
        inspector = inspect(connection)
        if not inspector.has_table("projects"):
            return

        columns = {col["name"] for col in inspector.get_columns("projects")}
        if "team_id" not in columns:
            connection.execute(text("ALTER TABLE projects ADD COLUMN team_id INTEGER NULL"))

        connection.execute(
            text(
                """
                DO $$
                BEGIN
                    IF NOT EXISTS (
                        SELECT 1
                        FROM pg_constraint c
                        JOIN pg_class t ON c.conrelid = t.oid
                        WHERE c.contype = 'f'
                          AND t.relname = 'projects'
                          AND pg_get_constraintdef(c.oid) LIKE 'FOREIGN KEY (team_id)%'
                    ) THEN
                        ALTER TABLE projects
                        ADD CONSTRAINT fk_projects_team_id
                        FOREIGN KEY (team_id) REFERENCES teams(id)
                        ON DELETE SET NULL;
                    END IF;
                END $$;
                """
            )
        )
        connection.execute(text("CREATE INDEX IF NOT EXISTS ix_projects_team_id ON projects (team_id)"))


_ensure_project_team_column()

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


# Include routers
from .routes import project_routes, branch_routes, commit_routes, merge_routes, team_routes

app.include_router(project_routes.router)
app.include_router(branch_routes.router)
app.include_router(commit_routes.router)
app.include_router(merge_routes.router)
app.include_router(team_routes.router)
