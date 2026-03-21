"""
Branch Routes - Endpoints for managing branches

REST API for CRUD operations on branches.
All routes require authentication via X-User-ID header.
"""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from ..database import get_db
from ..dependencies.auth_dependency import get_current_user
from ..services import BranchService
from ..schemas import BranchCreate, BranchResponse
from typing import List


router = APIRouter(
    prefix="/api/v1/branches",
    tags=["Branches"]
)


@router.post(
    "",
    response_model=BranchResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Create a new branch"
)
async def create_branch(
    request_body: dict,  # {"name": str, "project_id": int, "base_branch_id": int}
    current_user: int = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Create a new branch from an existing branch.
    
    Request body:
    {
      "name": "feature/auth",
      "project_id": 1,
      "base_branch_id": 3
    }
    
    - Verifies project ownership
    - Verifies base branch exists
    - Checks branch name uniqueness in project
    - Inherits HEAD commit from base branch
    
    Returns: BranchResponse with created branch
    """
    try:
        service = BranchService(db)
        
        branch = service.create_branch(
            user_id=current_user,
            project_id=request_body["project_id"],
            base_branch_id=request_body["base_branch_id"],
            new_branch_name=request_body["name"]
        )
        
        return branch
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
            detail=f"Failed to create branch: {str(e)}"
        )


@router.get(
    "/{branch_id}",
    response_model=BranchResponse,
    status_code=status.HTTP_200_OK,
    summary="Get a single branch by ID"
)
async def get_branch(
    branch_id: int,
    db: Session = Depends(get_db)
):
    """
    Get a single branch by ID.
    
    Returns: BranchResponse
    """
    try:
        service = BranchService(db)
        branch = service.get_branch(branch_id)
        
        if not branch:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Branch {branch_id} not found"
            )
        
        return branch
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to fetch branch: {str(e)}"
        )


@router.get(
    "/project/{project_id}",
    response_model=List[BranchResponse],
    status_code=status.HTTP_200_OK,
    summary="Get all branches in a project"
)
async def list_branches(
    project_id: int,
    db: Session = Depends(get_db),
    skip: int = 0,
    limit: int = 100
):
    """
    Get all branches in a project.
    
    Query Parameters:
    - skip: Number of branches to skip (pagination)
    - limit: Max branches to return (pagination)
    
    Returns: List of BranchResponse
    """
    try:
        service = BranchService(db)
        branches = service.list_branches(project_id, skip=skip, limit=limit)
        return branches
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to fetch branches: {str(e)}"
        )
