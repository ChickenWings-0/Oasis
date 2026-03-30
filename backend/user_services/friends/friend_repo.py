from sqlalchemy import and_, or_
from sqlalchemy.orm import Session

from backend.user_services.friends.friend_model import Friendship, FriendshipStatus


class FriendshipRepository:
    def __init__(self, db: Session):
        self.db = db

    def create_friendship(self, requester_id: int, receiver_id: int) -> Friendship:
        friendship = Friendship(
            requester_id=requester_id,
            receiver_id=receiver_id,
            status=FriendshipStatus.PENDING,
        )
        self.db.add(friendship)
        self.db.commit()
        self.db.refresh(friendship)
        return friendship

    def get_by_id(self, friendship_id: int) -> Friendship | None:
        return self.db.query(Friendship).filter(Friendship.id == friendship_id).first()

    def get_existing(self, user_a_id: int, user_b_id: int) -> Friendship | None:
        return (
            self.db.query(Friendship)
            .filter(
                or_(
                    and_(
                        Friendship.requester_id == user_a_id,
                        Friendship.receiver_id == user_b_id,
                    ),
                    and_(
                        Friendship.requester_id == user_b_id,
                        Friendship.receiver_id == user_a_id,
                    ),
                )
            )
            .first()
        )

    def get_pending_for_user(self, user_id: int) -> list[Friendship]:
        return (
            self.db.query(Friendship)
            .filter(
                Friendship.receiver_id == user_id,
                Friendship.status == FriendshipStatus.PENDING,
            )
            .order_by(Friendship.created_at.desc())
            .all()
        )

    def get_accepted_friends(self, user_id: int) -> list[Friendship]:
        return (
            self.db.query(Friendship)
            .filter(
                Friendship.status == FriendshipStatus.ACCEPTED,
                or_(
                    Friendship.requester_id == user_id,
                    Friendship.receiver_id == user_id,
                ),
            )
            .order_by(Friendship.created_at.desc())
            .all()
        )

    def update_status(self, friendship_id: int, new_status: FriendshipStatus) -> Friendship | None:
        friendship = self.get_by_id(friendship_id)
        if friendship is None:
            return None

        friendship.status = new_status
        self.db.commit()
        self.db.refresh(friendship)
        return friendship
