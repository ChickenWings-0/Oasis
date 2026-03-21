from sqlalchemy.orm import Session
from ..models import Branch, Project
from ..schemas import BranchCreate
from ..repositories import BranchRepository, ProjectRepository


class BranchService:
    """
    Business logic layer for Branches
    Handles branch creation, naming rules, and pointer management
    """

    def __init__(self, db: Session):
        self.db = db
        self.branch_repo = BranchRepository(db)
        self.project_repo = ProjectRepository(db)

    def create_branch(self, user_id: int, project_id: int, base_branch_id: int, 
                     new_branch_name: str) -> Branch:
        """
        Create new branch from existing base branch
        
        Flow:
        1. Verify project exists and user owns it
        2. Verify base branch exists and belongs to project
        3. Verify new branch name is unique in project
        4. Copy base branch's head_commit_id to new branch
        5. Create new branch with inherited HEAD
        """
        # Verify project ownership
        project = self.project_repo.get_project_by_id(project_id)
        if not project:
            raise ValueError(f"Project {project_id} not found")
        if project.owner_id != user_id:
            raise PermissionError(f"User {user_id} does not own project {project_id}")
        
        # Verify base branch exists and belongs to project
        base_branch = self.branch_repo.get_branch_by_id(base_branch_id)
        if not base_branch:
            raise ValueError(f"Base branch {base_branch_id} not found")
        if base_branch.project_id != project_id:
            raise ValueError(f"Base branch does not belong to project {project_id}")
        
        # Validate branch name
        if not new_branch_name or len(new_branch_name.strip()) == 0:
            raise ValueError("Branch name cannot be empty")
        if len(new_branch_name) > 255:
            raise ValueError("Branch name must be <= 255 characters")
        
        # Check name uniqueness in project
        existing = self.branch_repo.get_branch_by_name(project_id, new_branch_name)
        if existing:
            raise ValueError(f"Branch '{new_branch_name}' already exists in project {project_id}")
        
        # Create new branch with inherited HEAD from base branch
        branch_data = BranchCreate(
            name=new_branch_name,
            project_id=project_id,
            created_from=base_branch_id
        )
        new_branch = self.branch_repo.create_branch(branch_data)
        
        # Copy base branch's HEAD to new branch
        if base_branch.head_commit_id:
            self.branch_repo.update_branch_head_commit(
                new_branch.id,
                base_branch.head_commit_id
            )
            # Refresh to get updated object
            new_branch = self.branch_repo.get_branch_by_id(new_branch.id)
        
        return new_branch

    def list_branches(self, project_id: int, skip: int = 0, limit: int = 100) -> list[Branch]:
        """
        List all branches in a project
        """
        # Verify project exists
        project = self.project_repo.get_project_by_id(project_id)
        if not project:
            raise ValueError(f"Project {project_id} not found")
        
        return self.branch_repo.get_branches_by_project(project_id, skip=skip, limit=limit)

    def get_branch(self, branch_id: int) -> Branch | None:
        """
        Get branch by ID
        """
        branch = self.branch_repo.get_branch_by_id(branch_id)
        if not branch:
            raise ValueError(f"Branch {branch_id} not found")
        return branch
