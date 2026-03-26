"""
Custom Exception Classes for Auth & Business Logic
"""


class AuthError(Exception):
    """Base auth error"""
    def __init__(self, message: str, status_code: int = 401):
        self.message = message
        self.status_code = status_code
        super().__init__(self.message)


class UnauthorizedError(AuthError):
    """User not authenticated"""
    def __init__(self, message: str = "Not authenticated"):
        super().__init__(message, status_code=401)


class ForbiddenError(AuthError):
    """User not authorized to perform action"""
    def __init__(self, message: str = "Not authorized"):
        super().__init__(message, status_code=403)


class NotFoundError(Exception):
    """Resource not found"""
    def __init__(self, message: str = "Resource not found"):
        self.message = message
        self.status_code = 404
        super().__init__(self.message)


class ValidationError(Exception):
    """Validation error"""
    def __init__(self, message: str = "Validation failed"):
        self.message = message
        self.status_code = 400
        super().__init__(self.message)
