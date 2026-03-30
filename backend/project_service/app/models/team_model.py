from enum import Enum as PyEnum

from sqlalchemy import Column, DateTime, Enum, ForeignKey, Integer, String, UniqueConstraint, func
from sqlalchemy.orm import relationship

from ..database import Base


class TeamRole(PyEnum):
    OWNER = "owner"
    ADMIN = "admin"
    MEMBER = "member"


class TeamInviteStatus(PyEnum):
    PENDING = "pending"
    ACCEPTED = "accepted"
    DECLINED = "declined"


class Team(Base):
    __tablename__ = "teams"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(255), nullable=False, index=True)
    owner_id = Column(Integer, nullable=False, index=True)  # User service user id
    created_at = Column(DateTime, default=func.now(), nullable=False)

    members = relationship("TeamMember", back_populates="team", cascade="all, delete-orphan", lazy="select")
    invites = relationship("TeamInvite", back_populates="team", cascade="all, delete-orphan", lazy="select")

    def __repr__(self):
        return f"<Team(id={self.id}, name={self.name}, owner_id={self.owner_id})>"


class TeamMember(Base):
    __tablename__ = "team_members"
    __table_args__ = (
        UniqueConstraint("team_id", "user_id", name="uq_team_members_team_user"),
    )

    id = Column(Integer, primary_key=True, index=True)
    team_id = Column(Integer, ForeignKey("teams.id", ondelete="CASCADE"), nullable=False, index=True)
    user_id = Column(Integer, nullable=False, index=True)  # User service user id
    role = Column(Enum(TeamRole, name="teamrole"), default=TeamRole.MEMBER, nullable=False, index=True)
    joined_at = Column(DateTime, default=func.now(), nullable=False)

    team = relationship("Team", back_populates="members", lazy="select")

    def __repr__(self):
        return f"<TeamMember(id={self.id}, team_id={self.team_id}, user_id={self.user_id}, role={self.role.value})>"


class TeamInvite(Base):
    __tablename__ = "team_invites"
    __table_args__ = (
        UniqueConstraint("team_id", "invited_user_id", name="uq_team_invites_team_invited_user"),
    )

    id = Column(Integer, primary_key=True, index=True)
    team_id = Column(Integer, ForeignKey("teams.id", ondelete="CASCADE"), nullable=False, index=True)
    invited_user_id = Column(Integer, nullable=False, index=True)  # User service user id
    invited_by = Column(Integer, nullable=False, index=True)  # User service user id
    status = Column(Enum(TeamInviteStatus, name="teaminvitestatus"), default=TeamInviteStatus.PENDING, nullable=False, index=True)
    created_at = Column(DateTime, default=func.now(), nullable=False)

    team = relationship("Team", back_populates="invites", lazy="select")

    def __repr__(self):
        return (
            f"<TeamInvite(id={self.id}, team_id={self.team_id}, invited_user_id={self.invited_user_id}, "
            f"status={self.status.value})>"
        )
