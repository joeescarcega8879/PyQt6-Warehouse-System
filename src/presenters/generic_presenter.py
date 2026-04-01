from src.presenters.base_presenter import BasePresenter
from src.config.logger_config import logger
from src.common.enums import StatusType
from src.common.entity_config import EntityType, ModelConfig
from src.common.model_adapter import ModelAdapter

class GenericPresenter(BasePresenter):

    def __init__(self, view, entity_type: str | EntityType = "material", status_handler=None):
        """
        Initializes the generic presenter.
        
        Args:
            view: GenericView instance
            entity_type: Entity type ("material", "supplier", "production_line") or EntityType
            status_handler: Callback to display status messages
        """
        super().__init__(view, status_handler, current_user=None)

        # Resolve entity_type
        if isinstance(entity_type, str):
            self.entity_type = EntityType.from_string(entity_type)
        else:
            self.entity_type = entity_type

        self.config: ModelConfig = self.entity_type.value
        self.model_adapter = ModelAdapter(self.config)

        self._load_all_data()
        self._connect_signals()
    
    def _connect_signals(self):
        self.view.get_button_box().accepted.connect(self._handle_add)
        self.view.get_button_box().rejected.connect(self._handle_cancel)
        self.view.search_text_changed.connect(self._on_search_text_changed)
        self.view.item_double_clicked.connect(self._handle_double_click)


    def _handle_add(self):
        """Handles the accept/add selection event."""
        selected_item = self.view.get_selected_item()

        if not selected_item:
            self._emit_error(f"No {self.config.display_name.lower()} seleccionado")
            return
        
        # Emit both signals for compatibility
        self.view.item_selected.emit(selected_item)
        self.view.material_selected.emit(selected_item)  # Legacy
        self.view.accept()

    def _on_search_text_changed(self, text: str) -> None:
        """
        Handles changes in the search text.
        Searches by ID if numeric, by name if it has enough characters.
        """
        query = (text or "").strip()

        if not query:
            self._load_all_data()
            return
        
        # If the query is a number, search by ID first
        if query.isdigit():
            try:
                results = self.model_adapter.search_by_id(int(query))
                self.view.load_data(results)
            except Exception:
                logger.exception(f"Error searching {self.config.name} by id")
                self._emit_error("Error inesperado durante la búsqueda")
            return
        
        # Validate minimum length for name search
        if len(query) < self.config.min_search_length:
            return
        
        # For longer queries, search by name
        try:
            results = self.model_adapter.search_by_name(query)
            self.view.load_data(results)
        except Exception:
            logger.exception(f"Error searching {self.config.name} by name")
            self._emit_error("Error inesperado durante la búsqueda")
     
    def _handle_double_click(self, row: int, column: int) -> None:
        """Handles the double-click event on a row."""
        item = self.view.get_item_from_row(row)

        if not item:
            self._emit_error(f"{self.config.display_name} inválido")
            return
        
        # Emit both signals for compatibility
        self.view.item_selected.emit(item)
        self.view.material_selected.emit(item)  # Legacy
        self.view.accept()
    
    def _handle_cancel(self):
        """Handles the cancel event."""
        self.view.reject()

    def _load_all_data(self):
        """Loads all data for the configured entity."""
        try:
            data = self.model_adapter.get_all()
            self.view.load_data(data)
        except Exception:
            logger.exception(f"Error loading all {self.config.name} data")
            self._emit_error(f"Error al cargar {self.config.display_name}s")
    
    # Legacy method for compatibility
    def _load_list_materials(self):
        """Legacy method. Use _load_all_data() instead."""
        self._load_all_data()

    def _emit_error(self, message: str) -> None:
        """Emits an error message."""
        if self.status_handler:
            self.status_handler(message, 3000, StatusType.ERROR)
    
    def _emit_success(self, message: str) -> None:
        """Emits a success message."""
        if self.status_handler:
            self.status_handler(message, 3000, StatusType.SUCCESS)
        