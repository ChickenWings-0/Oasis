from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from ..database import get_db
from ..dependencies.auth_dependency import CurrentUser, get_current_user
from ..exceptions import ForbiddenError, NotFoundError, ValidationError
from ..schemas import (
    TeamCreate,
    TeamInviteCreate,
    TeamInviteResponse,
    TeamMemberResponse,
    TeamResponse,
)
from ..services import TeamService


router = APIRouter(
    prefix="/api/teams",
    tags=["Teams"],
)


def _invite_to_response(invite) -> TeamInviteResponse:
    return TeamInviteResponse(
        id=invite.id,
        team_id=invite.team_id,
        invited_user_id=invite.invited_user_id,
        invited_by=invite.invited_by,
        status=invite.status.value if hasattr(invite.status, "value") else str(invite.status),
        created_at=invite.created_at,
    )


def _member_to_response(member) -> TeamMemberResponse:
    return TeamMemberResponse(
        id=member.id,
        team_id=member.team_id,
        user_id=member.user_id,
        role=member.role.value if hasattr(member.role, "value") else str(member.role),
        joined_at=member.joined_at,
    )


@router.post("", response_model=TeamResponse, status_code=status.HTTP_201_CREATED)
async def create_team(
    team_data: TeamCreate,
    current_user: CurrentUser = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    try:
        service = TeamService(db)
        return service.create_team(current_user_id=current_user.id, name=team_data.name)
    except ValidationError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=e.message)
    except Exception:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Failed to create team")


@router.get("", response_model=list[TeamResponse], status_code=status.HTTP_200_OK)
async def list_user_teams(
    current_user: CurrentUser = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    try:
        service = TeamService(db)
        return service.list_user_teams(current_user_id=current_user.id)
    except Exception:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Failed to list teams")


@router.post("/{team_id}/invite", response_model=TeamInviteResponse, status_code=status.HTTP_201_CREATED)
async def invite_member(
    team_id: int,
    invite_data: TeamInviteCreate,
    current_user: CurrentUser = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    try:
        service = TeamService(db)
        invite = service.invite_member(
            team_id=team_id,
            current_user_id=current_user.id,
            invited_user_id=invite_data.invited_user_id,
        )
        return _invite_to_response(invite)
    except ValidationError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=e.message)
    except ForbiddenError as e:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=e.message)
    except NotFoundError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=e.message)
    except Exception:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Failed to invite member")


@router.get("/invites", response_model=list[TeamInviteResponse], status_code=status.HTTP_200_OK)
async def list_pending_invites(
    current_user: CurrentUser = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    try:
        service = TeamService(db)
        invites = service.list_pending_invites(current_user_id=current_user.id)
        return [_invite_to_response(invite) for invite in invites]
    except Exception:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Failed to list invites")


@router.post("/invites/{invite_id}/accept", response_model=TeamMemberResponse, status_code=status.HTTP_200_OK)
async def accept_invite(
    invite_id: int,
    current_user: CurrentUser = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    try:
        service = TeamService(db)
        member = service.accept_invite(invite_id=invite_id, current_user_id=current_user.id)
        return _member_to_response(member)
    except ValidationError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=e.message)
    except ForbiddenError as e:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=e.message)
    except NotFoundError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=e.message)
    except Exception:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Failed to accept invite")


@router.post("/invites/{invite_id}/decline", response_model=TeamInviteResponse, status_code=status.HTTP_200_OK)
async def decline_invite(
    invite_id: int,
    current_user: CurrentUser = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    try:
        service = TeamService(db)
        invite = service.decline_invite(invite_id=invite_id, current_user_id=current_user.id)
        return _invite_to_response(invite)
    except ValidationError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=e.message)
    except ForbiddenError as e:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=e.message)
    except NotFoundError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=e.message)
    except Exception:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Failed to decline invite")


@router.get("/{team_id}/members", response_model=list[TeamMemberResponse], status_code=status.HTTP_200_OK)
async def list_members(
    team_id: int,
    current_user: CurrentUser = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    try:
        service = TeamService(db)
        members = service.list_members(team_id=team_id, current_user_id=current_user.id)
        return [_member_to_response(member) for member in members]
    except ForbiddenError as e:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=e.message)
    except NotFoundError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=e.message)
    except Exception:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Failed to list members")
