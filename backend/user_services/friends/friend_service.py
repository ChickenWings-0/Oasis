from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from backend.user_services.friends.friend_model import Friendship, FriendshipStatus
from backend.user_services.friends.friend_repo import FriendshipRepository
from backend.user_services.friends.friend_schemas import FriendListResponse
from backend.user_services.models import User


class FriendService:
    def __init__(self, db: Session):
        self.db = db
        self.friendship_repo = FriendshipRepository(db)

    def _get_user_or_404(self, user_id: int) -> User:
        user = self.db.query(User).filter(User.id == user_id).first()
        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"User {user_id} not found",
            )
        return user

    def create_friend_request(self, requester_id: int, receiver_id: int) -> Friendship:
        self._get_user_or_404(requester_id)
        self._get_user_or_404(receiver_id)

        if requester_id == receiver_id:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="You cannot send a friend request to yourself",
            )

        existing = self.friendship_repo.get_existing(requester_id, receiver_id)
        if existing:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Friend request already exists between these users",
            )

        return self.friendship_repo.create_friendship(requester_id, receiver_id)

    def get_pending_requests(self, user_id: int) -> list[Friendship]:
        self._get_user_or_404(user_id)
        return self.friendship_repo.get_pending_for_user(user_id)

    def accept_request(self, friendship_id: int, current_user_id: int) -> Friendship:
        friendship = self.friendship_repo.get_by_id(friendship_id)
        if friendship is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Friend request not found",
            )

        if friendship.receiver_id != current_user_id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Only the receiver can accept this request",
            )

        if friendship.status != FriendshipStatus.PENDING:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Only pending requests can be accepted",
            )

        updated = self.friendship_repo.update_status(friendship.id, FriendshipStatus.ACCEPTED)
        if updated is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Friend request not found",
            )
        return updated

    def reject_request(self, friendship_id: int, current_user_id: int) -> Friendship:
        friendship = self.friendship_repo.get_by_id(friendship_id)
        if friendship is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Friend request not found",
            )

        if friendship.receiver_id != current_user_id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Only the receiver can reject this request",
            )

        if friendship.status != FriendshipStatus.PENDING:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Only pending requests can be rejected",
            )

        updated = self.friendship_repo.update_status(friendship.id, FriendshipStatus.REJECTED)
        if updated is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Friend request not found",
            )
        return updated

    def get_friends(self, user_id: int) -> list[FriendListResponse]:
        self._get_user_or_404(user_id)
        friendships = self.friendship_repo.get_accepted_friends(user_id)

        if not friendships:
            return []

        friend_ids = []
        for friendship in friendships:
            friend_id = friendship.receiver_id if friendship.requester_id == user_id else friendship.requester_id
            friend_ids.append(friend_id)

        friends = self.db.query(User).filter(User.id.in_(friend_ids)).all()
        friends_by_id = {friend.id: friend for friend in friends}

        response: list[FriendListResponse] = []
        for friendship in friendships:
            friend_id = friendship.receiver_id if friendship.requester_id == user_id else friendship.requester_id
            friend_user = friends_by_id.get(friend_id)
            if friend_user is None:
                continue

            response.append(
                FriendListResponse(
                    friend_id=friend_user.id,
                    username=friend_user.username,
                    first_name=friend_user.first_name,
                    last_name=friend_user.last_name,
                    since=friendship.created_at,
                )
            )

        return response
