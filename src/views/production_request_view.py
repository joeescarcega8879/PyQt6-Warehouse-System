from PyQt6 import uic
from PyQt6.QtGui import QIcon
from PyQt6.QtWidgets import QWidget, QMessageBox, QTableWidgetItem
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
    close_requested       = pyqtSignal()   # Close sub-window
    line_selected         = pyqtSignal()   # Open GenericView for production line
    material_selected     = pyqtSignal()   # Open GenericView for material

    def __init__(self):
        super(ProductionRequestView, self).__init__()
        self._items: list[dict] = []  # Items pending for the current request
        self.initialize_components()

    # -------------------------------------------------------------------------
    # Initialization
    # -------------------------------------------------------------------------

    def initialize_components(self) -> None:
        ui_path = Path(__file__).resolve().parent / "ui" / "production_request_view.ui"
        uic.loadUi(str(ui_path), self)

        # Icons
        self.btn_close.setIcon(_icon("IMG-LogOut.png"))

        # Connect action buttons
        self.btn_save.clicked.connect(self.save_requested.emit)
        self.btn_submit.clicked.connect(self._on_submit_clicked)
        self.btn_approve.clicked.connect(self._on_approve_clicked)
        self.btn_reject.clicked.connect(self._on_reject_clicked)
        self.btn_deactivate.clicked.connect(self._on_deactivate_clicked)
        self.btn_cancel.clicked.connect(self.cancel_requested.emit)
        self.btn_close.clicked.connect(self.close_requested.emit)

        # Connect selector buttons
        self.btn_select_line.clicked.connect(self.line_selected.emit)
        self.btn_select_material.clicked.connect(self.material_selected.emit)

        # Connect item management buttons
        self.btn_add_item.clicked.connect(self._on_add_item_clicked)
        self.btn_remove_item.clicked.connect(self._on_remove_item_clicked)

        # Setup items table headers
        self._setup_items_table()

    # -------------------------------------------------------------------------
    # Form data
    # -------------------------------------------------------------------------

    def get_form_data(self) -> dict:
        """Return the current form data ready to pass to the presenter."""
        return {
            "line_id": self.line_id if hasattr(self, "line_id") else None,
            "status":  self.cbo_status.currentText(),
            "items":   list(self._items),
        }

    def get_selected_request_id(self) -> int | None:
        """Return the request_id of the currently selected row in the main table."""
        current_row = self.tableWidget.currentRow()
        if current_row < 0:
            return None
        item = self.tableWidget.item(current_row, 0)
        return int(item.text()) if item else None

    def get_selected_request_data(self) -> dict | None:
        """Return a dict with all visible columns of the selected row."""
        current_row = self.tableWidget.currentRow()
        if current_row < 0:
            return None

        table = self.tableWidget

        def cell(col: int) -> str:
            it = table.item(current_row, col)
            return it.text() if it else ""

        id_text = cell(0)
        if not id_text:
            return None

        return {
            "id":               int(id_text),
            "line_id":          cell(1),
            "line_name":        cell(2),
            "status":           cell(3),
            "requested_at":     cell(4),
            "requested_by":     cell(5),
            "requested_by_name":cell(6),
            "approved_by":      cell(7),
            "approved_by_name": cell(8),
            "approved_at":      cell(9),
            "is_active":        cell(10),
        }

    # -------------------------------------------------------------------------
    # Display helpers — called by the presenter
    # -------------------------------------------------------------------------

    def load_user_information(self, user_info: dict) -> None:
        self.label_user_name.setText(f"User Name: {user_info.get('username', '')}")
        self.label_user_role.setText(f"User Role: {user_info.get('user_role', '')}")

    def display_selected_line(self, line: dict) -> None:
        """Store line_id and update label_line with a summary."""
        self.line_id = line.get("id", "")
        line_name    = line.get("line_name", "")
        description  = line.get("description", "")

        display_text = (
            f"ID: {self.line_id} | "
            f"Name: {line_name} | "
            f"Description: {description}"
        )
        self.label_line.setText(display_text)

    def display_selected_material(self, material: dict) -> None:
        """Store pending material data (used by btn_add_item)."""
        self.material_id          = material.get("id", "")
        self._pending_material_name = material.get("material_name", "")
        self._pending_unit          = material.get("unit", "")

        display_text = (
            f"ID: {self.material_id} | "
            f"Name: {self._pending_material_name} | "
            f"Unit: {self._pending_unit}"
        )
        self.label_material.setText(display_text)

    def set_form_data(self, data: dict) -> None:
        """Load an existing request into the form (read-only view of header fields)."""
        self.line_id = data.get("line_id")
        self.label_line.setText(
            f"ID: {self.line_id} | Name: {data.get('line_name', '')}"
        )

        # Set status combo to the current status of the request
        status_text = data.get("status", "DRAFT")
        index = self.cbo_status.findText(status_text)
        if index != -1:
            self.cbo_status.setCurrentIndex(index)

    def load_requests(self, requests: list) -> None:
        """Populate the main tableWidget with production requests."""
        headers = [
            "ID", "Line ID", "Line Name", "Status",
            "Requested At", "Requested By ID", "Requested By",
            "Approved By ID", "Approved By", "Approved At", "Active",
        ]
        FormatComponents.format_qtablewidget(self.tableWidget, headers, requests)

    def clear_form(self) -> None:
        """Reset form to empty state."""
        # Clear line selector
        self.label_line.setText("0")
        if hasattr(self, "line_id"):
            delattr(self, "line_id")

        # Clear material selector
        self.label_material.setText("0")
        if hasattr(self, "material_id"):
            delattr(self, "material_id")
        if hasattr(self, "_pending_material_name"):
            delattr(self, "_pending_material_name")
        if hasattr(self, "_pending_unit"):
            delattr(self, "_pending_unit")

        # Clear quantity field
        self.input_quantity.clear()

        # Reset status combo
        self.cbo_status.setCurrentIndex(0)

        # Clear items list and table
        self._items.clear()
        self._refresh_items_table()

        # Deselect main table
        self.tableWidget.clearSelection()
        self.tableWidget.setCurrentCell(-1, -1)

    # -------------------------------------------------------------------------
    # Permission visibility helpers — called by the presenter
    # -------------------------------------------------------------------------

    def enable_create(self, enabled: bool) -> None:
        """Show/hide Save button and form selectors."""
        self.btn_save.setVisible(enabled)
        self.btn_select_line.setEnabled(enabled)
        self.btn_select_material.setEnabled(enabled)
        self.btn_add_item.setEnabled(enabled)
        self.btn_remove_item.setEnabled(enabled)
        self.input_quantity.setEnabled(enabled)

    def enable_submit(self, enabled: bool) -> None:
        self.btn_submit.setVisible(enabled)

    def enable_approve(self, enabled: bool) -> None:
        """Show/hide Approve and Reject buttons together (same permission)."""
        self.btn_approve.setVisible(enabled)
        self.btn_reject.setVisible(enabled)

    def enable_deactivate(self, enabled: bool) -> None:
        self.btn_deactivate.setVisible(enabled)

    # -------------------------------------------------------------------------
    # Internal: items table management
    # -------------------------------------------------------------------------

    def _setup_items_table(self) -> None:
        """Configure the items table headers (called once on init)."""
        self.tableItems.setColumnCount(3)
        self.tableItems.setHorizontalHeaderLabels(["Material", "Quantity", "Unit"])
        self.tableItems.setEditTriggers(self.tableItems.EditTrigger.NoEditTriggers)
        self.tableItems.setSelectionBehavior(self.tableItems.SelectionBehavior.SelectRows)
        self.tableItems.setSelectionMode(self.tableItems.SelectionMode.SingleSelection)
        self.tableItems.verticalHeader().hide()
        self.tableItems.setShowGrid(False)
        self.tableItems.horizontalHeader().setStretchLastSection(True)

    def _refresh_items_table(self) -> None:
        """Re-render tableItems from self._items."""
        self.tableItems.setRowCount(len(self._items))
        for row, item in enumerate(self._items):
            self.tableItems.setItem(row, 0, QTableWidgetItem(item["material_name"]))
            self.tableItems.setItem(row, 1, QTableWidgetItem(str(item["quantity"])))
            self.tableItems.setItem(row, 2, QTableWidgetItem(item["unit"]))

    def _on_add_item_clicked(self) -> None:
        """Validate inputs and append a new item to _items."""
        if not hasattr(self, "material_id"):
            QMessageBox.warning(self, "No Material", "Please select a material first.")
            return

        qty_text = self.input_quantity.text().strip()
        if not qty_text:
            QMessageBox.warning(self, "Missing Quantity", "Please enter a quantity.")
            return

        try:
            quantity = float(qty_text)
            if quantity <= 0:
                raise ValueError
        except ValueError:
            QMessageBox.warning(self, "Invalid Quantity", "Quantity must be a positive number.")
            return

        # Check for duplicate material in the current items list
        for existing in self._items:
            if existing["material_id"] == self.material_id:
                QMessageBox.warning(
                    self,
                    "Duplicate Material",
                    f"Material '{existing['material_name']}' is already in the list.\n"
                    "Remove it first if you want to change the quantity.",
                )
                return

        self._items.append({
            "material_id":   self.material_id,
            "material_name": getattr(self, "_pending_material_name", str(self.material_id)),
            "quantity":      quantity,
            "unit":          getattr(self, "_pending_unit", ""),
        })

        self._refresh_items_table()

        # Clear material selector and quantity after adding
        self.label_material.setText("0")
        self.input_quantity.clear()
        if hasattr(self, "material_id"):
            delattr(self, "material_id")
        if hasattr(self, "_pending_material_name"):
            delattr(self, "_pending_material_name")
        if hasattr(self, "_pending_unit"):
            delattr(self, "_pending_unit")

    def _on_remove_item_clicked(self) -> None:
        """Remove the currently selected item from _items."""
        current_row = self.tableItems.currentRow()
        if current_row < 0:
            QMessageBox.warning(self, "No Selection", "Please select an item to remove.")
            return
        self._items.pop(current_row)
        self._refresh_items_table()

    # -------------------------------------------------------------------------
    # Internal: confirmation dialogs for destructive / irreversible actions
    # -------------------------------------------------------------------------

    def _on_submit_clicked(self) -> None:
        reply = QMessageBox.question(
            self,
            "Confirm Submit",
            "Submit this request for approval? This action cannot be undone.",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
            QMessageBox.StandardButton.No,
        )
        if reply == QMessageBox.StandardButton.Yes:
            self.submit_requested.emit()

    def _on_approve_clicked(self) -> None:
        reply = QMessageBox.question(
            self,
            "Confirm Approve",
            "Approve this production request?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
            QMessageBox.StandardButton.No,
        )
        if reply == QMessageBox.StandardButton.Yes:
            self.approve_requested.emit()

    def _on_reject_clicked(self) -> None:
        reply = QMessageBox.question(
            self,
            "Confirm Reject",
            "Reject this production request?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
            QMessageBox.StandardButton.No,
        )
        if reply == QMessageBox.StandardButton.Yes:
            self.reject_requested.emit()

    def _on_deactivate_clicked(self) -> None:
        reply = QMessageBox.question(
            self,
            "Confirm Deactivate",
            "Deactivate this request? It will no longer appear in active listings.",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
            QMessageBox.StandardButton.No,
        )
        if reply == QMessageBox.StandardButton.Yes:
            self.deactivate_requested.emit()
