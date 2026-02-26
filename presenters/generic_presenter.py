import logging

from models.material_model import MaterialModel

from common.styles import StatusType

class GenericPresenter:

    def __init__(self, view, status_handler):
        self.view = view
        self.status_handler = status_handler

        self._load_list_materials()
        self._connect_signals()
    
    def _connect_signals(self):
        self.view.get_button_box().accepted.connect(self._handle_add)
        self.view.get_button_box().rejected.connect(self._handle_cancel)
        self.view.search_text_changed.connect(self._on_search_text_changed)
        self.view.material_double_clicked.connect(self._handle_double_click)


    def _handle_add(self):
        selected_material = self.view.get_selected_material()

        if not selected_material:
            self._emit_error("No material selected")
            return
        
        self.view.material_selected.emit(selected_material)
        self.view.accept()

    def _on_search_text_changed(self, text: str) -> None:
        
        query = (text or "").strip()

        if not query:
            self._load_list_materials()
            return
        
        # If the query is a number, search by ID first
        if query.isdigit():
            try:
                materials = MaterialModel.search_by_id(int(query))
                self.view.load_materials(materials)
            except Exception:
                logging.exception("Error searching materials by id")
                self._emit_error("Unexpected error during search")
            return
        
        if len(query) < 3:
            return
        
        # For longer queries, search by name
        try:
            materials = MaterialModel.search_by_name(query)
            self.view.load_materials(materials)
        except Exception:
            logging.exception("Error searching materials by name")
            self._emit_error("Unexpected error during search")
     
    def _handle_double_click(self, row: int, column: int) -> None:
        
        material = self.view.get_material_from_row(row)

        if not material:
            self._emit_error("Invalid material selected")
            return
        
        self.view.material_selected.emit(material)
        self.view.accept()
    
    def _handle_cancel(self):
        self.view.reject()

    def _load_list_materials(self):
        materials = MaterialModel.get_all_materials()
        self.view.load_materials(materials)

    def _emit_error(self, message: str) -> None:
        self.status_handler(message, 3000, StatusType.ERROR)
    
    def _emit_success(self, message: str) -> None:
        self.status_handler(message, 3000, StatusType.SUCCESS)
        