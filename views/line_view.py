import os
from PyQt6 import uic
from PyQt6.QtCore import pyqtSignal
from PyQt6.QtWidgets import QWidget

from common.format import FormatComponents

class LineView(QWidget):

    # Signals for interactions
    save_requested = pyqtSignal()

    def __init__(self):
        super(LineView, self).__init__()

        # Initialize components
        self.initialize_components()


    def initialize_components(self):
        # Load ui path
        ui_path = os.path.join(os.path.dirname(__file__), "..", "ui", "line_view.ui")
        # Load ui
        uic.loadUi(ui_path, self)

        # Connect buttons
        self.btn_save.clicked.connect(self.save_requested.emit)

        self.init_combo_box_is_active()

    def get_line_form_data(self) -> dict:
        return {
            "name": self.input_line_name.text(),
            "description": self.input_description.toPlainText().strip(),
            "is_active": self.cbo_is_active.currentData()
        }
    
    def load_lines_data(self, lines_data: list) -> None:
        headers = ["ID", "Line Name", "Description", "Is Active"]
        FormatComponents.format_qtablewidget(self.tableWidget, headers, lines_data)

    def load_user_information(self, user_info: dict) -> None:
        self.label_user_name.setText(f"UserName: {user_info.get('username', '')}")
        self.label_user_role.setText(f"UserRole: {user_info.get('user_role', '')}")

    def clean_form(self)-> None:
        self.input_line_name.clear()
        self.input_line_name.setFocus()

        self.input_description.clear()
        self.cbo_is_active.setCurrentIndex(0)

        self.tableWidget.clearSelection()
        self.tableWidget.setCurrentCell(-1, -1)
    
    def init_combo_box_is_active(self):
        is_active_line = [True, False]
        
        for status in is_active_line:
            self.cbo_is_active.addItem(str(status), status)