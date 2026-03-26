from pydantic import BaseModel, Field
from typing import Optional, Literal
from datetime import datetime


class MergeCreate(BaseModel):
    """Schema for creating a new merge request"""
    source_branch_id: int = Field(..., description="Source branch ID")
    target_branch_id: int = Field(..., description="Target branch ID")
    merge_commit_id: Optional[str] = Field(None, max_length=64, description="Merge commit ID (if merged)")

    class Config:
        json_schema_extra = {
            "example": {
                "source_branch_id": 2,
                "target_branch_id": 1,
                "merge_commit_id": None
            }
        }


class MergeUpdate(BaseModel):
    """Schema for updating a merge request"""
    status: Optional[Literal["merged", "conflict", "pending"]] = Field(None, description="Merge status")
    merge_commit_id: Optional[str] = Field(None, max_length=64, description="Merge commit ID")

    class Config:
        json_schema_extra = {
            "example": {
                "status": "merged",
                "merge_commit_id": "m1e2r3g4e5c6o7m8m9i0t1h2a3s4h5"
            }
        }


class MergeResponse(BaseModel):
    """Schema for merge responses"""
    id: int
    source_branch_id: int
    target_branch_id: int
    merge_commit_id: Optional[str]
    status: str  # ENUM: merged, conflict, pending
    created_at: datetime
    merged_at: Optional[datetime]

    class Config:
        from_attributes = True
        json_schema_extra = {
            "example": {
                "id": 1,
                "source_branch_id": 2,
                "target_branch_id": 1,
                "merge_commit_id": "m1e2r3g4e5c6o7m8m9i0t1h2a3s4h5",
                "status": "merged",
                "created_at": "2026-03-21T19:00:00",
                "merged_at": "2026-03-21T20:00:00"
            }
        }


class MergeDetail(MergeResponse):
    """Extended merge response with branch details"""
    source_branch: Optional['BranchResponse'] = None
    target_branch: Optional['BranchResponse'] = None

    class Config:
        from_attributes = True


# Import here to avoid circular imports
from .branch_schema import BranchResponse
