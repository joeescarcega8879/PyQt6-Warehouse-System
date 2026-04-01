from PyQt6 import uic
from PyQt6.QtGui import QIcon
from PyQt6.QtWidgets import QWidget
from PyQt6.QtCore import pyqtSignal

from pathlib import Path
from src.common.format import FormatComponents

_ICONS_DIR = Path(__file__).resolve().parent.parent / "assets" / "icons"

def _icon(filename: str) -> QIcon:
    """Return a QIcon from the icons directory. Safe on any OS."""
    return QIcon(str(_ICONS_DIR / filename))


class ReceiptView(QWidget):

    save_requested = pyqtSignal()
    edit_requested = pyqtSignal()
    cancel_requested = pyqtSignal()
    material_selected = pyqtSignal()
    supplier_selected = pyqtSignal()

    def __init__(self):
        super(ReceiptView, self).__init__()

        # Initialize components
        self.initialize_components()

    
    def initialize_components(self):
        # Load ui path
        ui_path = Path(__file__).resolve().parent / "ui" / "receipt_view.ui"
        # Load ui
        uic.loadUi(str(ui_path), self)

        # Set button icons
        self.btn_close.setIcon(_icon("IMG-LogOut.png"))

        self.btn_save.clicked.connect(self.save_requested.emit)

        self.btn_select_material.clicked.connect(self.material_selected.emit)

        self.btn_select_supplier.clicked.connect(self.supplier_selected.emit)

        self.btn_update.clicked.connect(self.edit_requested.emit)

        self.btn_cancel.clicked.connect(self.cancel_requested.emit)
        
        self.btn_close.clicked.connect(self.close)

        # self.bar_information.hide()

    def get_receipt_form_data(self) -> dict | None:
        return {
            "material_id": self.material_id if hasattr(self, "material_id") else None,
            "supplier_id": self.supplier_id if hasattr(self, "supplier_id") else None,
            "quantity": self.input_quantity.text(),
            "notes": self.input_notes.toPlainText().strip(),
        }
    
    def get_selected_supplier_and_material_ids(self) -> dict | None:
        current_row = self.tableWidget.currentRow()
        if current_row < 0:
            return None
        
        supplier_item = self.tableWidget.item(current_row, 0)
        material_item = self.tableWidget.item(current_row, 1)

        return {
            "supplier_id": int(supplier_item.text()) if supplier_item else None,
            "material_id": int(material_item.text()) if material_item else None
        }
    
    def get_selected_receipt_data(self) -> dict | None:
        current_row = self.tableWidget.currentRow()
        if current_row < 0:
            return None
        
        table = self.tableWidget
        return {
            "id": int(table.item(current_row, 0).text()),
            "material_id": int(table.item(current_row, 1).text()),
            "supplier_id": int(table.item(current_row, 2).text()),
            "quantity": table.item(current_row, 4).text(),
            "notes": table.item(current_row, 6).text(),
        }

    def load_user_information(self, user_info: dict) -> None:
        self.label_user_name.setText(f"User Name: {user_info.get('username', '')}")
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

    def display_selected_supplier(self, supplier: dict) -> None:

        # Extract supplier details
        self.supplier_id = supplier.get("id", "")
        supplier_name = supplier.get("supplier_name", "")
        contact_department = supplier.get("contact_department", "")

        # Format text to display
        display_text = (
            f"ID: {self.supplier_id} | "
            f"Name: {supplier_name} | "
            f"Contact: {contact_department}"
        )

        self.label_supplier.setText(display_text)

    def clear_form(self) -> None:
        """Clear all form inputs and selections."""
        self.input_quantity.clear()
        self.input_notes.clear()
        self.label_material.clear()
        self.label_supplier.clear()
        
        # Reset stored IDs
        if hasattr(self, "material_id"):
            delattr(self, "material_id")
        if hasattr(self, "supplier_id"):
            delattr(self, "supplier_id")

    def set_form_data(self, data: dict) -> None:
        # Store IDs
        self.material_id = data.get("material_id")
        self.supplier_id = data.get("supplier_id")

        """Load receipt data into form for editing."""
        self.label_material.setText(f"Material ID: {self.material_id}")
        self.label_supplier.setText(f"Supplier ID: {self.supplier_id}")
        
        self.input_quantity.setText(str(data.get("quantity", "")))
        self.input_notes.setPlainText(data.get("notes", ""))

    def load_receipts(self, receipts: list) -> None:
        """Load receipts into the table widget."""
        headers = ["ID", "Material ID", "Supplier ID", "Supplier Name","Quantity","Receipt Date", "Notes", "Created By"]
        FormatComponents.format_qtablewidget(self.tableWidget, headers, receipts)


