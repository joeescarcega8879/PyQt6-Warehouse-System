from src.config.logger_config import logger

from src.domain.permissions import Permission
from src.domain.audit_service import AuditService
from src.domain.audit_definitions import AuditDefinition
from src.domain.permissions_service import PermissionService

from src.models.production_line_model import ProductionLineModel
from src.presenters.base_presenter import BasePresenter


class LinePresenter(BasePresenter):
    def __init__(self, view, status_handler, current_user):
        super().__init__(view, status_handler, current_user)

        self._connect_signals()
        self._load_user_information_to_view()
        self._load_lines_data()

    def _connect_signals(self) -> None:
        self.view.save_requested.connect(self._handle_save)
        self.view.edit_requested.connect(self._handle_edit)
        self.view.search_text_changed.connect(self._on_search_text_changed)

    def _handle_save(self) -> None:
        data = self.view.get_line_form_data() or {}

        error = self._validate(data)
        if error:
            self._emit_error(error)
            return

        name = data.get("name", "").strip()
        description = (data.get("description") or "").strip()
        is_active = data.get("is_active", True)

        try:
            if self._is_editing:
                if self._current_entity_id is None:
                    self._emit_error("Please select a valid production line to edit")
                    return

                if not PermissionService.has_permission(self.current_user, Permission.PRODUCTION_LINES_EDIT):
                    self._emit_error("You do not have permission to edit production lines")
                    AuditService.log_action(
                        user_id=self.current_user.user_id,
                        action=AuditDefinition.PRODUCTION_LINES_EDITED,
                        success=False,
                        entity="ProductionLine",
                        meta={"reason": "Insufficient permissions"}
                    )
                    return

                success = ProductionLineModel.update_production_line(
                    line_id=self._current_entity_id,
                    line_name=name,
                    description=description,
                    is_active=is_active
                )

                if success:
                    AuditService.log_action(
                        user_id=self.current_user.user_id,
                        action=AuditDefinition.PRODUCTION_LINES_EDITED,
                        success=True,
                        entity="ProductionLine",
                        entity_id=self._current_entity_id,
                        meta={"name": name, "is_active": is_active}
                    )
                    self._emit_success("Production line updated successfully")
                    self._post_save_cleanup()
                else:
                    self._emit_error("Failed to update production line")

            else:
                if not PermissionService.has_permission(self.current_user, Permission.PRODUCTION_LINES_CREATE):
                    self._emit_error("You do not have permission to create production lines")
                    AuditService.log_action(
                        user_id=self.current_user.user_id,
                        action=AuditDefinition.PRODUCTION_LINES_CREATED,
                        success=False,
                        entity="ProductionLine",
                        meta={"reason": "Insufficient permissions"}
                    )
                    return

                success = ProductionLineModel.add_production_line(name=name, description=description, is_active=is_active)

                if success:
                    AuditService.log_action(
                        user_id=self.current_user.user_id,
                        action=AuditDefinition.PRODUCTION_LINES_CREATED,
                        success=True,
                        entity="ProductionLine",
                        meta={"name": name, "is_active": is_active}
                    )
                    self._emit_success("Production line created successfully")
                    self._post_save_cleanup()
                else:
                    self._emit_error("Failed to create production line")

        except Exception as e:
            logger.error(f"Error saving production line: {e}")
            self._emit_error(f"Error saving production line: {str(e)}")

    def _handle_edit(self) -> None:
        data = self.view.get_selected_line_data()
        if not data or data.get("id") is None:
            self._emit_error("Please select a valid production line to edit")
            return

        self._enter_edit_mode(data["id"])
        self.view.set_form_data(data)

    def _on_search_text_changed(self, text: str) -> None:
        self._handle_search_with_id_and_name(
            query=text,
            search_by_id_func=lambda id: ProductionLineModel.search_by_id(id),
            search_by_name_func=lambda name: ProductionLineModel.search_by_name(name),
            load_all_func=self._load_lines_data,
            load_results_func=self.view.load_lines_data,
            entity_name="production line"
        )

    def _post_save_cleanup(self) -> None:
        self._exit_edit_mode()
        self.view.clean_form()
        self._load_lines_data()

    def _load_lines_data(self) -> None:
        lines_data = ProductionLineModel.get_all_production_lines()
        self.view.load_lines_data(lines_data)

    def _validate(self, data: dict) -> str | None:
        name = (data.get("name") or "").strip()
        is_active = data.get("is_active")

        if not name:
            return "Line name is required"
        if is_active is None:
            return "Is active status of line is required"

        return None
