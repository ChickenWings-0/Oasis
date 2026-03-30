from datetime import datetime
from enum import Enum

from sqlalchemy import CheckConstraint, Column, DateTime, Enum as SQLEnum, ForeignKey, Integer, UniqueConstraint

from backend.user_services.database import Base


class FriendshipStatus(str, Enum):
    PENDING = "pending"
    ACCEPTED = "accepted"
    REJECTED = "rejected"


class Friendship(Base):
    __tablename__ = "friendships"
    __table_args__ = (
        UniqueConstraint("requester_id", "receiver_id", name="uq_friendships_requester_receiver"),
        CheckConstraint("requester_id != receiver_id", name="ck_friendships_no_self_request"),
    )

    id = Column(Integer, primary_key=True, index=True)
    requester_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    receiver_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    status = Column(
        SQLEnum(FriendshipStatus, name="friendship_status", native_enum=False),
        nullable=False,
        default=FriendshipStatus.PENDING,
        index=True,
    )
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)

    def __repr__(self):
        return (
            f"<Friendship(id={self.id}, requester_id={self.requester_id}, "
            f"receiver_id={self.receiver_id}, status={self.status.value})>"
        )
