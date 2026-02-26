import os
import sys
from PyQt6 import uic
from PyQt6 import QtCore
from PyQt6.QtWidgets import QWidget
from PyQt6.QtCore import pyqtSignal

class ReceiptView(QWidget):

    save_requested = pyqtSignal()
    material_selected = pyqtSignal()

    def __init__(self):
        super(ReceiptView, self).__init__()

        # Initialize components
        self.initialize_components()

    
    def initialize_components(self):
        # Load ui path
        ui_path = os.path.join(os.path.dirname(__file__), "..", "ui", "receipt_view.ui")
        # Load ui
        uic.loadUi(ui_path, self)

        self.btn_save.clicked.connect(self.save_requested.emit)

        self.btn_select_material.clicked.connect(self.material_selected.emit)

        self.btn_close.clicked.connect(self.close)

    def get_receipt_form_data(self)-> dict | None:
        return {
            "material_id": self.material_id,  
            "supplier_name": self.input_supplier_name.text(),
            "quantity": self.input_quantity.text(),
            "notes": self.input_notes.toPlainText().strip(),
            # "created_by": self.current_user.user_id
        }

    def load_user_information(self, user_info: dict) -> None:        
        self.label_user_name.setText(f"User ID: {user_info.get('user_id', '')}")
        self.label_user_role.setText(f"User Role: {user_info.get('user_role', '')}")

    def display_selected_material(self, material: dict)-> None:

        # Extract material details
        self.material_id = material.get("id", "")
        material_name = material.get("material_name", "")
        description = material.get("description", "")
        unit = material.get("unit", "")

        # Format text to display
        display_text = (
            f"ID: {self.material_id} | "
            f"Name: {material_name} | "
            f"Description: {description} | "
            f"Unit: {unit}"
        )

        self.label_material.setText(display_text)

