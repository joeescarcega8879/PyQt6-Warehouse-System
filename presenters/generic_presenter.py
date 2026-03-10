from models.material_model import MaterialModel
from presenters.base_presenter import BasePresenter


class GenericPresenter(BasePresenter):

    def __init__(self, view, status_handler):
        super().__init__(view, status_handler, current_user=None)

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
        self._handle_search_with_id_and_name(
            query=text,
            search_by_id_func=MaterialModel.search_by_id,
            search_by_name_func=MaterialModel.search_by_name,
            load_all_func=self._load_list_materials,
            load_results_func=self.view.load_materials,
            min_name_length=3,
            entity_name="materials"
        )
     
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
        