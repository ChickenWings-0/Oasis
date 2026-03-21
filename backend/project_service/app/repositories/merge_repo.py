from sqlalchemy.orm import Session
from sqlalchemy import desc
from datetime import datetime
from ..models import Merge, MergeStatus
from ..schemas import MergeCreate, MergeUpdate


class MergeRepository:
    """
    Database access layer for Merges
    Tracks merge requests and their status
    ONLY data queries - NO business logic
    """

    def __init__(self, db: Session):
        self.db = db

    def create_merge_record(self, merge_data: MergeCreate) -> Merge:
        """Insert new merge record (defaults to PENDING status)"""
        db_merge = Merge(
            source_branch_id=merge_data.source_branch_id,
            target_branch_id=merge_data.target_branch_id,
            merge_commit_id=merge_data.merge_commit_id,
            status=MergeStatus.PENDING
        )
        self.db.add(db_merge)
        self.db.commit()
        self.db.refresh(db_merge)
        return db_merge

    def get_merge_by_id(self, merge_id: int) -> Merge | None:
        """Get merge record by ID"""
        return self.db.query(Merge).filter(Merge.id == merge_id).first()

    def get_merges_by_source_branch(self, source_branch_id: int, skip: int = 0, limit: int = 100) -> list[Merge]:
        """Get all merges FROM a specific branch"""
        return self.db.query(Merge).filter(
            Merge.source_branch_id == source_branch_id
        ).order_by(desc(Merge.created_at)).offset(skip).limit(limit).all()

    def get_merges_by_target_branch(self, target_branch_id: int, skip: int = 0, limit: int = 100) -> list[Merge]:
        """Get all merges TO a specific branch"""
        return self.db.query(Merge).filter(
            Merge.target_branch_id == target_branch_id
        ).order_by(desc(Merge.created_at)).offset(skip).limit(limit).all()

    def get_pending_merges(self, skip: int = 0, limit: int = 100) -> list[Merge]:
        """Get all merges with PENDING status"""
        return self.db.query(Merge).filter(
            Merge.status == MergeStatus.PENDING
        ).order_by(desc(Merge.created_at)).offset(skip).limit(limit).all()

    def get_merges_by_project_branches(self, branch_id: int, skip: int = 0, limit: int = 100) -> list[Merge]:
        """Get all merges involving a branch (source OR target)"""
        return self.db.query(Merge).filter(
            (Merge.source_branch_id == branch_id) | 
            (Merge.target_branch_id == branch_id)
        ).order_by(desc(Merge.created_at)).offset(skip).limit(limit).all()

    def update_merge_status(self, merge_id: int, status: MergeStatus, 
                           merge_commit_id: str | None = None) -> Merge | None:
        """Update merge status and optionally set merge_commit_id"""
        merge = self.get_merge_by_id(merge_id)
        if not merge:
            return None
        
        merge.status = status
        if merge_commit_id:
            merge.merge_commit_id = merge_commit_id
        
        # Set merged_at timestamp when status changes to MERGED
        if status == MergeStatus.MERGED:
            merge.merged_at = datetime.utcnow()
        
        self.db.commit()
        self.db.refresh(merge)
        return merge

    def delete_merge(self, merge_id: int) -> bool:
        """Delete merge record by ID"""
        merge = self.get_merge_by_id(merge_id)
        if not merge:
            return False
        
        self.db.delete(merge)
        self.db.commit()
        return True
