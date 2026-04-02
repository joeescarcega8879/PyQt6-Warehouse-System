from src.config.logger_config import logger
from src.models.material_model import MaterialModel
from src.presenters.base_presenter import BasePresenter

from src.domain.permissions import Permission
from src.domain.permissions_service import PermissionService
from src.domain.audit_service import AuditService
from src.domain.audit_definitions import AuditDefinition

class MaterialPresenter(BasePresenter):
    def __init__(self, view, status_handler, current_user):
        super().__init__(view, status_handler, current_user)

        self._connect_signals()
        self._load_init_data()
        self._load_user_information_to_view()

    def _connect_signals(self) -> None:
        self.view.save_requested.connect(self._handle_save)
        self.view.edit_requested.connect(self._handle_edit)
        self.view.delete_requested.connect(self._handle_delete)
        self.view.search_text_changed.connect(self._on_search_text_changed)

    def _handle_save(self) -> None:
        data = self.view.get_material_form_data() or {}

        error = self._validate(data)
        if error:
            self._emit_error(error)
            return

        name = data.get("name", "").strip()
        unit = data.get("unit", "").strip()
        description = (data.get("description") or "").strip()

        try:
            if self._is_editing:
                if self._current_entity_id is None:
                    self._emit_error("Please select a valid material to edit")
                    return
                
                if not PermissionService.has_permission(self.current_user, Permission.MATERIALS_EDIT):
                    self._emit_error("You do not have permission to edit materials")
                    AuditService.log_action(
                        user_id=self.current_user.user_id,
                        action=AuditDefinition.MATERIALS_EDITED,
                        success=False,
                        entity="Material",
                        meta={"reason": "Insufficient permissions"}
                    )
                    return

                success = MaterialModel.update_material(
                    material_id=self._current_entity_id,
                    name=name,
                    description=description,
                    unit=unit,
                )
                
                if success:
                    AuditService.log_action(
                        user_id=self.current_user.user_id,
                        action=AuditDefinition.MATERIALS_EDITED,
                        success=True,
                        entity="Material",
                        entity_id=self._current_entity_id,
                        meta={"name": name, "unit": unit, "description": description}
                    )

                    self._emit_success("Material updated successfully")
                    self._post_save_cleanup()
                else:
                    self._emit_error("Error updating material")
                    
            else:

                if not PermissionService.has_permission(self.current_user, Permission.MATERIALS_CREATE):
                    self._emit_error("You do not have permission to add materials")
                    AuditService.log_action(
                        user_id=self.current_user.user_id,
                        action=AuditDefinition.MATERIALS_CREATED,
                        success=False,
                        entity="Material",
                        meta={"reason": "Insufficient permissions"}
                    )
                    return
                
                success = MaterialModel.add_material(
                    name=name,
                    description=description,
                    unit=unit,
                )

                if success:
                    AuditService.log_action(
                        user_id=self.current_user.user_id,
                        action=AuditDefinition.MATERIALS_CREATED,
                        success=True,
                        entity="Material",
                        meta={"name": name, "unit": unit, "description": description}
                    )

                    self._emit_success("Material created successfully")
                    self._post_save_cleanup()
                else:
                    self._emit_error("Error creating material")

        except Exception:
            logger.exception("Error saving material")
            self._emit_error("Unexpected error")

    def _handle_edit(self) -> None:
        data = self.view.get_selected_material_data()
        if not data or data.get("id") is None:
            self._emit_error("Please select a valid material to edit")
            return

        self._enter_edit_mode(data["id"])
        self.view.set_form_data(data)

    def _handle_delete(self) -> None:
        material_id = self.view.get_selected_material_id()
        if material_id is None:
            self._emit_error("Please select a valid material to delete")
            return
        
        if not PermissionService.has_permission(self.current_user, Permission.MATERIALS_DELETE):
            self._emit_error("You do not have permission to delete materials")
            AuditService.log_action(
                user_id=self.current_user.user_id,
                action=AuditDefinition.MATERIALS_DELETED,
                success=False,
                entity="Material",
                meta={"reason": "Insufficient permissions"}
            )
            return

        try:
            success = MaterialModel.delete_material(material_id)
            if success:
                self._emit_success("Material deleted successfully")

                AuditService.log_action(
                    user_id=self.current_user.user_id,
                    action=AuditDefinition.MATERIALS_DELETED,
                    success=True,
                    entity="Material",
                    entity_id=material_id,
                    meta={"Deleted by": self.current_user.username}
                )

                self._post_save_cleanup()
            else:
                self._emit_error("Error deleting material")

        except Exception:
            logger.exception("Error deleting material")
            self._emit_error("Unexpected error")

    def _on_search_text_changed(self, text: str) -> None:
        self._handle_search_with_id_and_name(
            query=text,
            search_by_id_func=MaterialModel.search_by_id,
            search_by_name_func=MaterialModel.search_by_name,
            load_all_func=self._reload_materials,
            load_results_func=self.view.load_materials,
            min_name_length=3,
            entity_name="materials"
        )

    def _validate(self, data: dict) -> str | None:
        name = (data.get("name") or "").strip()
        unit = (data.get("unit") or "").strip()
        
        error = self._validate_required_field(name, "Material name")
        if error:
            return error
        
        error = self._validate_required_field(unit, "Unit of measure")
        if error:
            return error
        
        return None

    def _post_save_cleanup(self) -> None:
        self._clear_form_and_reset_state()
        self._reload_materials()

    def _reload_materials(self) -> None:
        materials = MaterialModel.get_all_materials()
        self.view.load_materials(materials)

    def _load_init_data(self) -> None:
        self._reload_materials()

