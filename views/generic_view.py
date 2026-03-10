import os
from PyQt6 import uic
from PyQt6.QtWidgets import QDialog
from PyQt6.QtCore import pyqtSignal

from common.format import FormatComponents
from common.entity_config import EntityType, ModelConfig

class GenericView(QDialog):

    # Generic signals
    item_selected = pyqtSignal(dict)
    search_text_changed = pyqtSignal(str)
    item_double_clicked = pyqtSignal(int, int)
    
    # Legacy signals (for backward compatibility)
    material_selected = pyqtSignal(dict)
    material_double_clicked = pyqtSignal(int, int)

    def __init__(self, entity_type: str | EntityType = "material"):
        """
        Initializes the generic view for selecting an entity.
        
        Args:
            entity_type: Type of entity to display. Can be:
                        - A string: "material", "supplier", "production_line"
                        - An EntityType enum directly
        """
        super(GenericView, self).__init__()
        
        # Resolve entity_type
        if isinstance(entity_type, str):
            self.entity_type = EntityType.from_string(entity_type)
        else:
            self.entity_type = entity_type
        
        self.config: ModelConfig = self.entity_type.value

        # Initialize components
        self.initialize_components()
        
        # Configure window based on entity
        self.setWindowTitle(f"Seleccionar {self.config.display_name}")

    def initialize_components(self):
        # Load ui path
        ui_path = os.path.join(os.path.dirname(__file__), "..", "ui", "generic_view.ui")
        # Load ui
        uic.loadUi(ui_path, self)

        self.input_search.textChanged.connect(self.on_search_text_changed)

        self.tableWidget.cellDoubleClicked.connect(self._on_item_double_clicked)

    def load_data(self, data: list[tuple]) -> None:
        """
        Loads data into the table using the entity configuration.
        
        Args:
            data: List of tuples with the data to display
        """
        FormatComponents.format_qtablewidget(
            self.tableWidget, 
            self.config.column_headers, 
            data
        )
    
    # Legacy method for compatibility
    def load_materials(self, materials: list) -> None:
        """Legacy method. Use load_data() instead."""
        self.load_data(materials)

    def get_selected_item(self) -> dict | None:
        """
        Gets the selected item from the table as a dictionary.
        Keys are generated dynamically based on column headers.
        
        Returns:
            Dictionary with selected item data, or None if no selection
        """
        current_row = self.tableWidget.currentRow()

        if current_row == -1:
            return None 
        
        # Extract data dynamically based on column_count
        item_data = {}
        for col in range(self.config.column_count):
            cell = self.tableWidget.item(current_row, col)
            if cell:
                # Use header as key (convert to snake_case)
                header = self.config.column_headers[col].lower().replace(" ", "_").replace("ó", "o").replace("í", "i")
                item_data[header] = cell.text()
        
        return item_data
    
    # Legacy method for compatibility
    def get_selected_material(self) -> dict | None:
        """Legacy method. Use get_selected_item() instead."""
        return self.get_selected_item()
        
    def get_button_box(self):
         return self.buttonBox
    
    def on_search_text_changed(self, text: str) -> None:
        self.search_text_changed.emit(text)

    def get_item_from_row(self, row: int) -> dict | None:
        """
        Gets item data from a specific row.
        
        Args:
            row: Row index
        
        Returns:
            Dictionary with item data, or None if row is invalid
        """
        # Validate row index
        if row < 0 or row >= self.tableWidget.rowCount():
            return None 
        
        # Validate all columns have data
        if not all(self.tableWidget.item(row, col) for col in range(self.config.column_count)):
            return None
        
        # Extract data from the row
        item_data = {}
        for col in range(self.config.column_count):
            cell = self.tableWidget.item(row, col)
            if cell:
                # Use header as key (convert to snake_case)
                header = self.config.column_headers[col].lower().replace(" ", "_").replace("ó", "o").replace("í", "i")
                item_data[header] = cell.text()
        
        return item_data
    
    # Legacy method for compatibility
    def get_material_from_row(self, row: int) -> dict | None:
        """Legacy method. Use get_item_from_row() instead."""
        return self.get_item_from_row(row)
        
    def _on_item_double_clicked(self, row: int, column: int) -> None:
        """
        Handler for double-click on a table cell.
        Emits both signals (generic and legacy) for compatibility.
        """
        self.item_double_clicked.emit(row, column)
        self.material_double_clicked.emit(row, column)  # Legacy compatibility
    