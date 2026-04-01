from datetime import datetime
from src.config.logger_config import logger
from src.models.user_model import UserModel
from src.domain.login_attempt_tracker import LoginAttemptTracker
from src.common.error_messages import ErrorMessages


class LoginPresenter:
    def __init__(self, view, on_login_success):
        self.view = view
        self._on_login_success = on_login_success
        self._connect_signals()

    def _connect_signals(self):
        self.view.login_request.connect(self._handle_login)

    def _handle_login(self):
        username, password = self.view.get_credentials()

        if not username or not password:
            self.view.show_error(ErrorMessages.VALIDATION_ERROR)
            return
        
        # Check if user is locked out
        is_locked, unlock_time = LoginAttemptTracker.is_locked_out(username)
        if is_locked and unlock_time:
            minutes_remaining = (unlock_time - datetime.now()).seconds // 60 + 1
            error_msg = f"{ErrorMessages.ACCOUNT_LOCKED} Try again in {minutes_remaining} minute(s)."
            self.view.show_error(error_msg)
            
            ErrorMessages.log_security_event(
                "Login attempt on locked account",
                username=username,
                details=f"Account locked until {unlock_time}"
            )
            return
        
        try:
            user, error = UserModel.authenticate_user(username, password)

            if error:
                # Record failed attempt
                LoginAttemptTracker.record_attempt(username, success=False)
                
                # Get remaining attempts
                remaining = LoginAttemptTracker.get_remaining_attempts(username)
                
                # Log security event
                ErrorMessages.log_security_event(
                    "Failed login attempt",
                    username=username,
                    details=f"{remaining} attempts remaining"
                )
                
                # Show user-friendly error with remaining attempts
                if remaining > 0:
                    error_msg = f"{ErrorMessages.LOGIN_FAILED} {remaining} attempt(s) remaining."
                else:
                    error_msg = ErrorMessages.ACCOUNT_LOCKED
                
                self.view.show_error(error_msg)
                return

            # Successful login
            LoginAttemptTracker.record_attempt(username, success=True)
            LoginAttemptTracker.clear_attempts(username)
            
            logger.info(f"Successful login for user: {username}")
            
            self.view.clear_form()
            self.view.close_view()
            self._on_login_success(user)

        except Exception as e:
            error_msg = ErrorMessages.log_and_mask_error(
                e, 
                f"Login attempt for user {username}", 
                ErrorMessages.AUTHENTICATION_ERROR
            )
            self.view.show_error(error_msg)