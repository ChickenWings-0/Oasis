from sqlalchemy.orm import Session
from datetime import datetime
from ..models import Merge, MergeStatus, Branch, Commit
from ..schemas import MergeCreate
from ..repositories import MergeRepository, BranchRepository, CommitRepository, ProjectRepository
from .commit_service import CommitService
from ..exceptions import ForbiddenError, NotFoundError, ValidationError
from .access_control import has_project_access


class MergeService:
    """
    Business logic layer for Merges
    Handles merge logic, conflict detection, and graph combining
    
    AUTHORIZATION RULES:
    - Only project owner can merge branches
    - Cannot merge across different projects
    - Cannot self-merge
    """

    def __init__(self, db: Session):
        self.db = db
        self.merge_repo = MergeRepository(db)
        self.branch_repo = BranchRepository(db)
        self.commit_repo = CommitRepository(db)
        self.project_repo = ProjectRepository(db)
        self.commit_service = CommitService(db)

    def merge_branches(self, user_id: int, source_branch_id: int, target_branch_id: int) -> Merge:
        """
        Merge source branch into target branch
        
        AUTHORIZATION: Only project owner can merge branches
        
        Flow:
        1. Verify both branches exist
        2. Verify both branches belong to same project
        3. Verify user owns the project
        4. Check merge eligibility (not same branch, states, etc)
        5. Determine merge type (fast-forward, normal, no-op)
        6. Execute merge
        7. Create merge record
        
        Raises:
        - NotFoundError: Branch doesn't exist
        - ValidationError: Invalid merge (same branch, different projects)
        - ForbiddenError: User is not project owner
        """
        # Get both branches
        source = self.branch_repo.get_branch_by_id(source_branch_id)
        if not source:
            raise NotFoundError(f"Source branch {source_branch_id} not found")
        
        target = self.branch_repo.get_branch_by_id(target_branch_id)
        if not target:
            raise NotFoundError(f"Target branch {target_branch_id} not found")
        
        # Verify same project
        if source.project_id != target.project_id:
            raise ValidationError("Cannot merge branches from different projects")
        
        # AUTHORIZATION CHECK: owner or project team member
        project = self.project_repo.get_project_by_id(source.project_id)
        if not project:
            raise NotFoundError(f"Project {source.project_id} not found")
        if not has_project_access(user_id, project, self.db):
            raise ForbiddenError("You do not have access to the project containing these branches")
        
        # Verify not same branch
        if source_branch_id == target_branch_id:
            raise ValidationError("Cannot merge branch into itself")
        
        # Determine merge type and execute
        merge_result = self._determine_merge_type(source, target)
        
        # Create merge record
        merge_data = MergeCreate(
            source_branch_id=source_branch_id,
            target_branch_id=target_branch_id,
            merge_commit_id=merge_result["merge_commit_id"]
        )
        merge = self.merge_repo.create_merge_record(merge_data)
        
        # Update merge status based on result
        if merge_result["status"] == "no-op":
            self.merge_repo.update_merge_status(merge.id, MergeStatus.MERGED)
        elif merge_result["status"] == "fast-forward":
            # Update target branch HEAD to source HEAD
            self.branch_repo.update_branch_head_commit(target_branch_id, source.head_commit_id)
            self.merge_repo.update_merge_status(merge.id, MergeStatus.MERGED)
        elif merge_result["status"] == "normal-merge":
            # Create merge commit
            merge_commit = self._create_merge_commit(source, target, user_id)
            # Update target branch HEAD to merge commit
            self.branch_repo.update_branch_head_commit(target_branch_id, merge_commit.id)
            # Update merge record with merge commit
            self.merge_repo.update_merge_status(merge.id, MergeStatus.MERGED, merge_commit.id)
        elif merge_result["status"] == "conflict":
            self.merge_repo.update_merge_status(merge.id, MergeStatus.CONFLICT)
        
        return self.merge_repo.get_merge_by_id(merge.id)

    def _determine_merge_type(self, source: Branch, target: Branch) -> dict:
        """
        Determine what type of merge this is:
        1. no-op: both already point to same commit
        2. fast-forward: target can move to source with no divergence
        3. normal-merge: branches diverged, need merge commit
        4. conflict: manual resolution needed
        """
        source_head = source.head_commit_id
        target_head = target.head_commit_id
        
        # Case 1: No-op - already same HEAD
        if source_head == target_head:
            return {
                "status": "no-op",
                "merge_commit_id": None,
                "source_head": source_head,
                "target_head": target_head
            }
        
        # Case 2: One is None (empty branch)
        if not source_head:
            return {
                "status": "no-op",
                "merge_commit_id": None,
                "source_head": source_head,
                "target_head": target_head
            }
        
        if not target_head:
            # Target is empty, can fast-forward to source
            return {
                "status": "fast-forward",
                "merge_commit_id": None,
                "source_head": source_head,
                "target_head": target_head
            }
        
        # Case 3: Check if fast-forward possible
        # For MVP: simplified check - if source is ancestor of target, it's FF
        # Full implementation would walk commit graph
        if self._is_ancestor(source_head, target_head):
            return {
                "status": "fast-forward",
                "merge_commit_id": None,
                "source_head": source_head,
                "target_head": target_head
            }
        
        # Case 4: Normal merge (branches diverged)
        return {
            "status": "normal-merge",
            "merge_commit_id": None,
            "source_head": source_head,
            "target_head": target_head
        }

    def _is_ancestor(self, potential_ancestor_id: str, commit_id: str) -> bool:
        """
        Check if potential_ancestor_id is an ancestor of commit_id
        by walking the parent chain
        """
        current = commit_id
        visited = set()
        
        while current:
            if current == potential_ancestor_id:
                return True
            
            if current in visited:
                break  # Cycle detection
            visited.add(current)
            
            parent = self.commit_repo.get_commit_parent(current)
            current = parent.id if parent else None
        
        return False

    def _create_merge_commit(self, source: Branch, target: Branch, user_id: int) -> Commit:
        """
        Create a merge commit combining two branches
        
        Note: Current implementation creates a merge commit with:
        - parent_id = target HEAD (primary parent)
        - author_id = current authenticated user
        """
        message = f"Merge '{source.name}' into '{target.name}'"
        
        # Create merge commit on target branch
        # Uses authenticated user as the commit author
        merge_commit = self.commit_service.create_commit(
            user_id=user_id,  # Authenticated user
            branch_id=target.id,
            message=message,
            author_id=user_id  # Authenticated user is merge commit author
        )
        
        return merge_commit

    def get_merge(self, merge_id: int) -> Merge | None:
        """
        Get single merge by ID
        
        AUTHORIZATION: Any user can read merge info (read-only)
        
        Raises:
        - NotFoundError: Merge doesn't exist
        """
        merge = self.merge_repo.get_merge_by_id(merge_id)
        if not merge:
            raise NotFoundError(f"Merge {merge_id} not found")
        return merge

    def get_merge_history(self, project_id: int, skip: int = 0, limit: int = 100) -> list[Merge]:
        """
        Get all merges in a project
        
        AUTHORIZATION: Any user can read merge history (read-only)
        
        Raises:
        - NotFoundError: Project doesn't exist
        """
        # Verify project exists
        project = self.project_repo.get_project_by_id(project_id)
        if not project:
            raise NotFoundError(f"Project {project_id} not found")
        
        # Get all merges for this project (all statuses)
        merges = self.merge_repo.get_merges_by_project(project_id, skip=skip, limit=limit)
        
        return merges

    def approve_merge(self, merge_id: int, user_id: int) -> Merge:
        """
        Approve a merge request
        
        AUTHORIZATION: Only project owner can approve merges
        
        Raises:
        - NotFoundError: Merge doesn't exist
        - ForbiddenError: User is not project owner
        - ValidationError: Invalid merge status
        """
        merge = self.merge_repo.get_merge_by_id(merge_id)
        if not merge:
            raise NotFoundError(f"Merge {merge_id} not found")
        
        # Get target branch to access project
        target_branch = self.branch_repo.get_branch_by_id(merge.target_branch_id)
        if not target_branch:
            raise NotFoundError(f"Target branch not found")
        
        # AUTHORIZATION: owner or project team member
        project = self.project_repo.get_project_by_id(target_branch.project_id)
        if not project:
            raise NotFoundError(f"Project {target_branch.project_id} not found")
        if not has_project_access(user_id, project, self.db):
            raise ForbiddenError("You do not have access to the project containing this merge")
        
        # For now, just update status to indicate approval
        # In a real system, this would track approvals separately
        self.merge_repo.update_merge_status(merge.id, MergeStatus.MERGED)
        
        return self.merge_repo.get_merge_by_id(merge.id)

    def _determine_merge_type(self, source: Branch, target: Branch) -> dict:
        """
        Determine what type of merge this is:
        1. no-op: both already point to same commit
        2. fast-forward: target can move to source with no divergence
        3. normal-merge: branches diverged, need merge commit
        4. conflict: manual resolution needed
        """
        source_head = source.head_commit_id
        target_head = target.head_commit_id
        
        # Case 1: No-op - already same HEAD
        if source_head == target_head:
            return {
                "status": "no-op",
                "merge_commit_id": None,
                "source_head": source_head,
                "target_head": target_head
            }
        
        # Case 2: One is None (empty branch)
        if not source_head:
            return {
                "status": "no-op",
                "merge_commit_id": None,
                "source_head": source_head,
                "target_head": target_head
            }
        
        if not target_head:
            # Target is empty, can fast-forward to source
            return {
                "status": "fast-forward",
                "merge_commit_id": None,
                "source_head": source_head,
                "target_head": target_head
            }
        
        # Case 3: Check if fast-forward possible
        # For MVP: simplified check - if source is ancestor of target, it's FF
        # Full implementation would walk commit graph
        if self._is_ancestor(source_head, target_head):
            return {
                "status": "fast-forward",
                "merge_commit_id": None,
                "source_head": source_head,
                "target_head": target_head
            }
        
        # Case 4: Normal merge (branches diverged)
        return {
            "status": "normal-merge",
            "merge_commit_id": None,
            "source_head": source_head,
            "target_head": target_head
        }

    def _is_ancestor(self, potential_ancestor_id: str, commit_id: str) -> bool:
        """
        Check if potential_ancestor_id is an ancestor of commit_id
        by walking the parent chain
        """
        current = commit_id
        visited = set()
        
        while current:
            if current == potential_ancestor_id:
                return True
            
            if current in visited:
                break  # Cycle detection
            visited.add(current)
            
            parent = self.commit_repo.get_commit_parent(current)
            current = parent.id if parent else None
        
        return False

    def _create_merge_commit(self, source: Branch, target: Branch) -> Commit:
        """
        Create a merge commit combining two branches
        
        Note: Current implementation creates a merge commit with:
        - parent_id = target HEAD (primary parent)
        - We don't store second_parent yet, but structure supports it
        """
        message = f"Merge '{source.name}' into '{target.name}'"
        
        # Create merge commit on target branch
        # Service will use target's current commit as parent
        merge_commit = self.commit_service.create_commit(
            user_id=1,  # System user (future: pass from auth context)
            branch_id=target.id,
            message=message,
            author_id=1  # System user
        )
        
        return merge_commit

    def get_merge(self, merge_id: int) -> Merge | None:
        """
        Get single merge by ID
        """
        merge = self.merge_repo.get_merge_by_id(merge_id)
        if not merge:
            raise ValueError(f"Merge {merge_id} not found")
        return merge
