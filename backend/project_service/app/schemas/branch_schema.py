from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime


class BranchCreate(BaseModel):
    """Schema for creating a new branch"""
    name: str = Field(..., min_length=1, max_length=255, description="Branch name")
    project_id: int = Field(..., description="Project ID this branch belongs to")
    created_from: Optional[int] = Field(None, description="Parent branch ID (optional)")

    class Config:
        json_schema_extra = {
            "example": {
                "name": "feature/auth",
                "project_id": 1,
                "created_from": None
            }
        }


class BranchUpdate(BaseModel):
    """Schema for updating a branch"""
    name: Optional[str] = Field(None, min_length=1, max_length=255)

    class Config:
        json_schema_extra = {
            "example": {
                "name": "feature/auth-v2"
            }
        }


class BranchResponse(BaseModel):
    """Schema for branch responses"""
    id: int
    name: str
    project_id: int
    created_from: Optional[int]
    created_at: datetime

    class Config:
        from_attributes = True
        json_schema_extra = {
            "example": {
                "id": 1,
                "name": "main",
                "project_id": 1,
                "created_from": None,
                "created_at": "2026-03-21T20:00:00"
            }
        }


class BranchDetail(BranchResponse):
    """Branch response with related commits"""
    commits: List['CommitResponse'] = []

    class Config:
        from_attributes = True


# Import here to avoid circular imports
from .commit_schema import CommitResponse
