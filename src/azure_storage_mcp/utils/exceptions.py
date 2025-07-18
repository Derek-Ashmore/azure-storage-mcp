"""Custom exceptions for Azure Storage MCP server."""

from typing import Optional


class AzureStorageMCPError(Exception):
    """Base exception for Azure Storage MCP server."""
    
    def __init__(self, message: str, error_code: str = "UNKNOWN_ERROR") -> None:
        super().__init__(message)
        self.message = message
        self.error_code = error_code


class AuthenticationError(AzureStorageMCPError):
    """Authentication-related errors."""
    
    def __init__(self, message: str, auth_method: str) -> None:
        super().__init__(message, "AUTH_ERROR")
        self.auth_method = auth_method


class PermissionError(AzureStorageMCPError):
    """Permission-related errors."""
    
    def __init__(self, message: str, required_permission: str) -> None:
        super().__init__(message, "PERMISSION_ERROR")
        self.required_permission = required_permission


class ValidationError(AzureStorageMCPError):
    """Input validation errors."""
    
    def __init__(self, message: str, field_name: str) -> None:
        super().__init__(message, "VALIDATION_ERROR")
        self.field_name = field_name


class AzureAPIError(AzureStorageMCPError):
    """Azure API related errors."""
    
    def __init__(self, message: str, status_code: Optional[int] = None) -> None:
        super().__init__(message, "AZURE_API_ERROR")
        self.status_code = status_code