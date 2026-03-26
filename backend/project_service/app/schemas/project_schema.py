from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime


class ProjectCreate(BaseModel):
    """Schema for creating a new project"""
    name: str = Field(..., min_length=1, max_length=255, description="Project name")
    description: Optional[str] = Field(None, max_length=2000, description="Project description")
    owner_id: Optional[int] = Field(None, description="User ID of project owner (auto-set from JWT)")

    class Config:
        json_schema_extra = {
            "example": {
                "name": "AI Content Creator",
                "description": "Platform for AI-powered content creation",
                "owner_id": 1
            }
        }


class ProjectUpdate(BaseModel):
    """Schema for updating a project"""
    name: Optional[str] = Field(None, min_length=1, max_length=255)
    description: Optional[str] = Field(None, max_length=2000)

    class Config:
        json_schema_extra = {
            "example": {
                "name": "Updated Project Name",
                "description": "Updated description"
            }
        }


class ProjectResponse(BaseModel):
    """Schema for project responses"""
    id: int
    name: str
    description: Optional[str]
    owner_id: int
    created_at: datetime

    class Config:
        from_attributes = True
        json_schema_extra = {
            "example": {
                "id": 1,
                "name": "AI Content Creator",
                "description": "Platform for AI-powered content creation",
                "owner_id": 1,
                "created_at": "2026-03-21T20:00:00"
            }
        }


class ProjectDetail(ProjectResponse):
    """Extended project response with related data"""
    branches: List['BranchResponse'] = []

    class Config:
        from_attributes = True


# Import here to avoid circular imports
from .branch_schema import BranchResponse
