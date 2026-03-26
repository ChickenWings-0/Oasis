from sqlalchemy import Column, Integer, String, Text, DateTime, ForeignKey, func
from sqlalchemy.orm import relationship
from ..database import Base


class Commit(Base):
    __tablename__ = "commits"

    id = Column(String(64), primary_key=True, index=True)  # SHA-like hash
    message = Column(Text, nullable=False)
    branch_id = Column(Integer, ForeignKey("branches.id", ondelete="CASCADE"), nullable=False, index=True)
    parent_commit_id = Column(String(64), ForeignKey("commits.id", ondelete="SET NULL"), nullable=True)
    author_id = Column(Integer, nullable=False)  # References user_services user id
    timestamp = Column(DateTime, default=func.now(), nullable=False, index=True)

    # Relationships
    branch = relationship("Branch", back_populates="commits", lazy="select")
    parent_commit = relationship("Commit", remote_side=[id], backref="child_commits", lazy="select")

    def __repr__(self):
        return f"<Commit(id={self.id[:8]}, message={self.message[:50]}, branch_id={self.branch_id})>"
