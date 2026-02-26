import os
from PyQt6 import uic
from PyQt6.QtWidgets import QDialog
from PyQt6.QtCore import pyqtSignal

from common.format import FormatComponents

class GenericView(QDialog):

    material_selected = pyqtSignal(dict)
    search_text_changed = pyqtSignal(str)
    material_double_clicked = pyqtSignal(int, int)

    def __init__(self):
        super(GenericView, self).__init__()

        # Initialize components
        self.initialize_components()

    def initialize_components(self):
        # Load ui path
        ui_path = os.path.join(os.path.dirname(__file__), "..", "ui", "generic_view.ui")
        # Load ui
        uic.loadUi(ui_path, self)

        self.input_search.textChanged.connect(self.on_search_text_changed)

        self.tableWidget.cellDoubleClicked.connect(self._on_material_double_clicked)

    def load_materials(self, materials: list) -> None:
        headers = ["ID", "Name", "Description", "Unit"]
        FormatComponents.format_qtablewidget(self.tableWidget, headers, materials)

    def get_selected_material(self) -> dict | None:
        current_row = self.tableWidget.currentRow()

        if current_row == -1:
            return None 
        
        # Extract material data from the selected row
        return {
            "id": self.tableWidget.item(current_row, 0).text(),
            "material_name": self.tableWidget.item(current_row, 1).text(),
            "description": self.tableWidget.item(current_row, 2).text(),
            "unit": self.tableWidget.item(current_row, 3).text(),
        }
        
    def get_button_box(self):
         return self.buttonBox
    
    def on_search_text_changed(self, text: str) -> None:
        self.search_text_changed.emit(text)

    def get_material_from_row(self, row: int) -> dict | None :

        # Validate row index
        if row < 0 or row >= self.tableWidget.rowCount():
            return None 
        
        # Validate all columns have data
        if not all(self.tableWidget.item(row, col) for col in range(4)):
            return None
        
        # Extract material data from the selected row
        return {
            "id": self.tableWidget.item(row, 0).text(),
            "material_name": self.tableWidget.item(row, 1).text(),
            "description": self.tableWidget.item(row, 2).text(),
            "unit": self.tableWidget.item(row, 3).text(),
        }
        
    def _on_material_double_clicked(self, row: int, column: int) -> None:
        
        self.material_double_clicked.emit(row, column)
    