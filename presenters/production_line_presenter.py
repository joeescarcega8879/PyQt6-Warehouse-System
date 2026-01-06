from os import name
from config.logger_config import logger
from common.enums import StatusType

from domain.permissions import Permission
from domain.audit_service import AuditService
from domain.audit_definitions import AuditDefinition
from domain.permissions_service import PermissionService

from models.production_line_model import ProductionLineModel

class LinePresenter:
    def __init__(self, view, status_handler, current_user):
        self.view = view
        self.status_handler = status_handler
        self.current_user = current_user

        self._is_editing = False
        self._current_line_id: int | None = None

        self._connect_signals()
        self._load_user_information()
        self._load_lines_data()

    def _connect_signals(self) -> None:
            self.view.save_requested.connect(self._handle_save)

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
                if self._current_line_id is None:
                    self._emit_error("Please select a valid production line to edit")
                    return
                
                if not PermissionService.has_permission(self.current_user, Permission.PRODUCTION_LINES_EDIT):
                    self._emit_error("You do not have permission to edit production lines")

                    AuditService.log_action(user_id=self.current_user.user_id,action=AuditDefinition.PRODUCTION_LINES_EDITED,success=False,entity="ProductionLine",meta={"reason": "Insufficient permissions"})
                    return
                
                success = ProductionLineModel.update_production_line(line_id=self._current_line_id,name=name,description=description,is_active=is_active)

            else:
                if not PermissionService.has_permission(self.current_user, Permission.PRODUCTION_LINES_CREATE):
                    self._emit_error("You do not have permission to create production lines")

                    AuditService.log_action(user_id=self.current_user.user_id,action=AuditDefinition.PRODUCTION_LINES_CREATED,success=True,entity="ProductionLine")
                    return
                success = ProductionLineModel.add_production_line(name=name, description=description, is_active=is_active)

            if success:
                AuditService.log_action(
                    user_id=self.current_user.user_id, 
                    action=AuditDefinition.PRODUCTION_LINES_CREATED, 
                    success=True, 
                    entity="ProductionLine", 
                    entity_id=self._current_line_id if self._current_line_id is not None else None
                )

                self._emit_success("Production line saved successfully")
                self._post_save_cleanup()

            else:
                self._emit_error("Failed to save production line")

        except Exception as e:
            logger.error(f"Error saving production line: {e}")
            self._emit_error(f"Error saving production line: {str(e)}")

    def _post_save_cleanup(self)-> None:
        self._is_editing = False
        self._current_line_id = None
        self.view.clean_form()
        self._load_lines_data()

    def _load_lines_data(self)-> None:
        lines_data = ProductionLineModel.get_all_production_lines()
        self.view.load_lines_data(lines_data)

    def _load_user_information(self)-> None:
        user_info = {
            "username": self.current_user.username,
            "user_role": self.current_user.user_role
        }
        self.view.load_user_information(user_info)

    def _validate(self, data: dict) -> str | None:
        name = (data.get("name") or "").strip()
        is_active = (data.get("is_active") or "")


        if not name:
            return "Line name is required"
        if not is_active:
            return "Unit of measure is required"

        return None

    def _emit_error(self, message: str)-> None:
         self.status_handler(message, 3000, StatusType.ERROR)

    def _emit_success(self, message: str)-> None:
         self.status_handler(message, 3000, StatusType.SUCCESS)