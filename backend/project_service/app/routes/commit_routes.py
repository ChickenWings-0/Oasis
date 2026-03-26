"""
Commit Routes - Endpoints for managing commits

REST API for CRUD operations on commits.
All routes require authentication via JWT or X-User-ID header.
"""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from ..database import get_db
from ..dependencies.auth_dependency import get_current_user, CurrentUser
from ..services import CommitService
from ..schemas import CommitResponse
from ..exceptions import ForbiddenError, NotFoundError, ValidationError
from typing import List


router = APIRouter(
    prefix="/api/v1/commits",
    tags=["Commits"]
)


@router.post(
    "",
    response_model=CommitResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Create a new commit"
)
async def create_commit(
    request_body: dict,  # {"message": str, "branch_id": int}
    current_user: CurrentUser = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Create a new commit on a branch.
    
    Request body:
    {
      "message": "fix login bug",
      "branch_id": 5
    }
    
    - Message is required and non-empty
    - Verifies branch exists
    - Auto-generates SHA-like commit ID
    - Sets parent to current branch HEAD
    - Updates branch HEAD to new commit
    
    Returns: CommitResponse with created commit
    """
    try:
        service = CommitService(db)
        
        commit = service.create_commit(
            user_id=current_user.user_id,
            branch_id=request_body["branch_id"],
            message=request_body["message"],
            author_id=current_user.user_id
        )
        
        return commit
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
            detail=f"Failed to create commit: {str(e)}"
        )


@router.get(
    "/{commit_id}",
    response_model=CommitResponse,
    status_code=status.HTTP_200_OK,
    summary="Get a single commit by ID"
)
async def get_commit(
    commit_id: str,
    db: Session = Depends(get_db)
):
    """
    Get a single commit by ID.
    
    Returns: CommitResponse
    """
    try:
        service = CommitService(db)
        commit = service.get_commit(commit_id)
        return commit
    except NotFoundError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=e.message
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to fetch commit: {str(e)}"
        )


@router.get(
    "/branch/{branch_id}/history",
    response_model=List[CommitResponse],
    status_code=status.HTTP_200_OK,
    summary="Get commit history for a branch"
)
async def get_branch_history(
    branch_id: int,
    db: Session = Depends(get_db),
    skip: int = 0,
    limit: int = 100
):
    """
    Get commit history (oldest to newest) for a branch.
    
    Query Parameters:
    - skip: Number of commits to skip (pagination)
    - limit: Max commits to return (pagination)
    
    Returns: List of CommitResponse (newest first)
    """
    try:
        service = CommitService(db)
        commits = service.get_branch_history(branch_id, skip=skip, limit=limit)
        return commits
    except NotFoundError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=e.message
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to fetch commit history: {str(e)}"
        )
