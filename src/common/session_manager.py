"""
Session management with automatic timeout for security.
Automatically logs out users after a period of inactivity.
"""
from PyQt6.QtCore import QObject, QTimer, pyqtSignal
from src.config.settings import SecurityConfig
import logging

logger = logging.getLogger(__name__)


class SessionManager(QObject):
    """
    Manages user session timeout for security.
    
    Automatically tracks user activity and triggers session expiration
    after a configured period of inactivity.
    
    Signals:
        session_expired: Emitted when the session times out
        session_warning: Emitted X minutes before timeout (for optional warning dialog)
    """
    
    session_expired = pyqtSignal()
    session_warning = pyqtSignal(int)  # Signal with minutes remaining
    
    def __init__(self, timeout_minutes: int = None, warning_minutes: int = 5):
        """
        Initialize the session manager.
        
        Args:
            timeout_minutes: Timeout in minutes (defaults to SecurityConfig value)
            warning_minutes: Minutes before timeout to emit warning signal
        """
        super().__init__()
        
        self.timeout_minutes = timeout_minutes or SecurityConfig.SESSION_TIMEOUT_MINUTES
        self.warning_minutes = warning_minutes
        self.is_active = False
        
        # Main timeout timer
        self.timeout_timer = QTimer()
        self.timeout_timer.timeout.connect(self._on_timeout)
        self.timeout_timer.setSingleShot(True)
        
        # Warning timer (fires before main timeout)
        self.warning_timer = QTimer()
        self.warning_timer.timeout.connect(self._on_warning)
        self.warning_timer.setSingleShot(True)
        
        logger.info(f"Session manager initialized with {self.timeout_minutes} minute timeout")
    
    def start(self) -> None:
        """
        Start the session timer.
        Called when user successfully logs in.
        """
        if not self.is_active:
            self.is_active = True
            self._reset_timers()
            logger.info("Session started")
    
    def stop(self) -> None:
        """
        Stop the session timer.
        Called when user logs out or session expires.
        """
        self.is_active = False
        self.timeout_timer.stop()
        self.warning_timer.stop()
        logger.info("Session stopped")
    
    def reset(self) -> None:
        """
        Reset the timeout timer due to user activity.
        Should be called on any user interaction (clicks, key presses, etc.).
        """
        if self.is_active:
            self._reset_timers()
    
    def _reset_timers(self) -> None:
        """Internal method to reset both timers"""
        # Calculate timeout in milliseconds (must be int)
        timeout_ms = int(self.timeout_minutes * 60 * 1000)
        warning_ms = int((self.timeout_minutes - self.warning_minutes) * 60 * 1000)
        
        # Restart main timeout timer
        self.timeout_timer.start(timeout_ms)
        
        # Restart warning timer (only if warning time is before timeout)
        if self.warning_minutes < self.timeout_minutes and self.warning_minutes > 0:
            self.warning_timer.start(warning_ms)
    
    def _on_warning(self) -> None:
        """
        Called when warning timer expires.
        Emits signal to optionally show warning to user.
        """
        if self.is_active:
            logger.info(f"Session warning: {self.warning_minutes} minutes remaining")
            self.session_warning.emit(self.warning_minutes)
    
    def _on_timeout(self) -> None:
        """
        Called when session timeout expires.
        Emits signal to log out user.
        """
        if self.is_active:
            logger.warning("Session expired due to inactivity")
            self.is_active = False
            self.session_expired.emit()
    
    def get_remaining_time(self) -> int:
        """
        Get remaining time in minutes before session expires.
        
        Returns:
            int: Minutes remaining (0 if session not active)
        """
        if not self.is_active or not self.timeout_timer.isActive():
            return 0
        
        remaining_ms = self.timeout_timer.remainingTime()
        remaining_minutes = remaining_ms // 60000
        return max(0, remaining_minutes)
    
    def extend_session(self, additional_minutes: int = None) -> None:
        """
        Extend the current session by additional minutes.
        Useful for long-running operations.
        
        Args:
            additional_minutes: Minutes to add (defaults to original timeout)
        """
        if self.is_active:
            if additional_minutes is None:
                additional_minutes = self.timeout_minutes
            
            # Get current remaining time
            remaining_ms = self.timeout_timer.remainingTime()
            
            # Add extension (must be int)
            new_timeout_ms = int(remaining_ms + (additional_minutes * 60 * 1000))
            
            # Restart timer with new timeout
            self.timeout_timer.start(new_timeout_ms)
            
            logger.info(f"Session extended by {additional_minutes} minutes")
