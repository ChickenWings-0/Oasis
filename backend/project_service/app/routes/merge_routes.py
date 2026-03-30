"""
Merge Routes - Endpoints for managing merges

REST API for CRUD operations on merges.
All routes require authentication via JWT.
"""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from ..database import get_db
from ..dependencies.auth_dependency import get_current_user, CurrentUser
from ..services import MergeService
from ..schemas import MergeResponse
from ..exceptions import ForbiddenError, NotFoundError, ValidationError
from typing import List


router = APIRouter(
    prefix="/api/v1/merges",
    tags=["Merges"]
)


@router.post(
    "",
    response_model=MergeResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Merge two branches"
)
async def merge_branches(
    request_body: dict,  # {"source_branch_id": int, "target_branch_id": int}
    current_user: CurrentUser = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Merge source branch into target branch.

    Returns: MergeResponse with merge details
    """
    try:
        service = MergeService(db)
        
        merge = service.merge_branches(
            user_id=current_user.id,
            source_branch_id=request_body["source_branch_id"],
            target_branch_id=request_body["target_branch_id"]
        )
        
        return merge
    except ValidationError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=e.message
        )
    except ForbiddenError as e:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=e.message
        )
    except NotFoundError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=e.message
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to merge branches: {str(e)}"
        )


@router.get(
    "/{merge_id}",
    response_model=MergeResponse,
    status_code=status.HTTP_200_OK,
    summary="Get a single merge by ID"
)
async def get_merge(
    merge_id: int,
    db: Session = Depends(get_db)
):
    """
    Get a single merge by ID.
    
    Returns: MergeResponse
    """
    try:
        service = MergeService(db)
        merge = service.get_merge(merge_id)
        return merge
    except NotFoundError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=e.message
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to fetch merge: {str(e)}"
        )


@router.get(
    "/project/{project_id}/history",
    response_model=List[MergeResponse],
    status_code=status.HTTP_200_OK,
    summary="Get merge history for a project"
)
async def get_merge_history(
    project_id: int,
    db: Session = Depends(get_db),
    skip: int = 0,
    limit: int = 100
):
    """
    Get merge history for a project.
    
    Returns: List of MergeResponse (newest first)
    """
    try:
        service = MergeService(db)
        merges = service.get_merge_history(project_id, skip=skip, limit=limit)
        return merges
    except NotFoundError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=e.message
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to fetch merge history: {str(e)}"
        )


@router.post(
    "/{merge_id}/approve",
    response_model=MergeResponse,
    status_code=status.HTTP_200_OK,
    summary="Approve a merge request"
)
async def approve_merge(
    merge_id: int,
    current_user: CurrentUser = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Approve a merge request (marks as approved).
    
    Returns: Updated MergeResponse
    """
    try:
        service = MergeService(db)
        merge = service.approve_merge(merge_id, current_user.id)
        return merge
    except NotFoundError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=e.message
        )
    except ForbiddenError as e:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=e.message
        )
    except ValidationError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=e.message
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to approve merge: {str(e)}"
        )
