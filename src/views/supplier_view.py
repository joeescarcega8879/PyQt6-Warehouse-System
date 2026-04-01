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

class SupplierView(QWidget):
    
    # Signals to request actions
    save_requested = pyqtSignal()
    edit_requested = pyqtSignal()
    cancel_requested = pyqtSignal()
    search_text_changed = pyqtSignal(str)
    
    def __init__(self):
        super(SupplierView, self).__init__()

        # Initialize components
        self.initialize_components()        
    
    def initialize_components(self):
        # Load ui path
        ui_path = Path(__file__).resolve().parent / "ui" / "supplier_view.ui"
        # Load ui
        uic.loadUi(str(ui_path), self)
        
        # Set button icons
        self.btn_close.setIcon(_icon("IMG-LogOut.png"))

        
        # Connect signals
        self.btn_save.clicked.connect(self.save_requested.emit)
        self.btn_update.clicked.connect(self.edit_requested.emit) 
        self.btn_cancel.clicked.connect(self.cancel_requested.emit)
        self.btn_close.clicked.connect(self.close)
        self.input_search.textChanged.connect(self.on_search_text_changed)    
        
        self.init_combo_box_is_active()
        
        
    def get_supplier_form_data(self) -> dict | None:
        return {
            "supplier_name": self.input_supplier_name.text(),
            "contact_department": self.input_contact_department.text(),
            "phone": self.input_phone.text(),
            "email": self.input_email.text(),
            "address": self.input_address.text(),
            "is_active": self.cbo_is_active.currentData(),
            "notes": self.input_notes.toPlainText().strip()
        }
        
    def get_selected_supplier_id(self) -> int | None:
        current_row = self.tableWidget.currentRow()
        if current_row < 0:
            return None
        
        item = self.tableWidget.item(current_row, 0)
        return int(item.text()) if item else None
    
    def get_selected_supplier_data(self) -> dict | None:
        current_row = self.tableWidget.currentRow()

        if current_row < 0:
            return None
        
        table = self.tableWidget
        return {
            "id": int(table.item(current_row, 0).text()),
            "supplier_name": table.item(current_row, 1).text(),
            "contact_department": table.item(current_row, 2).text(),
            "phone": table.item(current_row, 3).text(),
            "email": table.item(current_row, 4).text(),
            "address": table.item(current_row, 5).text(),
            "is_active": table.item(current_row, 6).text() == "True",
            "notes": table.item(current_row, 7).text()
        }
    
    def set_form_data(self, data: dict) -> None:
        self.input_supplier_name.setText(data["supplier_name"])
        self.input_contact_department.setText(data["contact_department"])
        self.input_phone.setText(data["phone"])
        self.input_email.setText(data["email"])
        self.input_address.setText(data["address"])
        self.cbo_is_active.setCurrentIndex(self.cbo_is_active.findData(data["is_active"]))
        self.input_notes.setPlainText(data["notes"])
        
    def load_suppliers(self, suppliers: list) -> None:
        headers = ["ID", "Supplier Name", "Contact Department", "Phone", "Email", "Address", "Notes", "Is Active"]
        FormatComponents.format_qtablewidget(self.tableWidget, headers, suppliers)
        
    def load_user_information(self, user_info: dict) -> None:
        self.label_user_name.setText(f"UserName: {user_info.get('username', '')}")
        self.label_user_role.setText(f"UserRole: {user_info.get('user_role', '')}")
    
    def on_search_text_changed(self, text: str) -> None:
        self.search_text_changed.emit(text)
    
    def init_combo_box_is_active(self):
        self.cbo_is_active.addItem("Active", True)
        self.cbo_is_active.addItem("Inactive", False)
        
    def clear_form(self) -> None:
        self.input_supplier_name.clear()
        self.input_contact_department.clear()
        self.input_phone.clear()
        self.input_email.clear()
        self.input_address.clear()
        self.cbo_is_active.setCurrentIndex(0)
        self.input_notes.clear()
        
        self.tableWidget.clearSelection()
        self.tableWidget.setCurrentCell(-1, -1)