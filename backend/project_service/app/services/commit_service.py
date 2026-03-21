from sqlalchemy.orm import Session
from datetime import datetime
import hashlib
from ..models import Commit, Branch
from ..schemas import CommitCreate
from ..repositories import CommitRepository, BranchRepository, ProjectRepository
from ..exceptions import ForbiddenError, NotFoundError, ValidationError


class CommitService:
    """
    Business logic layer for Commits
    Handles commit creation, parent logic, and history navigation
    
    AUTHORIZATION RULES:
    - Only project members (owner) can create commits
    - Any user can read commit history
    - Commit author is always the current user (cannot be overridden)
    """

    def __init__(self, db: Session):
        self.db = db
        self.commit_repo = CommitRepository(db)
        self.branch_repo = BranchRepository(db)
        self.project_repo = ProjectRepository(db)

    def create_commit(self, user_id: int, branch_id: int, message: str, author_id: int) -> Commit:
        """
        Create new commit on a branch
        
        AUTHORIZATION: Only project owner can create commits
        Note: author_id from JWT is used, client cannot override
        
        Flow:
        1. Verify branch exists
        2. Verify user owns the project that contains this branch
        3. Get current branch HEAD
        4. Create new commit with HEAD as parent
        5. Update branch HEAD to new commit
        
        Important: Service decides the parent automatically from branch HEAD.
        Client cannot override parent. Author is always the authenticated user.
        
        Raises:
        - NotFoundError: Branch doesn't exist
        - ForbiddenError: User is not project owner
        - ValidationError: Invalid message
        """
        # Verify branch exists
        branch = self.branch_repo.get_branch_by_id(branch_id)
        if not branch:
            raise NotFoundError(f"Branch {branch_id} not found")
        
        # AUTHORIZATION CHECK: Verify user owns the project
        project = self.project_repo.get_project_by_id(branch.project_id)
        if not project or project.owner_id != user_id:
            raise ForbiddenError(f"You do not own the project containing branch {branch_id}")
        
        # Validate message
        if not message or len(message.strip()) == 0:
            raise ValidationError("Commit message cannot be empty")
        
        # Generate commit ID (SHA-like hash)
        # Note: Always use the authenticated user's ID, not client-provided author_id
        commit_id = self._generate_commit_id(message, branch_id, user_id)
        
        # Create commit with current branch HEAD as parent
        # Author is always the current authenticated user
        commit_data = CommitCreate(
            id=commit_id,
            message=message,
            branch_id=branch_id,
            parent_commit_id=branch.head_commit_id,  # Automatically set from branch HEAD
            author_id=user_id  # Always use authenticated user
        )
        new_commit = self.commit_repo.create_commit(commit_data)
        
        # Update branch HEAD to new commit
        self.branch_repo.update_branch_head_commit(branch_id, new_commit.id)
        
        return new_commit

    def get_commit(self, commit_id: str) -> Commit | None:
        """
        Get single commit
        
        AUTHORIZATION: Any user can read commits (read-only)
        
        Raises:
        - NotFoundError: Commit doesn't exist
        """
        commit = self.commit_repo.get_commit_by_id(commit_id)
        if not commit:
            raise NotFoundError(f"Commit {commit_id} not found")
        return commit

    def get_branch_history(self, branch_id: int, limit: int = 100) -> list[Commit]:
        """
        Get commit history for a branch
        
        AUTHORIZATION: Any user can read commit history (read-only)
        
        Flow:
        1. Verify branch exists
        2. Get all commits on branch
        3. Return commits in reverse chronological order
        
        Raises:
        - NotFoundError: Branch doesn't exist
        """
        # Verify branch exists
        branch = self.branch_repo.get_branch_by_id(branch_id)
        if not branch:
            raise NotFoundError(f"Branch {branch_id} not found")
        
        # Get commits on branch
        commits = self.commit_repo.get_commits_by_branch(branch_id, skip=0, limit=limit)
        return commits

    def get_commit_parent(self, commit_id: str) -> Commit | None:
        """
        Get parent commit (graph traversal)
        
        AUTHORIZATION: Any user can traverse commit graph (read-only)
        """
        return self.commit_repo.get_commit_parent(commit_id)

    def get_commit_children(self, commit_id: str) -> list[Commit]:
        """
        Get child commits (reverse graph traversal)
        
        AUTHORIZATION: Any user can traverse commit graph (read-only)
        """
        return self.commit_repo.get_commit_children(commit_id)

    def _generate_commit_id(self, message: str, branch_id: int, author_id: int) -> str:
        """
        Generate unique commit ID (simplified SHA-like hash)
        
        In real Git, this would be a full SHA-1 of the tree contents.
        For MVP, we generate from message + branch + author + timestamp.
        """
        timestamp = int(datetime.utcnow().timestamp())
        combined = f"{message}{branch_id}{author_id}{timestamp}"
        hash_obj = hashlib.sha256(combined.encode())
        return hash_obj.hexdigest()[:16]  # First 16 chars (64-bit)
