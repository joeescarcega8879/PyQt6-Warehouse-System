"""
Login attempt tracking for rate limiting and brute force protection.
Tracks failed login attempts and enforces temporary lockouts.
"""
from datetime import datetime, timedelta
from typing import Optional, Tuple
from database.query_helper import QueryHelper
from config.settings import SecurityConfig
import logging

logger = logging.getLogger(__name__)


class LoginAttemptTracker:
    """
    Tracks login attempts to prevent brute force attacks.
    Enforces temporary account lockouts after repeated failed attempts.
    """
    
    @staticmethod
    def record_attempt(username: str, success: bool, ip_address: str = "unknown") -> bool:
        """
        Record a login attempt in the database.
        
        Args:
            username: Username that attempted to log in
            success: Whether the login was successful
            ip_address: IP address of the attempt (for audit purposes)
            
        Returns:
            bool: True if recorded successfully, False otherwise
        """
        try:
            sql = """
                INSERT INTO login_attempts (username, success, ip_address, attempt_time)
                VALUES (:username, :success, :ip_address, NOW())
            """
            
            params = {
                'username': username,
                'success': success,
                'ip_address': ip_address
            }
            
            result = QueryHelper.execute(sql, params)
            return result['success']
            
        except Exception as e:
            logger.error(f"Error recording login attempt: {str(e)}")
            return False
    
    @staticmethod
    def is_locked_out(username: str) -> Tuple[bool, Optional[datetime]]:
        """
        Check if a user is currently locked out due to failed attempts.
        
        Args:
            username: Username to check
            
        Returns:
            Tuple[bool, Optional[datetime]]: (is_locked, unlock_time)
                - is_locked: True if user is locked out
                - unlock_time: When the lockout will expire (None if not locked)
        """
        # Calculate time window for checking attempts
        lockout_window = datetime.now() - timedelta(minutes=SecurityConfig.LOGIN_LOCKOUT_MINUTES)
        
        try:
            # Count failed attempts in the lockout window
            sql = """
                SELECT COUNT(*) as attempt_count, MAX(attempt_time) as last_attempt
                FROM login_attempts
                WHERE username = :username
                  AND attempt_time > :lockout_window
                  AND success = false
            """
            
            params = {
                'username': username,
                'lockout_window': lockout_window.strftime('%Y-%m-%d %H:%M:%S')
            }
            
            result = QueryHelper.fetch_one(sql, params)
            
            if result:
                attempt_count = result.get('attempt_count', 0)
                last_attempt = result.get('last_attempt')
                
                if attempt_count >= SecurityConfig.MAX_LOGIN_ATTEMPTS:
                    # User is locked out
                    if last_attempt:
                        # Convert to datetime if it's a string
                        if isinstance(last_attempt, str):
                            last_attempt = datetime.fromisoformat(last_attempt)
                        
                        unlock_time = last_attempt + timedelta(minutes=SecurityConfig.LOGIN_LOCKOUT_MINUTES)
                        
                        if datetime.now() < unlock_time:
                            return True, unlock_time
            
            return False, None
            
        except Exception as e:
            logger.error(f"Error checking lockout status: {str(e)}")
            return False, None
    
    @staticmethod
    def get_remaining_attempts(username: str) -> int:
        """
        Get the number of remaining login attempts before lockout.
        
        Args:
            username: Username to check
            
        Returns:
            int: Number of remaining attempts (0 if locked out)
        """
        lockout_window = datetime.now() - timedelta(minutes=SecurityConfig.LOGIN_LOCKOUT_MINUTES)
        
        try:
            sql = """
                SELECT COUNT(*) as attempt_count
                FROM login_attempts
                WHERE username = :username
                  AND attempt_time > :lockout_window
                  AND success = false
            """
            
            params = {
                'username': username,
                'lockout_window': lockout_window.strftime('%Y-%m-%d %H:%M:%S')
            }
            
            result = QueryHelper.fetch_one(sql, params)
            
            if result:
                attempt_count = result.get('attempt_count', 0)
                remaining = SecurityConfig.MAX_LOGIN_ATTEMPTS - attempt_count
                return max(0, remaining)
            
            return SecurityConfig.MAX_LOGIN_ATTEMPTS
            
        except Exception as e:
            logger.error(f"Error getting remaining attempts: {str(e)}")
            return SecurityConfig.MAX_LOGIN_ATTEMPTS
    
    @staticmethod
    def clear_attempts(username: str) -> bool:
        """
        Clear all failed login attempts for a user (called after successful login).
        
        Args:
            username: Username to clear attempts for
            
        Returns:
            bool: True if cleared successfully, False otherwise
        """
        try:
            sql = """
                DELETE FROM login_attempts
                WHERE username = :username AND success = false
            """
            
            params = {'username': username}
            
            result = QueryHelper.execute(sql, params)
            
            logger.info(f"Cleared failed login attempts for {username}")
            return result['success']
            
        except Exception as e:
            logger.error(f"Error clearing login attempts: {str(e)}")
            return False
    
    @staticmethod
    def cleanup_old_attempts(days: int = 30) -> int:
        """
        Clean up login attempt records older than specified days.
        Should be called periodically to prevent table bloat.
        
        Args:
            days: Number of days to keep records for
            
        Returns:
            int: Number of records deleted (-1 on error)
        """
        cutoff_date = datetime.now() - timedelta(days=days)
        
        try:
            sql = """
                DELETE FROM login_attempts
                WHERE attempt_time < :cutoff_date
            """
            
            params = {'cutoff_date': cutoff_date.strftime('%Y-%m-%d %H:%M:%S')}
            
            result = QueryHelper.execute(sql, params)
            
            deleted_count = result.get('rows_affected', 0)
            logger.info(f"Cleaned up {deleted_count} old login attempt records")
            return deleted_count
            
        except Exception as e:
            logger.error(f"Error cleaning up old attempts: {str(e)}")
            return -1
