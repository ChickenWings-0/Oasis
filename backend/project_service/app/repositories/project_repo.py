from sqlalchemy.orm import Session
from sqlalchemy import desc
from ..models import Project
from ..schemas import ProjectCreate


class ProjectRepository:
    """
    Database access layer for Projects
    ONLY data queries - NO business logic
    """

    def __init__(self, db: Session):
        self.db = db

    def create_project(self, project_data: ProjectCreate) -> Project:
        """Insert new project into database"""
        db_project = Project(
            name=project_data.name,
            description=project_data.description,
            owner_id=project_data.owner_id,
            team_id=project_data.team_id,
        )
        self.db.add(db_project)
        self.db.commit()
        self.db.refresh(db_project)
        return db_project

    def get_project_by_id(self, project_id: int) -> Project | None:
        """Get project by ID"""
        return self.db.query(Project).filter(Project.id == project_id).first()

    def list_projects(self, owner_id: int | None = None, skip: int = 0, limit: int = 100) -> list[Project]:
        """
        List projects with optional filters
        Args:
            owner_id: Filter by owner (optional)
            skip: Pagination offset
            limit: Pagination limit
        Returns: List of projects, newest first
        """
        query = self.db.query(Project)
        
        if owner_id is not None:
            query = query.filter(Project.owner_id == owner_id)
        
        return query.order_by(desc(Project.created_at)).offset(skip).limit(limit).all()

    def update_project(self, project_id: int, **updates) -> Project | None:
        """Update project fields and return updated project"""
        project = self.get_project_by_id(project_id)
        if not project:
            return None
        
        for key, value in updates.items():
            if hasattr(project, key):
                setattr(project, key, value)
        
        self.db.commit()
        self.db.refresh(project)
        return project

    def delete_project(self, project_id: int) -> bool:
        """Delete project by ID"""
        project = self.get_project_by_id(project_id)
        if not project:
            return False
        
        self.db.delete(project)
        self.db.commit()
        return True
