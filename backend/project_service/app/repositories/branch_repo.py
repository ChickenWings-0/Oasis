from sqlalchemy.orm import Session
from sqlalchemy import desc
from ..models import Branch
from ..schemas import BranchCreate


class BranchRepository:
    """
    Database access layer for Branches
    ONLY data queries - NO business logic
    """

    def __init__(self, db: Session):
        self.db = db

    def create_branch(self, branch_data: BranchCreate) -> Branch:
        """Insert new branch into database"""
        db_branch = Branch(
            name=branch_data.name,
            project_id=branch_data.project_id,
            created_from=branch_data.created_from
        )
        self.db.add(db_branch)
        self.db.commit()
        self.db.refresh(db_branch)
        return db_branch

    def get_branch_by_id(self, branch_id: int) -> Branch | None:
        """Get branch by ID"""
        return self.db.query(Branch).filter(Branch.id == branch_id).first()

    def get_branch_by_name(self, project_id: int, name: str) -> Branch | None:
        """Get branch by name within a project"""
        return self.db.query(Branch).filter(
            Branch.project_id == project_id,
            Branch.name == name
        ).first()

    def get_branches_by_project(self, project_id: int, skip: int = 0, limit: int = 100) -> list[Branch]:
        """Get all branches for a project with pagination"""
        return self.db.query(Branch).filter(
            Branch.project_id == project_id
        ).order_by(desc(Branch.created_at)).offset(skip).limit(limit).all()

    def update_branch_head_commit(self, branch_id: int, commit_id: str) -> Branch | None:
        """⭐ CRITICAL: Update the HEAD commit ref for a branch"""
        branch = self.get_branch_by_id(branch_id)
        if not branch:
            return None
        
        branch.head_commit_id = commit_id
        self.db.commit()
        self.db.refresh(branch)
        return branch

    def delete_branch(self, branch_id: int) -> bool:
        """Delete branch by ID"""
        branch = self.get_branch_by_id(branch_id)
        if not branch:
            return False
        
        self.db.delete(branch)
        self.db.commit()
        return True
