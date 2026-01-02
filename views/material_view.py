import os
from PyQt6 import uic
from PyQt6.QtCore import pyqtSignal
from PyQt6.QtWidgets import QWidget, QMessageBox

from common.enums import StatusType
from common.format import FormatComponents

class MaterialView(QWidget):

    # Signals to request actions
    save_requested = pyqtSignal()
    edit_requested = pyqtSignal()
    delete_requested = pyqtSignal()
    search_text_changed = pyqtSignal(str)

    # Signal to send status messages
    status_signal = pyqtSignal(str, int, StatusType)

    def __init__(self):
        super(MaterialView, self).__init__()
    
        # Initialize components
        self.initialize_components()


    def initialize_components(self):
        # Load ui path
        ui_path = os.path.join(os.path.dirname(__file__), "..", "ui", "material_view.ui")
        # Load ui
        uic.loadUi(ui_path, self)

        self.btn_save.clicked.connect(self.save_requested.emit)

        self.btn_update.clicked.connect(self.edit_requested.emit)

        self.btn_delete.clicked.connect(self.on_delete_clicked)

        self.btn_close.clicked.connect(self.close)

        self.input_search.textChanged.connect(self._on_search_text_changed)
       
        self.init_combo_box_units()


    def get_material_form_data(self) -> dict:
        return {
            "name": self.input_material_name.text(),
            "description": self.input_description.toPlainText().strip(),
            "unit": self.cbo_unit.currentData()
        }
    
    def get_selected_material_id(self) -> int | None:
        current_row = self.tableWidget.currentRow()
        if current_row < 0:
            return None
        
        item = self.tableWidget.item(current_row, 0)
        return int(item.text()) if item else None
    
    def get_selected_material_data(self) -> dict | None:
        current_row = self.tableWidget.currentRow()

        if current_row < 0:
            return None
        
        table = self.tableWidget
        return {
            "id": int(table.item(current_row, 0).text()),
            "name": table.item(current_row, 1).text(),
            "description": table.item(current_row, 2).text(),
            "unit": table.item(current_row, 3).text()
        }
    
    def set_form_data(self, data: dict) -> None:
        self.input_material_name.setText(data["name"])
        self.input_description.setPlainText(data["description"])

        index = self.cbo_unit.findData(data["unit"])
        if index != -1:
            self.cbo_unit.setCurrentIndex(index)

    def load_materials(self, materials: list) -> None:
        headers = ["ID", "Name", "Description", "Unit"]
        FormatComponents.format_qtablewidget(self.tableWidget, headers, materials)

    def load_user_information(self, user_info: dict) -> None:
        self.label_user_name.setText(f"UserName: {user_info.get("username", "")}")
        self.label_user_role.setText(f"UserRole: {user_info.get("user_role", "")}")

    def on_delete_clicked(self) -> None:

        material_id = self.get_selected_material_id()
        if material_id is None:
            self.delete_requested.emit()
            return

        reply = QMessageBox.question(

            self,
            "Confirm Delete",
            "Are you sure you want to delete this material?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
            QMessageBox.StandardButton.No
    )

        if reply == QMessageBox.StandardButton.Yes:
            self.delete_requested.emit()

    def _on_search_text_changed(self, text: str) -> None:
        self.search_text_changed.emit(text)

    def clear_form(self) -> None:

        self.input_material_name.clear()
        self.input_description.clear()
        self.cbo_unit.setCurrentIndex(0)

        self.tableWidget.clearSelection()
        self.tableWidget.setCurrentCell(-1, -1)

    def init_combo_box_units(self) -> None:
        units = [
            ("Meters (m)", "m"),
            ("Kilograms (kg)", "kg"),
            ("Pieces (pcs)", "pcs"),
        ]

        for display_text, value in units:
            self.cbo_unit.addItem(display_text, value)

    def show_error(self, message: str) -> None:
        QMessageBox.warning(self, "Error", message)

    def show_success(self, message: str) -> None:
        QMessageBox.information(self, "Success", message)
