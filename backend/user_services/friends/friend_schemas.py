from datetime import datetime
from typing import Optional

from pydantic import BaseModel, Field


class FriendRequestCreate(BaseModel):
    receiver_id: int = Field(..., gt=0)

    class Config:
        json_schema_extra = {
            "example": {
                "receiver_id": 2,
            }
        }


class FriendshipResponse(BaseModel):
    id: int
    requester_id: int
    receiver_id: int
    status: str
    created_at: datetime

    class Config:
        from_attributes = True
        json_schema_extra = {
            "example": {
                "id": 1,
                "requester_id": 1,
                "receiver_id": 2,
                "status": "pending",
                "created_at": "2026-03-29T10:00:00",
            }
        }


class FriendListResponse(BaseModel):
    friend_id: int
    username: str
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    since: datetime

    class Config:
        from_attributes = True
        json_schema_extra = {
            "example": {
                "friend_id": 2,
                "username": "jane_doe",
                "first_name": "Jane",
                "last_name": "Doe",
                "since": "2026-03-20T09:30:00",
            }
        }
