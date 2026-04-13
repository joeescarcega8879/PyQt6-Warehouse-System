from PyQt6 import uic
from PyQt6.QtGui import QIcon
from PyQt6.QtWidgets import QWidget, QMessageBox, QTableWidgetItem, QTableWidget
from PyQt6.QtCore import pyqtSignal

from pathlib import Path
from src.common.format import FormatComponents

_ICONS_DIR = Path(__file__).resolve().parent.parent / "assets" / "icons"


def _icon(filename: str) -> QIcon:
    """Return a QIcon from the icons directory. Safe on any OS."""
    return QIcon(str(_ICONS_DIR / filename))


class ProductionRequestView(QWidget):

    # --- Signals ---
    save_requested        = pyqtSignal()   # Create DRAFT
    submit_requested      = pyqtSignal()   # DRAFT → SUBMITTED
    approve_requested     = pyqtSignal()   # SUBMITTED → APPROVED
    reject_requested      = pyqtSignal()   # SUBMITTED → REJECTED
    deactivate_requested  = pyqtSignal()   # Mark request inactive
    cancel_requested      = pyqtSignal()   # Clear form / cancel edit
    selected_line         = pyqtSignal()   # Open GenericView for production line
    selected_material     = pyqtSignal()   # Open GenericView for material
    add_item_requested    = pyqtSignal()   # Add item to current request
    remove_item_requested = pyqtSignal()   # Remove item from current request
    close_requested       = pyqtSignal()   # Close sub-window

    def __init__(self):
        super(ProductionRequestView, self).__init__()
        self.material_id: int | None = None
        self.line_id: int | None = None
        self.items: list[dict] = []  # Items pending for the current request
        self.initialize_components()

 
    def initialize_components(self) -> None:
        
        ui_path = Path(__file__).resolve().parent / "ui" / "production_request_view.ui"
        
        uic.loadUi(str(ui_path), self)

        # Icons
        self.btn_close.setIcon(_icon("IMG-LogOut.png"))

        # Connect action buttons
        self.btn_save.clicked.connect(self.save_requested.emit)
        # self.btn_submit.clicked.connect(self._on_submit_clicked)
        # self.btn_approve.clicked.connect(self._on_approve_clicked)
        # self.btn_reject.clicked.connect(self._on_reject_clicked)
        # self.btn_deactivate.clicked.connect(self._on_deactivate_clicked)
        self.btn_cancel.clicked.connect(self.cancel_requested.emit)
        self.btn_close.clicked.connect(self.close)

        # Connect selector buttons
        self.btn_select_line.clicked.connect(self.selected_line.emit)
        self.btn_select_material.clicked.connect(self.selected_material.emit)

        # Connect item management buttons
        self.btn_add_item.clicked.connect(self.add_item_requested.emit)
        self.btn_remove_item.clicked.connect(self.remove_item_requested.emit)

        # Table setup
        self.tableItems.setColumnCount(4)
        # Behavior configuration
        self.tableItems.setEditTriggers(QTableWidget.EditTrigger.NoEditTriggers)
        self.tableItems.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectRows)
        self.tableItems.setSelectionMode(QTableWidget.SelectionMode.SingleSelection)
        self.tableItems.setHorizontalHeaderLabels(["Line ID", "Material ID", "Quantity", "Unit"])
 

    def get_selected_material_and_line_info(self) -> dict | None:

        return {
            "material_id": self.material_id,
            "line_id": self.line_id,
            "quantity": self.input_quantity.text() or None,
            "unit": self.label_unit.text() or None
        }
        
    def get_index_from_selected_item(self) -> int | None:
        
        selected_items = self.tableItems.selectedItems()
        if not selected_items:
            return None
        
        selected_row = selected_items[0].row()
        return selected_row
    
    def remove_item_from_table(self, index: int) -> None:
        
        if 0 <= index < len(self.items):
            self.items.pop(index)
            self.tableItems.removeRow(index)        
        
    def display_added_item(self, item: dict) -> None:
        
        self.items.append(item)
        self.tableItems.setRowCount(len(self.items))
        
        row = len(self.items) - 1
        self.tableItems.setItem(row, 0, QTableWidgetItem(str(item.get("line_id", "N/A"))))
        self.tableItems.setItem(row, 1, QTableWidgetItem(str(item.get("material_id", "N/A"))))
        self.tableItems.setItem(row, 2, QTableWidgetItem(str(item.get("quantity", "N/A"))))
        self.tableItems.setItem(row, 3, QTableWidgetItem(str(item.get("unit", "N/A"))))
   
    def display_selected_material(self, material: dict) -> None:
        
        # Extract relevant info from material dict 
        self.material_id = material.get("id", "")
        material_name = material.get("material_name", "")
        unit = material.get("unit", "")
        
        display_format = (
            f"ID: {self.material_id}\n"
            f"Name: {material_name}\n"
        )
        
        self.label_material.setText(display_format)
        self.label_unit.setText(unit)
        
    def display_selected_line(self, line: dict) -> None:
        
        # Extract relevant info from line dict|
        self.line_id = line.get("id", "")
        line_name = line.get("line_name", "")
        
        display_format = (
            f"ID: {self.line_id}\n"
            f"Name: {line_name}\n"
        )
        
        self.label_line.setText(display_format)
        
    def load_user_information(self, user_info: dict) -> None:
       self.label_user_name.setText(f"UserName: {user_info.get('username', '')}")
       self.label_user_role.setText(f"UserRole: {user_info.get('user_role', '')}")
       
    def clear_form(self) -> None:
        self.input_quantity.clear()
        self.label_material.setText("0")
        self.label_line.setText("0")
        self.label_unit.setText("0")

