import logging
from models.user_model import UserModel

from common.styles import StatusType

class ChangePasswordPresenter:
    def __init__(self, view, user_id, current_user, status_handler):
        self.view = view
        self.user_id = user_id
        self.current_user = current_user
        self.status_handler = status_handler


        self._connect_signals()
    
    def _connect_signals(self):
        self.view.get_button_box().accepted.connect(self._change_password)
        self.view.get_button_box().rejected.connect(self.view.close)


    def _change_password(self):
    
        password = self.view.get_password()
        confirm_password = self.view.get_confirm_password()

        if not password or not confirm_password:
            self._emit_error("Password fields cannot be empty")
            return
        
        if password != confirm_password:
            self._emit_error("Passwords do not match")
            return

        try:
            success = UserModel.change_user_password(self.user_id, password)

            if not success:
                self._emit_error("Failed to change password")
                return
        except Exception:
            logging.exception("Error changing password for user")
            self._emit_error("An unexpected error occurred while changing the password")
            return
        
        self._emit_success("Password changed successfully")
        self.view.accept()
    
    def _validate(self, password: str, confirm_password: str) -> str | None:

        if not password or not confirm_password:
            return "Password fields cannot be empty"

        if password != confirm_password:
            return "Passwords do not match"

        return None
    
    def _emit_error(self, message: str) -> None:
        self.status_handler(message, 3000, StatusType.ERROR)
    
    def _emit_success(self, message: str) -> None:
        self.status_handler(message, 3000, StatusType.SUCCESS)