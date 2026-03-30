from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Enum, func
from sqlalchemy.orm import relationship
from enum import Enum as PyEnum
from ..database import Base


class MergeStatus(PyEnum):
    MERGED = "merged"
    CONFLICT = "conflict"
    PENDING = "pending"


class Merge(Base):
    __tablename__ = "merges"

    id = Column(Integer, primary_key=True, index=True)
    source_branch_id = Column(Integer, ForeignKey("branches.id", ondelete="CASCADE"), nullable=False, index=True)
    target_branch_id = Column(Integer, ForeignKey("branches.id", ondelete="CASCADE"), nullable=False, index=True)
    merge_commit_id = Column(String(64), ForeignKey("commits.id", ondelete="SET NULL"), nullable=True)
    status = Column(Enum(MergeStatus, name="mergestatus"), default=MergeStatus.PENDING, nullable=False, index=True)
    created_at = Column(DateTime, default=func.now(), nullable=False)
    merged_at = Column(DateTime, nullable=True)

    # Relationships
    source_branch = relationship(
        "Branch",
        foreign_keys=[source_branch_id],
        back_populates="source_merges",
        lazy="select"
    )
    target_branch = relationship(
        "Branch",
        foreign_keys=[target_branch_id],
        back_populates="target_merges",
        lazy="select"
    )
    merge_commit = relationship("Commit", lazy="select")

    def __repr__(self):
        return f"<Merge(id={self.id}, {self.source_branch_id} -> {self.target_branch_id}, status={self.status.value})>"
