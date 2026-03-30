from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session

from backend.user_services.database import get_db
from backend.user_services.dependencies import get_current_user
from backend.user_services.friends.friend_schemas import FriendListResponse, FriendRequestCreate, FriendshipResponse
from backend.user_services.friends.friend_service import FriendService
from backend.user_services.models import User


router = APIRouter(
    prefix="/api/friends",
    tags=["friends"],
)


def _friendship_to_dict(friendship) -> dict:
    return {
        "id": friendship.id,
        "requester_id": friendship.requester_id,
        "receiver_id": friendship.receiver_id,
        "status": friendship.status.value if hasattr(friendship.status, "value") else str(friendship.status),
        "created_at": friendship.created_at,
    }


@router.post(
    "/request",
    response_model=FriendshipResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Send a friend request",
)
def send_friend_request(
    payload: FriendRequestCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    service = FriendService(db)
    friendship = service.create_friend_request(current_user.id, payload.receiver_id)
    return friendship


@router.get(
    "/requests",
    response_model=list[FriendshipResponse],
    status_code=status.HTTP_200_OK,
    summary="Get pending friend requests",
)
def get_pending_friend_requests(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    service = FriendService(db)
    return service.get_pending_requests(current_user.id)


@router.post(
    "/{friendship_id}/accept",
    status_code=status.HTTP_200_OK,
    summary="Accept a friend request",
)
def accept_friend_request(
    friendship_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    service = FriendService(db)
    friendship = service.accept_request(friendship_id, current_user.id)
    return {
        "detail": "Friend request accepted",
        "friendship": _friendship_to_dict(friendship),
    }


@router.post(
    "/{friendship_id}/reject",
    status_code=status.HTTP_200_OK,
    summary="Reject a friend request",
)
def reject_friend_request(
    friendship_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    service = FriendService(db)
    friendship = service.reject_request(friendship_id, current_user.id)
    return {
        "detail": "Friend request rejected",
        "friendship": _friendship_to_dict(friendship),
    }


@router.get(
    "",
    response_model=list[FriendListResponse],
    status_code=status.HTTP_200_OK,
    summary="Get accepted friends",
)
def get_accepted_friends(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    service = FriendService(db)
    return service.get_friends(current_user.id)
