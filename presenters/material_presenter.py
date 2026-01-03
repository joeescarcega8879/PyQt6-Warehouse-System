import logging
from re import A
from common.enums import StatusType
from models.material_model import MaterialModel

from domain.permissions import Permission
from domain.permissions_service import PermissionService
from domain.audit_service import AuditService
from domain.audit_definitions import AuditDefinition

class MaterialPresenter:
    def __init__(self, view, status_handler, current_user):
        self.view = view
        self.status_handler = status_handler
        self.current_user = current_user

        self._is_editing = False
        self._current_material_id: int | None = None

        self._connect_signals()
        self._load_init_data()
        self._load_user_information()

    def _connect_signals(self) -> None:
        self.view.save_requested.connect(self._handle_save)
        self.view.edit_requested.connect(self._handle_edit)
        self.view.delete_requested.connect(self._handle_delete)
        self.view.search_text_changed.connect(self.on_search_text_changed)

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
                if self._current_material_id is None:
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
                    material_id=self._current_material_id,
                    name=name,
                    description=description,
                    unit=unit,
                )
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
                self._emit_success("Material saved successfully")

                AuditService.log_action(
                    user_id=self.current_user.user_id,
                    action=AuditDefinition.MATERIALS_CREATED,
                    success=True,
                    entity="Material",
                    entity_id=self._current_material_id,
                    meta={"name": name, "unit": unit, "description": description}
                )

                self._post_save_cleanup()
            else:
                self._emit_error("Error saving material")

        except Exception:
            logging.exception("Error saving material")
            self._emit_error("Unexpected error")

    def _handle_edit(self) -> None:
        data = self.view.get_selected_material_data()
        if not data or data.get("id") is None:
            self._emit_error("Please select a valid material to edit")
            return

        self._is_editing = True
        self._current_material_id = data["id"]
        self.view.set_form_data(data)

    def _handle_delete(self) -> None:
        material_id = self.view.get_selected_material_id()
        if material_id is None:
            self._emit_error("Please select a valid material to delete")
            return
        
        if not PermissionService.has_permission(self.current_user, Permission.DELETE_MATERIAL):
            self._emit_error("You do not have permission to delete materials")
            AuditService.log_action(
                user_id=self.current_user.id,
                action=Permission.DELETE_MATERIAL,
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
            logging.exception("Error deleting material")
            self._emit_error("Unexpected error")

    def on_search_text_changed(self, text: str) -> None:
        query = (text or "").strip()

        if not query:
            self._reload_materials()
            return

        # Para ID permitimos cualquier longitud si son dígitos.
        if query.isdigit():
            try:
                materials = MaterialModel.search_by_id(int(query))
                self.view.load_materials(materials)
            except Exception:
                logging.exception("Error searching materials by id")
                self._emit_error("Unexpected error during search")
            return

        # Para nombre, aplica umbral mínimo (como ya hacías).
        if len(query) < 3:
            return

        try:
            materials = MaterialModel.search_by_name(query)
            self.view.load_materials(materials)
        except Exception:
            logging.exception("Error searching materials by name")
            self._emit_error("Unexpected error during search")

    def _validate(self, data: dict) -> str | None:
        name = (data.get("name") or "").strip()
        unit = (data.get("unit") or "").strip()

        if not name:
            return "Material name is required"
        if not unit:
            return "Unit of measure is required"

        return None

    def _post_save_cleanup(self) -> None:
        self._is_editing = False
        self._current_material_id = None
        self.view.clear_form()
        self._reload_materials()

    def _reload_materials(self) -> None:
        materials = MaterialModel.get_all_materials()
        self.view.load_materials(materials)

    def _load_init_data(self) -> None:
        self._reload_materials()

    def _load_user_information(self) -> None:
        user_info = {
            "username": self.current_user.username,
            "user_role": self.current_user.user_role,
        }
        self.view.load_user_information(user_info)

    def _emit_error(self, message: str) -> None:
        self.status_handler(message, 3000, StatusType.ERROR)

    def _emit_success(self, message: str) -> None:
        self.status_handler(message, 3000, StatusType.SUCCESS)

