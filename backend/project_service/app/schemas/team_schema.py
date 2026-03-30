from datetime import datetime

from pydantic import BaseModel, Field


class TeamCreate(BaseModel):
    name: str = Field(..., min_length=1, max_length=255)

    class Config:
        json_schema_extra = {
            "example": {
                "name": "Backend Squad"
            }
        }


class TeamResponse(BaseModel):
    id: int
    name: str
    owner_id: int
    created_at: datetime

    class Config:
        from_attributes = True


class TeamInviteCreate(BaseModel):
    invited_user_id: int = Field(..., gt=0)

    class Config:
        json_schema_extra = {
            "example": {
                "invited_user_id": 5
            }
        }


class TeamInviteResponse(BaseModel):
    id: int
    team_id: int
    invited_user_id: int
    invited_by: int
    status: str
    created_at: datetime

    class Config:
        from_attributes = True


class TeamMemberResponse(BaseModel):
    id: int
    team_id: int
    user_id: int
    role: str
    joined_at: datetime

    class Config:
        from_attributes = True
