from sqlalchemy.orm import Session
from ..models import Branch, Project
from ..schemas import BranchCreate
from ..repositories import BranchRepository, ProjectRepository
from ..exceptions import ForbiddenError, NotFoundError, ValidationError


class BranchService:

    def __init__(self, db: Session):
        self.db = db
        self.branch_repo = BranchRepository(db)
        self.project_repo = ProjectRepository(db)

    def create_branch(self, user_id: int, project_id: int, new_branch_name: str, 
                     base_branch_id: int = None) -> Branch:
        """
        Create new branch from existing base branch
        
        """
        # Verify project exists and get ownership
        project = self.project_repo.get_project_by_id(project_id)
        if not project:
            raise NotFoundError(f"Project {project_id} not found")
        
        # AUTHORIZATION CHECK: Verify project ownership
        if project.owner_id != user_id:
            raise ForbiddenError(f"You do not own project {project_id}")
        
        # If base_branch_id not provided, auto-select main branch
        if base_branch_id is None:
            main_branch = self.branch_repo.get_branch_by_name(project_id, "main")
            if main_branch:
                base_branch_id = main_branch.id
            else:
                # If no main branch, use the first branch in the project
                first_branch = self.branch_repo.list_branches(project_id, skip=0, limit=1)
                if not first_branch:
                    raise ValidationError(f"Project {project_id} has no branches. Cannot create branch from empty project.")
                base_branch_id = first_branch[0].id
        
        # Verify base branch exists and belongs to project
        base_branch = self.branch_repo.get_branch_by_id(base_branch_id)
        if not base_branch:
            raise NotFoundError(f"Base branch {base_branch_id} not found")
        if base_branch.project_id != project_id:
            raise ValidationError(f"Base branch does not belong to project {project_id}")
        
        # Validate branch name
        if not new_branch_name or len(new_branch_name.strip()) == 0:
            raise ValidationError("Branch name cannot be empty")
        if len(new_branch_name) > 255:
            raise ValidationError("Branch name must be <= 255 characters")
        
        # Check name uniqueness in project
        existing = self.branch_repo.get_branch_by_name(project_id, new_branch_name)
        if existing:
            raise ValidationError(f"Branch '{new_branch_name}' already exists in project {project_id}")
        
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
        
        AUTHORIZATION: Any user can list branches (read-only)
        
        Raises:
        - NotFoundError: Project doesn't exist
        """
        # Verify project exists
        project = self.project_repo.get_project_by_id(project_id)
        if not project:
            raise NotFoundError(f"Project {project_id} not found")
        
        return self.branch_repo.get_branches_by_project(project_id, skip=skip, limit=limit)

    def get_branch(self, branch_id: int) -> Branch | None:
        """
        Get branch by ID
        
        AUTHORIZATION: Any user can view branches (read-only)
        
        Raises:
        - NotFoundError: Branch doesn't exist
        """
        branch = self.branch_repo.get_branch_by_id(branch_id)
        if not branch:
            raise NotFoundError(f"Branch {branch_id} not found")
        return branch
