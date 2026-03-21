"""
Merge Routes - Endpoints for managing merges

REST API for CRUD operations on merges.
All routes require authentication via X-User-ID header.
"""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from ..database import get_db
from ..dependencies.auth_dependency import get_current_user
from ..services import MergeService
from ..schemas import MergeResponse
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
    current_user: int = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Merge source branch into target branch.
    
    Request body:
    {
      "source_branch_id": 5,
      "target_branch_id": 3
    }
    
    - Verifies both branches exist and belong to same project
    - Verifies current user owns the project
    - Determines merge type (no-op, fast-forward, normal, conflict)
    - Creates merge commit automatically
    - Updates target branch HEAD
    - Records merge in history
    
    Returns: MergeResponse with merge details
    """
    try:
        service = MergeService(db)
        
        merge = service.merge_branches(
            user_id=current_user,
            source_id=request_body["source_branch_id"],
            target_id=request_body["target_branch_id"]
        )
        
        return merge
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except PermissionError as e:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=str(e)
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
        
        if not merge:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Merge {merge_id} not found"
            )
        
        return merge
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
    
    Query Parameters:
    - skip: Number of merges to skip (pagination)
    - limit: Max merges to return (pagination)
    
    Returns: List of MergeResponse (newest first)
    """
    try:
        service = MergeService(db)
        merges = service.get_merge_history(project_id, skip=skip, limit=limit)
        return merges
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to fetch merge history: {str(e)}"
        )
