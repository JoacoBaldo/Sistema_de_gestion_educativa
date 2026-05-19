class AppError(Exception):
    """Base exception class for the application"""
    pass

class UnauthorizedError(AppError):
    """Raised when a user is not authorized or a token is invalid/expired/overwritten"""
    pass

class InvalidCredentialsError(AppError):
    """Raised when authentication credentials (username/email/password) are incorrect"""
    pass
