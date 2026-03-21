"""
Auth Dependency - For injecting current user into routes

For now, uses a simple mock implementation.
In production, this would validate JWT tokens and extract user_id.
"""

from fastapi import Depends, HTTPException, Header
from typing import Optional


async def get_current_user(
    x_user_id: Optional[int] = Header(None)
) -> int:
    """
    Get current user ID from request header.
    
    In production: validate JWT token and extract user_id
    For now: accept x_user_id header (testing/dev)
    
    Args:
        x_user_id: User ID from X-User-ID header
        
    Returns:
        User ID
        
    Raises:
        HTTPException: If user not authenticated
    """
    if x_user_id is None:
        raise HTTPException(
            status_code=401,
            detail="Not authenticated. Please provide X-User-ID header."
        )
    return x_user_id
