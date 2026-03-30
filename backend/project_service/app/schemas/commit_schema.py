from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime


class CommitCreate(BaseModel):
    """Schema for creating a new commit"""
    id: str = Field(..., min_length=1, max_length=64, description="Commit hash/ID")
    message: str = Field(..., min_length=1, max_length=500, description="Commit message")
    branch_id: int = Field(..., description="Branch ID this commit belongs to")
    parent_commit_id: Optional[str] = Field(None, max_length=64, description="Parent commit ID (optional)")
    author_id: int = Field(..., description="User ID of commit author")

    class Config:
        json_schema_extra = {
            "example": {
                "id": "a1b2c3d4e5f6g7h8i9j0k1l2m3n4o5p6",
                "message": "Fix authentication bug in login route",
                "branch_id": 1,
                "parent_commit_id": None,
                "author_id": 1
            }
        }


class CommitResponse(BaseModel):
    """Schema for commit responses"""
    id: str
    message: str
    branch_id: int
    parent_commit_id: Optional[str]
    author_id: int
    timestamp: datetime

    class Config:
        from_attributes = True
        json_schema_extra = {
            "example": {
                "id": "a1b2c3d4e5f6g7h8i9j0k1l2m3n4o5p6",
                "message": "Fix authentication bug in login route",
                "branch_id": 1,
                "parent_commit_id": None,
                "author_id": 1,
                "timestamp": "2026-03-21T20:00:00"
            }
        }


class CommitDetail(CommitResponse):
    """Extended commit response"""
    parent_commit: Optional['CommitResponse'] = None
    child_commits: list['CommitResponse'] = []

    class Config:
        from_attributes = True
