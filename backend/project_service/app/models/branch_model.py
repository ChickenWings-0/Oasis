from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, func
from sqlalchemy.orm import relationship
from ..database import Base


class Branch(Base):
    __tablename__ = "branches"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(255), nullable=False, index=True)
    project_id = Column(Integer, ForeignKey("projects.id", ondelete="CASCADE"), nullable=False, index=True)
    created_from = Column(Integer, ForeignKey("branches.id", ondelete="SET NULL"), nullable=True)  # Self-reference
    head_commit_id = Column(String(64), nullable=True)  # ⭐ References current HEAD commit
    created_at = Column(DateTime, default=func.now(), nullable=False)

    # Relationships
    project = relationship("Project", back_populates="branches", lazy="select")
    commits = relationship("Commit", back_populates="branch", cascade="all, delete-orphan", lazy="select")
    source_merges = relationship("Merge", foreign_keys="Merge.source_branch_id", back_populates="source_branch", cascade="all, delete-orphan", lazy="select")
    target_merges = relationship("Merge", foreign_keys="Merge.target_branch_id", back_populates="target_branch", cascade="all, delete-orphan", lazy="select")
    parent_branch = relationship("Branch", remote_side=[id], backref="child_branches", lazy="select")

    def __repr__(self):
        return f"<Branch(id={self.id}, name={self.name}, project_id={self.project_id})>"
