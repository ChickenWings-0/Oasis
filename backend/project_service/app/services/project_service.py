from sqlalchemy.orm import Session
from ..models import Project
from ..schemas import ProjectCreate
from ..repositories import ProjectRepository, BranchRepository, TeamRepository
from ..schemas import BranchCreate
from ..exceptions import ForbiddenError, NotFoundError, ValidationError
from .access_control import has_project_access
from ..models import TeamRole


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
        self.team_repo = TeamRepository(db)

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

        team_id = project_data.team_id
        if team_id is not None:
            team = self.team_repo.get_team_by_id(team_id)
            if not team:
                raise NotFoundError(f"Team {team_id} not found")

            if team.owner_id != user_id:
                membership = self.team_repo.get_member(team_id=team_id, user_id=user_id)
                allowed_roles = {TeamRole.OWNER, TeamRole.ADMIN}
                if not membership or membership.role not in allowed_roles:
                    raise ForbiddenError("Only team owner or admin can create projects for this team")
        
        # Create project (ownership set to user_id from auth)
        project_create = ProjectCreate(
            name=project_data.name,
            description=project_data.description,
            owner_id=user_id,
            team_id=team_id,
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
        
        # AUTHORIZATION CHECK: owner or project team member
        if not has_project_access(user_id, project, self.db):
            raise ForbiddenError(f"You do not have access to project {project_id}")
        
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
        project = self.project_repo.get_project_by_id(project_id)
        if not project:
            raise NotFoundError(f"Project {project_id} not found")

        # Delete remains owner-only
        if not has_project_access(user_id, project, self.db, require_role="owner"):
            raise ForbiddenError(f"Only the project owner can delete project {project_id}")
        
        return self.project_repo.delete_project(project_id)

    def update_project(self, user_id: int, project_id: int, project_data) -> Project:
        """
        Update project with ownership verification
        
        AUTHORIZATION: Only owner can update their project
        
        Rules:
        1. Project must exist
        2. Current user must be the owner
        3. Only provided fields are updated (partial update)
        
        Raises:
        - NotFoundError: Project doesn't exist
        - ForbiddenError: User is not the owner
        """
        # Verify access to project
        project = self.get_project(user_id, project_id)

        fields_set = getattr(project_data, "model_fields_set", None)
        if fields_set is None:
            fields_set = getattr(project_data, "__fields_set__", set())

        team_id_in_payload = "team_id" in fields_set
        
        # Update only provided fields
        updates = {}
        if project_data.name is not None:
            if len(project_data.name.strip()) == 0:
                raise ValidationError("Project name cannot be empty")
            if len(project_data.name) > 255:
                raise ValidationError("Project name must be <= 255 characters")
            updates['name'] = project_data.name
        
        if project_data.description is not None:
            if len(project_data.description) > 2000:
                raise ValidationError("Project description must be <= 2000 characters")
            updates['description'] = project_data.description

        # Team reassignment rules to prevent privilege escalation
        if team_id_in_payload and project_data.team_id != project.team_id:
            if project_data.team_id is None:
                # Removing team assignment is owner-only
                if project.owner_id != user_id:
                    raise ForbiddenError("Only the project owner can remove team assignment")
                updates['team_id'] = None
            else:
                target_team_id = project_data.team_id
                team = self.team_repo.get_team_by_id(target_team_id)
                if not team:
                    raise NotFoundError(f"Team {target_team_id} not found")

                # User must be owner/admin in the target team
                if team.owner_id != user_id:
                    membership = self.team_repo.get_member(team_id=target_team_id, user_id=user_id)
                    allowed_roles = {TeamRole.OWNER, TeamRole.ADMIN}
                    if not membership or membership.role not in allowed_roles:
                        raise ForbiddenError("Only team owner or admin can assign this project to the target team")

                updates['team_id'] = target_team_id
        
        # Apply updates if any
        if updates:
            return self.project_repo.update_project(project_id, **updates)
        
        return project
