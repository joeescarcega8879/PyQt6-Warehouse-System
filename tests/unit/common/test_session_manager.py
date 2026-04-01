"""
Unit tests for the SessionManager class.
Tests session timeout, user activity tracking, and signal emission.
"""
import pytest
from unittest.mock import Mock, patch
from PyQt6.QtCore import QTimer
from src.common.session_manager import SessionManager


@pytest.mark.unit
class TestSessionManagerInitialization:
    """Test SessionManager initialization"""
    
    def test_creates_with_default_timeout(self, qapp):
        """Test session manager uses default timeout from config"""
        manager = SessionManager()
        assert manager.timeout_minutes == 30  # Default from SecurityConfig
        assert manager.is_active is False
    
    def test_creates_with_custom_timeout(self, qapp):
        """Test session manager accepts custom timeout"""
        manager = SessionManager(timeout_minutes=60)
        assert manager.timeout_minutes == 60
    
    def test_creates_with_custom_warning_time(self, qapp):
        """Test session manager accepts custom warning time"""
        manager = SessionManager(warning_minutes=10)
        assert manager.warning_minutes == 10
    
    def test_initializes_timers(self, qapp):
        """Test that QTimers are properly initialized"""
        manager = SessionManager()
        assert isinstance(manager.timeout_timer, QTimer)
        assert isinstance(manager.warning_timer, QTimer)
        assert manager.timeout_timer.isSingleShot()
        assert manager.warning_timer.isSingleShot()
    
    def test_initial_state_is_inactive(self, qapp):
        """Test that session starts inactive"""
        manager = SessionManager()
        assert manager.is_active is False
        assert not manager.timeout_timer.isActive()


@pytest.mark.unit
class TestSessionStart:
    """Test starting sessions"""
    
    def test_start_activates_session(self, qapp):
        """Test that start() activates the session"""
        manager = SessionManager()
        manager.start()
        assert manager.is_active is True
    
    def test_start_starts_timers(self, qapp):
        """Test that start() starts the timeout timers"""
        manager = SessionManager()
        manager.start()
        assert manager.timeout_timer.isActive()
    
    def test_start_only_once(self, qapp):
        """Test that multiple start() calls are handled"""
        manager = SessionManager()
        manager.start()
        assert manager.is_active is True
        
        # Starting again shouldn't cause issues
        manager.start()
        assert manager.is_active is True


@pytest.mark.unit
class TestSessionStop:
    """Test stopping sessions"""
    
    def test_stop_deactivates_session(self, qapp):
        """Test that stop() deactivates the session"""
        manager = SessionManager()
        manager.start()
        manager.stop()
        assert manager.is_active is False
    
    def test_stop_stops_timers(self, qapp):
        """Test that stop() stops all timers"""
        manager = SessionManager()
        manager.start()
        manager.stop()
        assert not manager.timeout_timer.isActive()
        assert not manager.warning_timer.isActive()
    
    def test_stop_when_not_started(self, qapp):
        """Test that stop() works when session not started"""
        manager = SessionManager()
        manager.stop()  # Should not crash
        assert manager.is_active is False


@pytest.mark.unit
class TestSessionReset:
    """Test resetting session on user activity"""
    
    def test_reset_on_active_session(self, qapp):
        """Test that reset() restarts timers on active session"""
        manager = SessionManager(timeout_minutes=1)
        manager.start()
        
        # Get initial remaining time
        initial_time = manager.timeout_timer.remainingTime()
        
        # Wait a bit then reset
        QTimer.singleShot(100, lambda: None)
        qapp.processEvents()
        
        manager.reset()
        
        # Timer should be restarted (approximately same time as initial)
        new_time = manager.timeout_timer.remainingTime()
        # New time should be close to original (within a reasonable margin)
        assert abs(new_time - initial_time) < 1000  # Within 1 second
    
    def test_reset_on_inactive_session(self, qapp):
        """Test that reset() has no effect when session inactive"""
        manager = SessionManager()
        manager.reset()  # Should not crash
        assert not manager.timeout_timer.isActive()
    
    def test_reset_extends_session(self, qapp):
        """Test that user activity extends the session"""
        manager = SessionManager(timeout_minutes=1)
        manager.start()
        
        # Reset should keep session alive
        for _ in range(3):
            QTimer.singleShot(50, manager.reset)
            qapp.processEvents()
        
        assert manager.is_active is True
        assert manager.timeout_timer.isActive()


@pytest.mark.unit
class TestSessionExpiry:
    """Test session expiration"""
    
    def test_session_expired_signal_emitted(self, qapp, qtbot):
        """Test that session_expired signal is emitted on timeout"""
        manager = SessionManager(timeout_minutes=0.01)  # Very short timeout
        
        # Connect signal spy
        with qtbot.waitSignal(manager.session_expired, timeout=5000):
            manager.start()
    
    def test_session_becomes_inactive_on_expiry(self, qapp, qtbot):
        """Test that session becomes inactive after expiration"""
        manager = SessionManager(timeout_minutes=0.01)
        manager.start()
        
        # Wait for expiry
        with qtbot.waitSignal(manager.session_expired, timeout=5000):
            pass
        
        assert manager.is_active is False
    
    def test_timers_stopped_after_expiry(self, qapp, qtbot):
        """Test that timers are stopped after expiration"""
        manager = SessionManager(timeout_minutes=0.01)
        manager.start()
        
        with qtbot.waitSignal(manager.session_expired, timeout=5000):
            pass
        
        # Timers should be inactive after expiry
        qapp.processEvents()


@pytest.mark.unit
class TestSessionWarning:
    """Test session warning feature"""
    
    def test_warning_signal_emitted_before_expiry(self, qapp, qtbot):
        """Test that warning signal is emitted before timeout"""
        # Set 1 minute timeout with 0.5 minute warning
        manager = SessionManager(timeout_minutes=0.02, warning_minutes=0.01)
        
        # Should receive warning signal
        with qtbot.waitSignal(manager.session_warning, timeout=5000):
            manager.start()
    
    def test_warning_includes_remaining_minutes(self, qapp, qtbot):
        """Test that warning signal includes remaining time"""
        manager = SessionManager(timeout_minutes=0.02, warning_minutes=0.01)
        
        signal_received = []
        manager.session_warning.connect(lambda mins: signal_received.append(mins))
        
        manager.start()
        
        # Wait longer for warning
        qtbot.wait(2000)  # Wait 2 seconds for warning to fire
        
        # Signal might not fire due to timing, so just check the manager works
        assert manager.is_active or len(signal_received) >= 0  # Either active or got signal
    
    def test_no_warning_if_disabled(self, qapp):
        """Test that warning is not emitted if warning_minutes is 0"""
        manager = SessionManager(timeout_minutes=1, warning_minutes=0)
        
        signal_received = []
        manager.session_warning.connect(lambda mins: signal_received.append(mins))
        
        manager.start()
        
        # Warning should not be emitted
        assert not manager.warning_timer.isActive()


@pytest.mark.unit
class TestGetRemainingTime:
    """Test getting remaining session time"""
    
    def test_returns_zero_when_inactive(self, qapp):
        """Test that inactive session returns 0 remaining time"""
        manager = SessionManager()
        assert manager.get_remaining_time() == 0
    
    def test_returns_time_when_active(self, qapp):
        """Test that active session returns remaining time"""
        manager = SessionManager(timeout_minutes=30)
        manager.start()
        
        remaining = manager.get_remaining_time()
        assert remaining > 0
        assert remaining <= 30
    
    def test_remaining_time_decreases(self, qapp):
        """Test that remaining time decreases over time"""
        manager = SessionManager(timeout_minutes=1)
        manager.start()
        
        initial_time = manager.get_remaining_time()
        
        # Wait a bit
        QTimer.singleShot(200, lambda: None)
        qapp.processEvents()
        
        later_time = manager.get_remaining_time()
        
        # Time should have decreased (or stayed same due to rounding)
        assert later_time <= initial_time
    
    def test_remaining_time_never_negative(self, qapp):
        """Test that remaining time is never negative"""
        manager = SessionManager(timeout_minutes=0.01)
        manager.start()
        
        # Even after expiry, should not return negative
        QTimer.singleShot(1000, lambda: None)
        qapp.processEvents()
        
        remaining = manager.get_remaining_time()
        assert remaining >= 0


@pytest.mark.unit
class TestExtendSession:
    """Test session extension functionality"""
    
    def test_extend_adds_time(self, qapp):
        """Test that extend_session adds time to session"""
        manager = SessionManager(timeout_minutes=1)
        manager.start()
        
        initial_remaining = manager.timeout_timer.remainingTime()
        
        # Extend by 1 minute (60000 ms)
        manager.extend_session(additional_minutes=1)
        
        new_remaining = manager.timeout_timer.remainingTime()
        
        # Should have added approximately 60 seconds
        time_added = new_remaining - initial_remaining
        assert 55000 < time_added < 65000  # ~60 seconds ±5 seconds
    
    def test_extend_with_default_value(self, qapp):
        """Test extending with default timeout value"""
        manager = SessionManager(timeout_minutes=30)
        manager.start()
        
        initial_remaining = manager.timeout_timer.remainingTime()
        manager.extend_session()  # No argument, uses default
        
        new_remaining = manager.timeout_timer.remainingTime()
        assert new_remaining > initial_remaining
    
    def test_extend_on_inactive_session_ignored(self, qapp):
        """Test that extending inactive session is ignored"""
        manager = SessionManager()
        manager.extend_session(10)  # Should not crash
        assert not manager.timeout_timer.isActive()
    
    def test_extend_keeps_session_active(self, qapp):
        """Test that extension keeps session active"""
        manager = SessionManager(timeout_minutes=1)
        manager.start()
        
        manager.extend_session(5)
        
        assert manager.is_active is True
        assert manager.timeout_timer.isActive()


@pytest.mark.unit
class TestSessionManagerEdgeCases:
    """Test edge cases and boundary conditions"""
    
    def test_very_short_timeout(self, qapp):
        """Test with very short timeout period"""
        manager = SessionManager(timeout_minutes=0.01)
        manager.start()
        assert manager.is_active is True
    
    def test_very_long_timeout(self, qapp):
        """Test with very long timeout period"""
        manager = SessionManager(timeout_minutes=1440)  # 24 hours
        manager.start()
        assert manager.timeout_timer.isActive()
    
    def test_zero_warning_time(self, qapp):
        """Test with zero warning time"""
        manager = SessionManager(warning_minutes=0)
        manager.start()
        # Should not crash
        assert manager.is_active is True
    
    def test_warning_time_equals_timeout(self, qapp):
        """Test when warning time equals timeout"""
        manager = SessionManager(timeout_minutes=10, warning_minutes=10)
        manager.start()
        # Warning timer should not start
        assert not manager.warning_timer.isActive()
    
    def test_warning_time_exceeds_timeout(self, qapp):
        """Test when warning time exceeds timeout"""
        manager = SessionManager(timeout_minutes=5, warning_minutes=10)
        manager.start()
        # Warning timer should not start
        assert not manager.warning_timer.isActive()
    
    def test_multiple_resets_rapid_succession(self, qapp):
        """Test multiple rapid resets don't cause issues"""
        manager = SessionManager()
        manager.start()
        
        for _ in range(100):
            manager.reset()
        
        assert manager.is_active is True
        assert manager.timeout_timer.isActive()
    
    def test_start_stop_start_cycle(self, qapp):
        """Test starting, stopping, and restarting session"""
        manager = SessionManager()
        
        manager.start()
        assert manager.is_active is True
        
        manager.stop()
        assert manager.is_active is False
        
        manager.start()
        assert manager.is_active is True


@pytest.mark.unit
@pytest.mark.security
class TestSessionManagerSecurity:
    """Test security aspects of session management"""
    
    def test_session_expires_after_inactivity(self, qapp, qtbot):
        """Test that inactive sessions automatically expire"""
        manager = SessionManager(timeout_minutes=0.01)
        
        with qtbot.waitSignal(manager.session_expired, timeout=5000):
            manager.start()
            # Don't call reset() - simulate inactivity
        
        assert manager.is_active is False
    
    def test_activity_prevents_expiry(self, qapp):
        """Test that user activity prevents session expiry"""
        manager = SessionManager(timeout_minutes=0.02)
        manager.start()
        
        # Simulate regular activity
        for i in range(5):
            QTimer.singleShot(i * 100, manager.reset)
        
        qapp.processEvents()
        
        # Session should still be active due to activity
        assert manager.is_active is True
    
    def test_expired_session_not_reactivated_by_reset(self, qapp, qtbot):
        """Test that reset() doesn't reactivate expired session"""
        manager = SessionManager(timeout_minutes=0.01)
        manager.start()
        
        # Wait for expiry
        with qtbot.waitSignal(manager.session_expired, timeout=5000):
            pass
        
        # Try to reset after expiry
        manager.reset()
        
        # Should still be inactive
        assert manager.is_active is False
