import os
from re import search
from tkinter import NO
from PyQt6 import uic
from PyQt6.QtCore import pyqtSignal
from PyQt6.QtWidgets import QWidget

from common.format import FormatComponents

class UserView(QWidget):

    # Signals to request actions
    save_requested = pyqtSignal()
    edit_requested = pyqtSignal()
    change_password_requested = pyqtSignal()
    search_text_changed = pyqtSignal(str)

    def __init__(self):
        super(UserView, self).__init__()
    
        # Initialize components
        self.initialize_components()

    def initialize_components(self):
        # Load ui path
        ui_path = os.path.join(os.path.dirname(__file__), "..", "ui", "user_view.ui")
        # Load ui
        uic.loadUi(ui_path, self)

        # Connect buttons
        self.btn_save.clicked.connect(self.save_requested.emit)

        self.btn_update.clicked.connect(self.edit_requested.emit)

        self.btn_change_password.clicked.connect(self.change_password_requested.emit)

        self.btn_close.clicked.connect(self.close)

        self.input_search.textChanged.connect(self.on_search_text_changed)


        self.initialize_user_role_combo_box()

    def get_selected_user_id(self) -> int | None:
        current_row = self.tableWidget.currentRow()
        if current_row < 0:
            return None
        
        user_id = self.tableWidget.item(current_row, 0)
        if user_id is None:
            return None
        
        return int(user_id.text())

    def get_user_form_data(self) -> dict:
        return {
            "username": self.input_username.text(),
            "password": self.input_password.text(),
            "confirm_password": self.input_confirm_password.text(),
            "full_name": self.input_full_name.text(),
            "user_role": self.cbo_user_role.currentData(),
            "is_active": self.cbo_is_active.currentData(),
        }
    
    def get_selected_user_data(self) -> dict | None:
        current_row = self.tableWidget.currentRow()
        if current_row < 0:
            return None
        
        table = self.tableWidget
        return {
            "user_id": int(table.item(current_row, 0).text()),
            "username": table.item(current_row, 1).text(),
            "full_name": table.item(current_row, 2).text(),
            "user_role": table.item(current_row, 3).text(),
            "is_active": table.item(current_row, 4).text(),
        }
    
    def set_form_data(self, data: dict) -> None:
        self.input_username.setText(data["username"])
        self.input_full_name.setText(data["full_name"])
        self.input_password.setText("")  # Clear password field
        self.input_password.setEnabled(False)  # Disable password field during edit
        self.input_confirm_password.setText("")  # Clear confirm password field
        self.input_confirm_password.setEnabled(False)  # Disable confirm password field during edit

        role_index = self.cbo_user_role.findData(data["user_role"])
        is_active_index = self.cbo_is_active.findData(data["is_active"])

        self.cbo_user_role.setCurrentIndex(role_index if role_index != -1 else 0)
        self.cbo_is_active.setCurrentIndex(is_active_index if is_active_index != -1 else 0)

    def load_user_information(self, user_info: dict) -> None:
        self.label_user_name.setText(f"UserName: {user_info.get('username', '')}")
        self.label_user_role.setText(f"UserRole: {user_info.get('user_role', '')}")

    def on_search_text_changed(self, text: str) -> None:
        self.search_text_changed.emit(text)
    
    def enable_create(self, enable: bool) -> None:
        self.btn_save.setEnabled(enable)

    def enable_edit(self, enable: bool) -> None:
        self.btn_update.setEnabled(enable)

    def enable_change_password(self, enable: bool) -> None:
        self.btn_change_password.setEnabled(enable)

    def enable_password_fields(self, enable: bool) -> None:
        self.input_password.setEnabled(enable)
        self.input_confirm_password.setEnabled(enable)

    def load_users(self, users: list) -> None:
        headers = ["ID", "Username", "Full Name", "User Role", "Is Active"]
        FormatComponents.format_qtablewidget(self.tableWidget, headers, users)

    def initialize_user_role_combo_box(self)-> None:
        roles = ["admin", "operator", "viewer"]
        is_active_user = [True, False]

        self.cbo_user_role.clear()
        self.cbo_is_active.clear()

        for role in roles:
            self.cbo_user_role.addItem(role, role)

        for active in is_active_user:
            self.cbo_is_active.addItem(str(active), active)

    def clear_form(self) -> None:
        self.input_username.clear()
        self.input_password.clear()
        self.input_confirm_password.clear()
        self.input_full_name.clear()
        self.cbo_user_role.setCurrentIndex(0)
        self.cbo_is_active.setCurrentIndex(0)

        self.tableWidget.clearSelection()
        self.tableWidget.setCurrentCell(-1, -1)