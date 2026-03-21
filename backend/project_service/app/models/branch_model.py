from sqlalchemy import Column, Integer, String, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from datetime import datetime
from ..database import Base


class Branch(Base):
    __tablename__ = "branches"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(255), nullable=False, index=True)
    project_id = Column(Integer, ForeignKey("projects.id", ondelete="CASCADE"), nullable=False, index=True)
    created_from = Column(Integer, ForeignKey("branches.id", ondelete="SET NULL"), nullable=True)  # Self-reference
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)

    # Relationships
    project = relationship("Project", back_populates="branches")
    commits = relationship("Commit", back_populates="branch", cascade="all, delete-orphan")
    source_merges = relationship("Merge", foreign_keys="Merge.source_branch_id", back_populates="source_branch")
    target_merges = relationship("Merge", foreign_keys="Merge.target_branch_id", back_populates="target_branch")
    parent_branch = relationship("Branch", remote_side=[id], backref="child_branches")

    def __repr__(self):
        return f"<Branch(id={self.id}, name={self.name}, project_id={self.project_id})>"
