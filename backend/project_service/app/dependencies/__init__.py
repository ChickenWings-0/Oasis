"""
Dependencies package - Shared dependencies for routes
"""

from .auth_dependency import get_current_user, CurrentUser

__all__ = [
    "get_current_user",
    "CurrentUser",
]
