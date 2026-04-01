"""
Secure error message handling.
Provides generic user-facing messages while logging detailed errors securely.
"""
import logging
from typing import Optional

logger = logging.getLogger(__name__)


class ErrorMessages:
    """
    Centralized error message management.
    Ensures sensitive information is not exposed to users while maintaining detailed logs.
    """
    
    # Generic error messages for users
    GENERIC_ERROR = "An error occurred. Please contact your system administrator."
    VALIDATION_ERROR = "The data entered is not valid. Please check your input."
    PERMISSION_DENIED = "You do not have permission to perform this action."
    DATABASE_ERROR = "A database error occurred. Please try again later."
    AUTHENTICATION_ERROR = "Authentication failed. Please check your credentials."
    SESSION_EXPIRED = "Your session has expired. Please log in again."
    NETWORK_ERROR = "A network error occurred. Please check your connection."
    NOT_FOUND = "The requested resource was not found."
    DUPLICATE_ERROR = "This record already exists in the system."
    
    # Login-specific messages
    LOGIN_FAILED = "Invalid username or password."
    ACCOUNT_LOCKED = "Account temporarily locked due to multiple failed attempts."
    ACCOUNT_DISABLED = "This account has been disabled. Please contact an administrator."
    
    # Password-related messages
    PASSWORD_MISMATCH = "Passwords do not match."
    PASSWORD_WEAK = "Password does not meet security requirements."
    PASSWORD_CHANGE_SUCCESS = "Password changed successfully."
    PASSWORD_CHANGE_FAILED = "Failed to change password. Please try again."
    
    # Operation result messages
    SAVE_SUCCESS = "Record saved successfully."
    SAVE_FAILED = "Failed to save record. Please try again."
    DELETE_SUCCESS = "Record deleted successfully."
    DELETE_FAILED = "Failed to delete record. Please try again."
    UPDATE_SUCCESS = "Record updated successfully."
    UPDATE_FAILED = "Failed to update record. Please try again."
    
    @staticmethod
    def log_and_mask_error(
        error: Exception, 
        context: str, 
        user_message: Optional[str] = None
    ) -> str:
        """
        Log detailed error information and return a safe user-facing message.
        
        This method ensures that:
        1. Detailed error information is logged for debugging
        2. Sensitive information (DB schema, internal paths, etc.) is not exposed to users
        3. A consistent, generic error message is shown to users
        
        Args:
            error: The exception that occurred
            context: Description of what operation was being performed
            user_message: Optional custom message for the user (defaults to GENERIC_ERROR)
            
        Returns:
            str: Safe user-facing error message
        """
        # Log the full error with context for debugging
        logger.error(f"{context}: {str(error)}", exc_info=True)
        
        # Return generic message to user
        return user_message if user_message else ErrorMessages.GENERIC_ERROR
    
    @staticmethod
    def log_database_error(
        error: Exception, 
        operation: str, 
        table: Optional[str] = None
    ) -> str:
        """
        Specialized method for logging database errors.
        
        Args:
            error: The database exception
            operation: The operation being performed (SELECT, INSERT, UPDATE, DELETE)
            table: Optional table name involved
            
        Returns:
            str: Generic database error message for user
        """
        context = f"Database {operation}"
        if table:
            context += f" on table {table}"
        
        logger.error(f"{context}: {str(error)}", exc_info=True)
        
        return ErrorMessages.DATABASE_ERROR
    
    @staticmethod
    def log_security_event(
        event: str, 
        username: Optional[str] = None, 
        ip_address: Optional[str] = None,
        details: Optional[str] = None
    ) -> None:
        """
        Log security-related events (login failures, permission denials, etc.).
        These are logged at WARNING level for security monitoring.
        
        Args:
            event: Description of the security event
            username: Username involved (if applicable)
            ip_address: IP address of the request (if applicable)
            details: Additional details about the event
        """
        log_message = f"SECURITY EVENT: {event}"
        
        if username:
            log_message += f" | User: {username}"
        if ip_address:
            log_message += f" | IP: {ip_address}"
        if details:
            log_message += f" | Details: {details}"
        
        logger.warning(log_message)
    
    @staticmethod
    def get_validation_error(field_name: str, requirement: str) -> str:
        """
        Generate a user-friendly validation error message.
        
        Args:
            field_name: Name of the field that failed validation
            requirement: Description of what the field requires
            
        Returns:
            str: Formatted validation error message
        """
        return f"{field_name}: {requirement}"
    
    @staticmethod
    def get_permission_error(action: str) -> str:
        """
        Generate a permission denied message for a specific action.
        
        Args:
            action: The action that was attempted
            
        Returns:
            str: Permission denied message
        """
        return f"You do not have permission to {action}."
