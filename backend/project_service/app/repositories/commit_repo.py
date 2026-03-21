from sqlalchemy.orm import Session
from sqlalchemy import desc
from ..models import Commit
from ..schemas import CommitCreate


class CommitRepository:
    """
    Database access layer for Commits
    Supports commit graph traversal (parent/child relationships)
    ONLY data queries - NO business logic
    """

    def __init__(self, db: Session):
        self.db = db

    def create_commit(self, commit_data: CommitCreate) -> Commit:
        """Insert new commit into database"""
        db_commit = Commit(
            id=commit_data.id,
            message=commit_data.message,
            branch_id=commit_data.branch_id,
            parent_commit_id=commit_data.parent_commit_id,
            author_id=commit_data.author_id
        )
        self.db.add(db_commit)
        self.db.commit()
        self.db.refresh(db_commit)
        return db_commit

    def get_commit_by_id(self, commit_id: str) -> Commit | None:
        """Get commit by hash ID"""
        return self.db.query(Commit).filter(Commit.id == commit_id).first()

    def get_commits_by_branch(self, branch_id: int, skip: int = 0, limit: int = 100) -> list[Commit]:
        """Get all commits on a branch, newest first (branch history)"""
        return self.db.query(Commit).filter(
            Commit.branch_id == branch_id
        ).order_by(desc(Commit.timestamp)).offset(skip).limit(limit).all()

    def get_commit_parent(self, commit_id: str) -> Commit | None:
        """Get parent commit (commit graph traversal)"""
        commit = self.get_commit_by_id(commit_id)
        if not commit or not commit.parent_commit_id:
            return None
        return self.get_commit_by_id(commit.parent_commit_id)

    def get_commit_children(self, parent_commit_id: str) -> list[Commit]:
        """Get all child commits (reverse graph traversal)"""
        return self.db.query(Commit).filter(
            Commit.parent_commit_id == parent_commit_id
        ).all()

    def get_commits_by_author(self, author_id: int, branch_id: int | None = None, 
                             skip: int = 0, limit: int = 100) -> list[Commit]:
        """Get all commits by author, optionally filtered by branch"""
        query = self.db.query(Commit).filter(Commit.author_id == author_id)
        
        if branch_id is not None:
            query = query.filter(Commit.branch_id == branch_id)
        
        return query.order_by(desc(Commit.timestamp)).offset(skip).limit(limit).all()

    def delete_commit(self, commit_id: str) -> bool:
        """Delete commit by ID"""
        commit = self.get_commit_by_id(commit_id)
        if not commit:
            return False
        
        self.db.delete(commit)
        self.db.commit()
        return True
