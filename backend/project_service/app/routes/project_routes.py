"""
Project Routes - Endpoints for managing projects

REST API for CRUD operations on projects.
All routes require authentication via JWT or X-User-ID header.
"""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from ..database import get_db
from ..dependencies.auth_dependency import get_current_user, CurrentUser
from ..services import ProjectService
from ..schemas import ProjectCreate, ProjectResponse
from ..exceptions import ForbiddenError, NotFoundError, ValidationError
from typing import List


router = APIRouter(
    prefix="/api/v1/projects",
    tags=["Projects"]
)


@router.post(
    "",
    response_model=ProjectResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Create a new project"
)
async def create_project(
    project_data: ProjectCreate,
    current_user: CurrentUser = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Create a new project.
    
    - Validates project name
    - Auto-creates 'main' branch
    - Sets owner to current authenticated user
    
    Returns: ProjectResponse with created project
    """
    try:
        # Remove owner_id from incoming data, set to current user
        project_data.owner_id = current_user.user_id
        
        service = ProjectService(db)
        project = service.create_project(current_user.user_id, project_data)
        
        return project
    except ValidationError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=e.message
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to create project: {str(e)}"
        )


@router.get(
    "",
    response_model=List[ProjectResponse],
    status_code=status.HTTP_200_OK,
    summary="Get all projects for current user"
)
async def get_user_projects(
    current_user: CurrentUser = Depends(get_current_user),
    db: Session = Depends(get_db),
    skip: int = 0,
    limit: int = 100
):
    """
    Get all projects owned by the current user.
    
    Query Parameters:
    - skip: Number of projects to skip (pagination)
    - limit: Max projects to return (pagination)
    
    Returns: List of ProjectResponse
    """
    try:
        service = ProjectService(db)
        projects = service.list_user_projects(current_user.user_id, skip=skip, limit=limit)
        return projects
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to fetch projects: {str(e)}"
        )


@router.get(
    "/{project_id}",
    response_model=ProjectResponse,
    status_code=status.HTTP_200_OK,
    summary="Get a single project by ID"
)
async def get_project(
    project_id: int,
    current_user: CurrentUser = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Get a single project by ID.
    
    - Verifies project exists
    - Verifies current user is the owner
    
    Returns: ProjectResponse
    """
    try:
        service = ProjectService(db)
        project = service.get_project(current_user.user_id, project_id)
        return project
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
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to fetch project: {str(e)}"
        )


@router.delete(
    "/{project_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Delete a project"
)
async def delete_project(
    project_id: int,
    current_user: CurrentUser = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Delete a project by ID.
    
    - Verifies project exists
    - Verifies current user is the owner
    - Cascades delete to all branches, commits, merges
    
    Returns: 204 No Content on success
    """
    try:
        service = ProjectService(db)
        success = service.delete_project(current_user.user_id, project_id)
        
        if not success:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to delete project"
            )
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
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to delete project: {str(e)}"
        )
