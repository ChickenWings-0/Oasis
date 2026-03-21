from sqlalchemy.orm import Session
from ..models import Project
from ..schemas import ProjectCreate
from ..repositories import ProjectRepository, BranchRepository
from ..schemas import BranchCreate
from ..exceptions import ForbiddenError, NotFoundError, ValidationError


class ProjectService:
    """
    Business logic layer for Projects
    Handles validation, ownership, and orchestration
    
    AUTHORIZATION RULES:
    - Only owner can get/delete their project
    - Only authenticated users can create projects
    - Project deletion is owner-only
    """

    def __init__(self, db: Session):
        self.db = db
        self.project_repo = ProjectRepository(db)
        self.branch_repo = BranchRepository(db)

    def create_project(self, user_id: int, project_data: ProjectCreate) -> Project:
        """
        Create new project with ownership and auto-create main branch
        
        AUTHORIZATION: Any authenticated user can create projects
        
        Flow:
        1. Validate project name
        2. Create project (owner = current user)
        3. Auto-create 'main' branch as default
        4. Return project
        """
        # Validate project name
        if not project_data.name or len(project_data.name.strip()) == 0:
            raise ValidationError("Project name cannot be empty")
        
        if len(project_data.name) > 255:
            raise ValidationError("Project name must be <= 255 characters")
        
        # Create project (ownership set to user_id from auth)
        project_create = ProjectCreate(
            name=project_data.name,
            description=project_data.description,
            owner_id=user_id
        )
        project = self.project_repo.create_project(project_create)
        
        # Auto-create default 'main' branch
        main_branch_data = BranchCreate(
            name="main",
            project_id=project.id,
            created_from=None
        )
        self.branch_repo.create_branch(main_branch_data)
        
        return project

    def get_project(self, user_id: int, project_id: int) -> Project | None:
        """
        Get project with ownership verification
        
        AUTHORIZATION: Only owner can view their project
        
        Rules:
        1. Project must exist
        2. Current user must be the owner
        
        Raises:
        - NotFoundError: Project doesn't exist
        - ForbiddenError: User is not the owner
        """
        project = self.project_repo.get_project_by_id(project_id)
        
        if not project:
            raise NotFoundError(f"Project {project_id} not found")
        
        # AUTHORIZATION CHECK: Verify ownership
        if project.owner_id != user_id:
            raise ForbiddenError(f"You do not own project {project_id}")
        
        return project

    def list_user_projects(self, user_id: int, skip: int = 0, limit: int = 100) -> list[Project]:
        """
        List all projects owned by current user
        
        AUTHORIZATION: Users can only list their own projects
        """
        return self.project_repo.list_projects(owner_id=user_id, skip=skip, limit=limit)

    def delete_project(self, user_id: int, project_id: int) -> bool:
        """
        Delete project with ownership verification
        
        AUTHORIZATION: Only owner can delete their project
        
        Rules:
        1. Project must exist
        2. Current user must be the owner
        3. Deletion cascades to all branches, commits, merges
        
        Raises:
        - NotFoundError: Project doesn't exist
        - ForbiddenError: User is not the owner
        """
        # This internally checks authorization (calls get_project which verifies ownership)
        project = self.get_project(user_id, project_id)
        
        return self.project_repo.delete_project(project_id)
