from sqlalchemy import Column, Integer, String, Text, DateTime, ForeignKey, func
from sqlalchemy.orm import relationship
from ..database import Base


class Project(Base):
    __tablename__ = "projects"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(255), nullable=False, index=True)
    description = Column(Text, nullable=True)
    owner_id = Column(Integer, nullable=False)  # References user_services users.id
    team_id = Column(Integer, ForeignKey("teams.id"), nullable=True)
    created_at = Column(DateTime, default=func.now(), nullable=False)

    # Relationships
    branches = relationship(
        "Branch",
        back_populates="project",
        cascade="all, delete-orphan",
        lazy="select"
    )
    team = relationship("Team")

    def __repr__(self):
        return f"<Project(id={self.id}, name={self.name}, owner_id={self.owner_id})>"
