import os
from PyQt6 import uic
from PyQt6.QtCore import pyqtSignal
from PyQt6.QtWidgets import QWidget, QMessageBox

from common.style_manager import StyleManager

class LoginView(QWidget):

    # Signals
    login_request = pyqtSignal()

    def __init__(self):
        super(LoginView, self).__init__()

        # Initialize components
        self.initialize_components()
        # Load global styles
        StyleManager.apply_global_styles(self)

    def initialize_components(self):
            # Load ui path
            ui_path = os.path.join(os.path.dirname(__file__), "..", "ui", "login_view.ui")
            # Load ui
            uic.loadUi(ui_path, self)

            self.user_input.setFocus()

            # Signals and slots
            self.btn_login.clicked.connect(self.login_request.emit)
            self.btn_cancel.clicked.connect(self.close)

    def get_credentials(self):
         return (
            self.user_input.text().strip(),
            self.pass_input.text().strip()
         )
    
    def show_error(self, message) -> None:
        QMessageBox.critical(self, "Login Error", message)

    def clear_form(self):
        self.user_input.clear()
        self.pass_input.clear()

    def close_view(self) -> None:
        self.close()