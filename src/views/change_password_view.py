from pathlib import Path
from PyQt6 import uic
from pathlib import Path
from PyQt6.QtCore import pyqtSignal
from pathlib import Path
from PyQt6.QtWidgets import QDialog

from src.common.style_manager import StyleManager

class ChangePasswordView(QDialog):

    # Constructor
    def __init__(self):
        super(ChangePasswordView, self).__init__()

        # Initialize components
        self.initialize_components()
        # Load global styles
        StyleManager.apply_global_styles(self)


    def initialize_components(self):
            # Load ui path
            ui_path = Path(__file__).resolve().parent / "ui" / "change_password.ui"
            # Load ui
            uic.loadUi(str(ui_path), self)

            self.input_password.setFocus()
            self.buttonBox.accepted.disconnect()

    
    def get_button_box(self):
         return self.buttonBox
    
    def get_password(self) -> str:
        return self.input_password.text()
    
    def get_confirm_password(self) -> str:
        return self.input_confirm_password.text()