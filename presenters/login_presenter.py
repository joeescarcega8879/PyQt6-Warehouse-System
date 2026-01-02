import logging
from models.user_model import UserModel

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
            self.view.show_error("Username and password cannot be empty.")
            return
        
        try:
            user, error = UserModel.authenticate_user(username, password)

            if error:
                self.view.show_error(error)
                return

            self.view.clear_form()
            self.view.close_view()
            self._on_login_success(user)

        except Exception as e:
            logging.error(f"Login error: {e}")
            self.view.show_error("An unexpected error occurred during login.")