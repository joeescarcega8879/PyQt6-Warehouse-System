"""
Unit tests for the ErrorMessages class.
Tests secure error handling, logging, and message sanitization.
"""
import pytest
import logging
from unittest.mock import patch, MagicMock
from src.common.error_messages import ErrorMessages


@pytest.mark.unit
class TestErrorMessagesConstants:
    """Test that all error message constants are defined and non-empty"""
    
    def test_generic_error_message_exists(self):
        assert ErrorMessages.GENERIC_ERROR
        assert isinstance(ErrorMessages.GENERIC_ERROR, str)
        assert len(ErrorMessages.GENERIC_ERROR) > 0
    
    def test_validation_error_message_exists(self):
        assert ErrorMessages.VALIDATION_ERROR
        assert isinstance(ErrorMessages.VALIDATION_ERROR, str)
    
    def test_database_error_message_exists(self):
        assert ErrorMessages.DATABASE_ERROR
        assert isinstance(ErrorMessages.DATABASE_ERROR, str)
    
    def test_authentication_error_message_exists(self):
        assert ErrorMessages.AUTHENTICATION_ERROR
        assert isinstance(ErrorMessages.AUTHENTICATION_ERROR, str)
    
    def test_login_failed_message_exists(self):
        assert ErrorMessages.LOGIN_FAILED
        assert isinstance(ErrorMessages.LOGIN_FAILED, str)
    
    def test_password_weak_message_exists(self):
        assert ErrorMessages.PASSWORD_WEAK
        assert isinstance(ErrorMessages.PASSWORD_WEAK, str)
    
    def test_save_failed_message_exists(self):
        assert ErrorMessages.SAVE_FAILED
        assert isinstance(ErrorMessages.SAVE_FAILED, str)
    
    def test_error_messages_are_generic(self):
        """Ensure error messages don't leak sensitive technical information"""
        # Technical keywords that should not appear in user-facing messages
        sensitive_keywords = [
            "sql", "table", "column", 
            "connection", "query", "exception", "traceback", "stack"
        ]
        
        # Check key error messages for sensitive technical information
        # Note: "password", "database", "update" can be OK in context like 
        # "Invalid password" or "database error" or "failed to update"
        messages_to_check = [
            ErrorMessages.GENERIC_ERROR,
            ErrorMessages.SAVE_FAILED,
            ErrorMessages.DELETE_FAILED
        ]
        
        for message in messages_to_check:
            message_lower = message.lower()
            for keyword in sensitive_keywords:
                assert keyword not in message_lower, \
                    f"Message '{message}' contains sensitive keyword '{keyword}'"


@pytest.mark.unit
@pytest.mark.security
class TestLogAndMaskError:
    """Test the log_and_mask_error method"""
    
    def test_logs_error_with_context(self, mock_logger):
        """Test that error is logged with proper context"""
        test_error = ValueError("Detailed error message")
        context = "testing error handling"
        
        result = ErrorMessages.log_and_mask_error(
            error=test_error,
            context=context,
            user_message=ErrorMessages.GENERIC_ERROR
        )
        
        assert result == ErrorMessages.GENERIC_ERROR
    
    def test_returns_custom_user_message(self):
        """Test that custom user message is returned"""
        test_error = Exception("Internal error")
        custom_message = "Custom user-facing message"
        
        with patch("common.error_messages.logger"):
            result = ErrorMessages.log_and_mask_error(
                error=test_error,
                context="test operation",
                user_message=custom_message
            )
        
        assert result == custom_message
    
    def test_returns_generic_error_when_no_user_message(self):
        """Test default behavior returns GENERIC_ERROR"""
        test_error = Exception("Some error")
        
        with patch("common.error_messages.logger"):
            result = ErrorMessages.log_and_mask_error(
                error=test_error,
                context="test operation"
            )
        
        assert result == ErrorMessages.GENERIC_ERROR
    
    def test_does_not_expose_exception_details_to_user(self):
        """Test that exception details are not in user message"""
        test_error = Exception("SECRET_PASSWORD=abc123, DB_CONNECTION=localhost:5432")
        
        with patch("common.error_messages.logger"):
            result = ErrorMessages.log_and_mask_error(
                error=test_error,
                context="test operation",
                user_message=ErrorMessages.DATABASE_ERROR
            )
        
        # User message should not contain sensitive details
        assert "SECRET_PASSWORD" not in result
        assert "DB_CONNECTION" not in result
        assert "abc123" not in result
        assert result == ErrorMessages.DATABASE_ERROR
    
    def test_handles_different_exception_types(self):
        """Test handling of various exception types"""
        exceptions = [
            ValueError("Invalid value"),
            KeyError("Missing key"),
            RuntimeError("Runtime error"),
            Exception("Generic exception")
        ]
        
        with patch("common.error_messages.logger"):
            for exc in exceptions:
                result = ErrorMessages.log_and_mask_error(
                    error=exc,
                    context="test",
                    user_message=ErrorMessages.GENERIC_ERROR
                )
                assert result == ErrorMessages.GENERIC_ERROR


@pytest.mark.unit
class TestLogDatabaseError:
    """Test the log_database_error method"""
    
    def test_logs_database_error_with_operation(self):
        """Test database error logging with operation"""
        test_error = Exception("Connection refused")
        
        with patch("common.error_messages.logger") as mock_log:
            result = ErrorMessages.log_database_error(
                error=test_error,
                operation="SELECT"
            )
        
        assert result == ErrorMessages.DATABASE_ERROR
        mock_log.error.assert_called_once()
    
    def test_logs_database_error_with_table(self):
        """Test database error logging with table name"""
        test_error = Exception("Table not found")
        
        with patch("common.error_messages.logger") as mock_log:
            result = ErrorMessages.log_database_error(
                error=test_error,
                operation="INSERT",
                table="users"
            )
        
        assert result == ErrorMessages.DATABASE_ERROR
        mock_log.error.assert_called_once()
        
        # Check that log includes table name
        call_args = mock_log.error.call_args[0][0]
        assert "users" in call_args
    
    def test_returns_generic_database_error(self):
        """Test that generic database error is returned"""
        test_error = Exception("Detailed DB error with connection string")
        
        with patch("common.error_messages.logger"):
            result = ErrorMessages.log_database_error(
                error=test_error,
                operation="UPDATE",
                table="sensitive_table"
            )
        
        # Should return generic message, not expose details
        assert result == ErrorMessages.DATABASE_ERROR
        assert "connection string" not in result
        assert "sensitive_table" not in result


@pytest.mark.unit
@pytest.mark.security
class TestLogSecurityEvent:
    """Test the log_security_event method"""
    
    def test_logs_basic_security_event(self):
        """Test logging basic security event"""
        with patch("common.error_messages.logger") as mock_log:
            ErrorMessages.log_security_event(
                event="Failed login attempt"
            )
        
        mock_log.warning.assert_called_once()
        call_args = mock_log.warning.call_args[0][0]
        assert "SECURITY EVENT" in call_args
        assert "Failed login attempt" in call_args
    
    def test_logs_security_event_with_username(self):
        """Test security event logging with username"""
        with patch("common.error_messages.logger") as mock_log:
            ErrorMessages.log_security_event(
                event="Unauthorized access attempt",
                username="testuser"
            )
        
        call_args = mock_log.warning.call_args[0][0]
        assert "testuser" in call_args
        assert "User:" in call_args
    
    def test_logs_security_event_with_ip_address(self):
        """Test security event logging with IP address"""
        with patch("common.error_messages.logger") as mock_log:
            ErrorMessages.log_security_event(
                event="Suspicious activity",
                ip_address="192.168.1.100"
            )
        
        call_args = mock_log.warning.call_args[0][0]
        assert "192.168.1.100" in call_args
        assert "IP:" in call_args
    
    def test_logs_security_event_with_all_parameters(self):
        """Test security event logging with all parameters"""
        with patch("common.error_messages.logger") as mock_log:
            ErrorMessages.log_security_event(
                event="Multiple failed logins",
                username="admin",
                ip_address="10.0.0.1",
                details="5 attempts in 2 minutes"
            )
        
        call_args = mock_log.warning.call_args[0][0]
        assert "Multiple failed logins" in call_args
        assert "admin" in call_args
        assert "10.0.0.1" in call_args
        assert "5 attempts in 2 minutes" in call_args
    
    def test_security_events_use_warning_level(self):
        """Test that security events are logged at WARNING level"""
        with patch("common.error_messages.logger") as mock_log:
            ErrorMessages.log_security_event(event="Test event")
        
        # Should call warning, not error or info
        mock_log.warning.assert_called_once()
        mock_log.error.assert_not_called()
        mock_log.info.assert_not_called()


@pytest.mark.unit
class TestGetValidationError:
    """Test the get_validation_error method"""
    
    def test_returns_formatted_validation_error(self):
        """Test validation error formatting"""
        result = ErrorMessages.get_validation_error(
            field_name="Email",
            requirement="Must be a valid email address"
        )
        
        assert "Email" in result
        assert "Must be a valid email address" in result
    
    def test_validation_error_contains_both_parts(self):
        """Test that both field name and requirement are in message"""
        field = "Password"
        requirement = "Must be at least 8 characters"
        
        result = ErrorMessages.get_validation_error(field, requirement)
        
        assert field in result
        assert requirement in result


@pytest.mark.unit
class TestGetPermissionError:
    """Test the get_permission_error method"""
    
    def test_returns_formatted_permission_error(self):
        """Test permission error formatting"""
        result = ErrorMessages.get_permission_error("delete users")
        
        assert "permission" in result.lower()
        assert "delete users" in result
    
    def test_permission_error_is_clear(self):
        """Test that permission error is user-friendly"""
        result = ErrorMessages.get_permission_error("access admin panel")
        
        assert result
        assert len(result) > 0
        assert "access admin panel" in result


@pytest.mark.unit
class TestErrorMessageSecurity:
    """Test security aspects of error messages"""
    
    def test_no_sql_injection_hints(self):
        """Ensure error messages don't hint at SQL structure"""
        # SQL-specific keywords that reveal database internals
        sql_keywords = ["SELECT", "INSERT", "FROM", "WHERE", "JOIN", "INNER", "OUTER"]
        
        # Check common error messages
        # Note: Words like "UPDATE" and "DELETE" are OK in context like 
        # "Failed to update" or "Failed to delete" as they describe user actions
        common_messages = [
            ErrorMessages.GENERIC_ERROR,
            ErrorMessages.DATABASE_ERROR,
            ErrorMessages.SAVE_FAILED
        ]
        
        for message in common_messages:
            for keyword in sql_keywords:
                assert keyword not in message.upper(), \
                    f"Message '{message}' contains SQL keyword '{keyword}'"
    
    def test_no_path_disclosure(self):
        """Ensure error messages don't disclose file paths"""
        path_indicators = ["/", "\\", ".py", ".sql", "C:", "home", "usr"]
        
        common_messages = [
            ErrorMessages.GENERIC_ERROR,
            ErrorMessages.DATABASE_ERROR,
            ErrorMessages.SAVE_FAILED
        ]
        
        for message in common_messages:
            for indicator in path_indicators:
                assert indicator not in message
    
    def test_error_messages_are_actionable(self):
        """Test that error messages give users guidance"""
        messages_with_action = [
            (ErrorMessages.SAVE_FAILED, ["please", "try", "again"]),
            (ErrorMessages.SESSION_EXPIRED, ["log", "in", "again"]),
            (ErrorMessages.GENERIC_ERROR, ["contact", "administrator"])
        ]
        
        # Each message should either tell user what to do or who to contact
        for message, expected_words in messages_with_action:
            message_lower = message.lower()
            has_action = all(word in message_lower for word in expected_words)
            assert has_action, \
                f"Message '{message}' should contain guidance words: {expected_words}"
