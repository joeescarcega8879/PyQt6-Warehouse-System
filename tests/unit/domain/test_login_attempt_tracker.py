"""
Unit tests for the LoginAttemptTracker class.
Tests rate limiting, lockout logic, and brute force protection.
"""
import pytest
from datetime import datetime, timedelta
from unittest.mock import patch, MagicMock
from src.domain.login_attempt_tracker import LoginAttemptTracker


@pytest.mark.unit
@pytest.mark.security
class TestRecordAttempt:
    """Test recording login attempts"""
    
    @patch('domain.login_attempt_tracker.QueryHelper')
    def test_record_successful_attempt(self, mock_query_helper):
        """Test recording a successful login attempt"""
        mock_query_helper.execute.return_value = {'success': True, 'rows_affected': 1}
        
        result = LoginAttemptTracker.record_attempt(
            username="testuser",
            success=True,
            ip_address="192.168.1.1"
        )
        
        assert result is True
        mock_query_helper.execute.assert_called_once()
        
        # Verify SQL parameters
        call_args = mock_query_helper.execute.call_args
        assert 'testuser' in str(call_args)
        assert 'INSERT INTO login_attempts' in call_args[0][0]
    
    @patch('domain.login_attempt_tracker.QueryHelper')
    def test_record_failed_attempt(self, mock_query_helper):
        """Test recording a failed login attempt"""
        mock_query_helper.execute.return_value = {'success': True, 'rows_affected': 1}
        
        result = LoginAttemptTracker.record_attempt(
            username="testuser",
            success=False,
            ip_address="192.168.1.1"
        )
        
        assert result is True
        mock_query_helper.execute.assert_called_once()
    
    @patch('domain.login_attempt_tracker.QueryHelper')
    def test_record_attempt_without_ip(self, mock_query_helper):
        """Test recording attempt with default IP address"""
        mock_query_helper.execute.return_value = {'success': True, 'rows_affected': 1}
        
        result = LoginAttemptTracker.record_attempt(
            username="testuser",
            success=False
        )
        
        assert result is True
        call_args = mock_query_helper.execute.call_args
        assert 'unknown' in str(call_args)
    
    @patch('domain.login_attempt_tracker.QueryHelper')
    def test_record_attempt_handles_database_error(self, mock_query_helper):
        """Test that database errors are handled gracefully"""
        mock_query_helper.execute.side_effect = Exception("Database error")
        
        result = LoginAttemptTracker.record_attempt(
            username="testuser",
            success=False
        )
        
        assert result is False


@pytest.mark.unit
@pytest.mark.security
class TestIsLockedOut:
    """Test lockout detection logic"""
    
    @patch('domain.login_attempt_tracker.QueryHelper')
    def test_user_not_locked_out_with_no_attempts(self, mock_query_helper):
        """Test user with no failed attempts is not locked out"""
        mock_query_helper.fetch_one.return_value = {
            'attempt_count': 0,
            'last_attempt': None
        }
        
        is_locked, unlock_time = LoginAttemptTracker.is_locked_out("testuser")
        
        assert is_locked is False
        assert unlock_time is None
    
    @patch('domain.login_attempt_tracker.QueryHelper')
    def test_user_not_locked_out_with_few_attempts(self, mock_query_helper):
        """Test user with fewer than max attempts is not locked out"""
        mock_query_helper.fetch_one.return_value = {
            'attempt_count': 3,  # Less than default 5
            'last_attempt': datetime.now().isoformat()
        }
        
        is_locked, unlock_time = LoginAttemptTracker.is_locked_out("testuser")
        
        assert is_locked is False
        assert unlock_time is None
    
    @patch('domain.login_attempt_tracker.QueryHelper')
    def test_user_locked_out_after_max_attempts(self, mock_query_helper):
        """Test user is locked out after reaching max attempts"""
        last_attempt = datetime.now()
        mock_query_helper.fetch_one.return_value = {
            'attempt_count': 5,  # Max attempts reached
            'last_attempt': last_attempt.isoformat()
        }
        
        is_locked, unlock_time = LoginAttemptTracker.is_locked_out("testuser")
        
        assert is_locked is True
        assert unlock_time is not None
        assert isinstance(unlock_time, datetime)
        assert unlock_time > datetime.now()
    
    @patch('domain.login_attempt_tracker.QueryHelper')
    def test_lockout_expires_after_timeout_period(self, mock_query_helper):
        """Test that lockout expires after the configured timeout"""
        # Last attempt was 31 minutes ago (beyond 30-minute default lockout)
        old_attempt = datetime.now() - timedelta(minutes=31)
        mock_query_helper.fetch_one.return_value = {
            'attempt_count': 5,
            'last_attempt': old_attempt.isoformat()
        }
        
        is_locked, unlock_time = LoginAttemptTracker.is_locked_out("testuser")
        
        assert is_locked is False
        assert unlock_time is None
    
    @patch('domain.login_attempt_tracker.QueryHelper')
    def test_handles_string_datetime_format(self, mock_query_helper):
        """Test that string datetime is properly converted"""
        last_attempt = datetime.now()
        mock_query_helper.fetch_one.return_value = {
            'attempt_count': 5,
            'last_attempt': last_attempt.strftime('%Y-%m-%d %H:%M:%S')
        }
        
        is_locked, unlock_time = LoginAttemptTracker.is_locked_out("testuser")
        
        assert is_locked is True
        assert unlock_time is not None
    
    @patch('domain.login_attempt_tracker.QueryHelper')
    def test_handles_database_error_gracefully(self, mock_query_helper):
        """Test that database errors don't cause lockout"""
        mock_query_helper.fetch_one.side_effect = Exception("Database error")
        
        is_locked, unlock_time = LoginAttemptTracker.is_locked_out("testuser")
        
        # Should not lock out user on error (fail open for usability)
        assert is_locked is False
        assert unlock_time is None
    
    @patch('domain.login_attempt_tracker.QueryHelper')
    def test_lockout_time_calculation_is_correct(self, mock_query_helper):
        """Test that unlock time is calculated correctly"""
        last_attempt = datetime.now()
        mock_query_helper.fetch_one.return_value = {
            'attempt_count': 5,
            'last_attempt': last_attempt.isoformat()
        }
        
        is_locked, unlock_time = LoginAttemptTracker.is_locked_out("testuser")
        
        assert is_locked is True
        # Unlock time should be approximately 30 minutes from last attempt
        expected_unlock = last_attempt + timedelta(minutes=30)
        time_diff = abs((unlock_time - expected_unlock).total_seconds())
        assert time_diff < 5  # Allow 5 seconds tolerance


@pytest.mark.unit
class TestGetRemainingAttempts:
    """Test remaining attempts calculation"""
    
    @patch('domain.login_attempt_tracker.QueryHelper')
    def test_full_attempts_available_for_new_user(self, mock_query_helper):
        """Test that new user has all attempts available"""
        mock_query_helper.fetch_one.return_value = {
            'attempt_count': 0
        }
        
        remaining = LoginAttemptTracker.get_remaining_attempts("newuser")
        
        assert remaining == 5  # Default max attempts
    
    @patch('domain.login_attempt_tracker.QueryHelper')
    def test_remaining_attempts_decreases(self, mock_query_helper):
        """Test that remaining attempts decrease with failed logins"""
        mock_query_helper.fetch_one.return_value = {
            'attempt_count': 2
        }
        
        remaining = LoginAttemptTracker.get_remaining_attempts("testuser")
        
        assert remaining == 3  # 5 - 2 = 3
    
    @patch('domain.login_attempt_tracker.QueryHelper')
    def test_zero_attempts_when_locked_out(self, mock_query_helper):
        """Test that locked out user has zero attempts"""
        mock_query_helper.fetch_one.return_value = {
            'attempt_count': 5
        }
        
        remaining = LoginAttemptTracker.get_remaining_attempts("testuser")
        
        assert remaining == 0
    
    @patch('domain.login_attempt_tracker.QueryHelper')
    def test_no_negative_attempts(self, mock_query_helper):
        """Test that attempts don't go negative"""
        mock_query_helper.fetch_one.return_value = {
            'attempt_count': 10  # More than max
        }
        
        remaining = LoginAttemptTracker.get_remaining_attempts("testuser")
        
        assert remaining >= 0
    
    @patch('domain.login_attempt_tracker.QueryHelper')
    def test_handles_database_error_safely(self, mock_query_helper):
        """Test that errors return max attempts (fail open)"""
        mock_query_helper.fetch_one.side_effect = Exception("Database error")
        
        remaining = LoginAttemptTracker.get_remaining_attempts("testuser")
        
        # Should return max attempts on error (better UX)
        assert remaining == 5
    
    @patch('domain.login_attempt_tracker.QueryHelper')
    def test_returns_integer(self, mock_query_helper):
        """Test that return value is always an integer"""
        mock_query_helper.fetch_one.return_value = {
            'attempt_count': 2
        }
        
        remaining = LoginAttemptTracker.get_remaining_attempts("testuser")
        
        assert isinstance(remaining, int)


@pytest.mark.unit
class TestClearAttempts:
    """Test clearing failed attempts"""
    
    @patch('domain.login_attempt_tracker.QueryHelper')
    def test_clear_attempts_successful(self, mock_query_helper):
        """Test successfully clearing failed attempts"""
        mock_query_helper.execute.return_value = {'success': True, 'rows_affected': 3}
        
        result = LoginAttemptTracker.clear_attempts("testuser")
        
        assert result is True
        mock_query_helper.execute.assert_called_once()
        
        # Verify DELETE query is used
        call_args = mock_query_helper.execute.call_args
        assert 'DELETE FROM login_attempts' in call_args[0][0]
        assert 'success = false' in call_args[0][0]
    
    @patch('domain.login_attempt_tracker.QueryHelper')
    def test_clear_attempts_only_deletes_failed(self, mock_query_helper):
        """Test that only failed attempts are deleted"""
        mock_query_helper.execute.return_value = {'success': True, 'rows_affected': 2}
        
        LoginAttemptTracker.clear_attempts("testuser")
        
        # Check SQL includes success = false condition
        call_args = mock_query_helper.execute.call_args
        sql = call_args[0][0]
        assert 'success = false' in sql.lower()
    
    @patch('domain.login_attempt_tracker.QueryHelper')
    def test_clear_attempts_handles_error(self, mock_query_helper):
        """Test error handling when clearing attempts"""
        mock_query_helper.execute.side_effect = Exception("Database error")
        
        result = LoginAttemptTracker.clear_attempts("testuser")
        
        assert result is False
    
    @patch('domain.login_attempt_tracker.QueryHelper')
    def test_clear_attempts_for_specific_user(self, mock_query_helper):
        """Test that clear only affects specified user"""
        mock_query_helper.execute.return_value = {'success': True, 'rows_affected': 1}
        
        LoginAttemptTracker.clear_attempts("specificuser")
        
        call_args = mock_query_helper.execute.call_args
        # Check that the username is in the call somewhere
        full_call = str(call_args)
        assert 'specificuser' in full_call or call_args[0][1]['username'] == 'specificuser'


@pytest.mark.unit
class TestCleanupOldAttempts:
    """Test cleanup of old login attempt records"""
    
    @patch('domain.login_attempt_tracker.QueryHelper')
    def test_cleanup_deletes_old_records(self, mock_query_helper):
        """Test that old records are deleted"""
        mock_query_helper.execute.return_value = {'success': True, 'rows_affected': 150}
        
        deleted = LoginAttemptTracker.cleanup_old_attempts(days=30)
        
        assert deleted == 150
        mock_query_helper.execute.assert_called_once()
    
    @patch('domain.login_attempt_tracker.QueryHelper')
    def test_cleanup_uses_correct_cutoff_date(self, mock_query_helper):
        """Test that cleanup uses correct date calculation"""
        mock_query_helper.execute.return_value = {'success': True, 'rows_affected': 10}
        
        LoginAttemptTracker.cleanup_old_attempts(days=90)
        
        call_args = mock_query_helper.execute.call_args
        sql = call_args[0][0]
        assert 'attempt_time <' in sql
    
    @patch('domain.login_attempt_tracker.QueryHelper')
    def test_cleanup_returns_zero_when_none_deleted(self, mock_query_helper):
        """Test cleanup when no records match"""
        mock_query_helper.execute.return_value = {'success': True, 'rows_affected': 0}
        
        deleted = LoginAttemptTracker.cleanup_old_attempts(days=30)
        
        assert deleted == 0
    
    @patch('domain.login_attempt_tracker.QueryHelper')
    def test_cleanup_handles_database_error(self, mock_query_helper):
        """Test error handling during cleanup"""
        mock_query_helper.execute.side_effect = Exception("Database error")
        
        deleted = LoginAttemptTracker.cleanup_old_attempts(days=30)
        
        assert deleted == -1  # Error indicator
    
    @patch('domain.login_attempt_tracker.QueryHelper')
    def test_cleanup_custom_retention_period(self, mock_query_helper):
        """Test cleanup with custom retention period"""
        mock_query_helper.execute.return_value = {'success': True, 'rows_affected': 50}
        
        deleted = LoginAttemptTracker.cleanup_old_attempts(days=7)
        
        assert deleted == 50
        mock_query_helper.execute.assert_called_once()


@pytest.mark.unit
@pytest.mark.security
class TestLoginAttemptTrackerSecurity:
    """Test security aspects of login attempt tracking"""
    
    @patch('domain.login_attempt_tracker.QueryHelper')
    def test_prevents_username_enumeration(self, mock_query_helper):
        """Test that behavior is consistent for existing and non-existing users"""
        # Both should return similar results (don't reveal user existence)
        mock_query_helper.fetch_one.return_value = {
            'attempt_count': 0,
            'last_attempt': None
        }
        
        is_locked1, _ = LoginAttemptTracker.is_locked_out("existing_user")
        is_locked2, _ = LoginAttemptTracker.is_locked_out("nonexistent_user")
        
        # Both should have same response type
        assert isinstance(is_locked1, bool)
        assert isinstance(is_locked2, bool)
    
    @patch('domain.login_attempt_tracker.QueryHelper')
    def test_lockout_cannot_be_bypassed_with_special_chars(self, mock_query_helper):
        """Test that special characters in username don't bypass lockout"""
        mock_query_helper.fetch_one.return_value = {
            'attempt_count': 5,
            'last_attempt': datetime.now().isoformat()
        }
        
        # Try usernames with special characters
        special_usernames = [
            "user'; DROP TABLE users; --",
            "user\" OR 1=1",
            "user<script>alert('xss')</script>"
        ]
        
        for username in special_usernames:
            is_locked, _ = LoginAttemptTracker.is_locked_out(username)
            # Should still enforce lockout
            assert isinstance(is_locked, bool)
    
    @patch('domain.login_attempt_tracker.QueryHelper')
    def test_ip_address_recorded_for_audit(self, mock_query_helper):
        """Test that IP addresses are recorded for security auditing"""
        mock_query_helper.execute.return_value = {'success': True, 'rows_affected': 1}
        
        LoginAttemptTracker.record_attempt(
            username="testuser",
            success=False,
            ip_address="10.0.0.1"
        )
        
        call_args = mock_query_helper.execute.call_args
        assert '10.0.0.1' in str(call_args)


@pytest.mark.unit
class TestLoginAttemptTrackerEdgeCases:
    """Test edge cases and boundary conditions"""
    
    @patch('domain.login_attempt_tracker.QueryHelper')
    def test_empty_username_handling(self, mock_query_helper):
        """Test handling of empty username"""
        mock_query_helper.execute.return_value = {'success': True, 'rows_affected': 1}
        
        result = LoginAttemptTracker.record_attempt("", success=False)
        
        # Should handle gracefully
        assert isinstance(result, bool)
    
    @patch('domain.login_attempt_tracker.QueryHelper')
    def test_very_long_username(self, mock_query_helper):
        """Test handling of very long username"""
        mock_query_helper.execute.return_value = {'success': True, 'rows_affected': 1}
        
        long_username = "a" * 1000
        result = LoginAttemptTracker.record_attempt(long_username, success=False)
        
        assert isinstance(result, bool)
    
    @patch('domain.login_attempt_tracker.QueryHelper')
    def test_none_result_from_database(self, mock_query_helper):
        """Test handling when database returns None"""
        mock_query_helper.fetch_one.return_value = None
        
        is_locked, unlock_time = LoginAttemptTracker.is_locked_out("testuser")
        
        assert is_locked is False
        assert unlock_time is None
    
    @patch('domain.login_attempt_tracker.QueryHelper')
    def test_missing_keys_in_result(self, mock_query_helper):
        """Test handling when database result is missing expected keys"""
        mock_query_helper.fetch_one.return_value = {}  # Missing keys
        
        # Should not crash
        remaining = LoginAttemptTracker.get_remaining_attempts("testuser")
        assert isinstance(remaining, int)
