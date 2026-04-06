from src.config.logger_config import logger

from src.domain.permissions import Permission
from src.domain.audit_service import AuditService
from src.domain.audit_definitions import AuditDefinition
from src.domain.permissions_service import PermissionService

from src.models.production_request_model import ProductionRequestModel
from src.presenters.base_presenter import BasePresenter

class ProductionRequestPresenter(BasePresenter):
    
    def __init__(self, view, main_app, status_handler, current_user):
        super().__init__(view, status_handler, current_user, main_app=main_app)
        
        self._selected_material: dict | None = None
        self._selected_line: dict | None = None
        
        self._connect_signals()
        
        
    def _connect_signals(self):
        self.view.selected_material.connect(self._handling_selected_material)
        self.view.selected_line.connect(self._handling_selected_line)
        self.view.add_item_requested.connect(self._on_add_item_requested)
        
    def _on_add_item_requested(self):
        if not PermissionService.has_permission(self.current_user, Permission.PRODUCTION_REQUESTS_CREATE):
            self._emit_error("You do not have permission to add items to production requests.")
            
            AuditService.log_action(
                user_id=self.current_user.id,
                action=AuditDefinition.PRODUCTION_REQUESTS_DENIED,
                success=False,
                meta={"reason": "Insufficient permissions to add items to production requests."}
            )
            return
        
        data = self.view.get_selected_material_and_line_info()

        if not data.get("material_id") or not data.get("line_id") or not data.get("quantity"):
            self._emit_error("Please select a material, a production line, and enter a quantity before adding an item.")
            return
        
        self.view.display_added_item(data)
        self._clear_form()
    
    def _clear_form(self) -> None:
        self._selected_material = None
        self._selected_line = None
        self.view.clear_form()
    
    def _handling_selected_material(self) -> None:
        if not PermissionService.has_permission(self.current_user, Permission.PRODUCTION_REQUESTS_CREATE):
            self._emit_error("You do not have permission to select materials for production requests.")
            
            AuditService.log_action(
                user_id=self.current_user.id,
                action=AuditDefinition.PRODUCTION_REQUESTS_DENIED,
                success=False,
                meta={"reason": "Insufficient permissions to select materials for production requests."}
            )
            return
        
        self.main_app.open_generic_form(entity_type="material", on_item_selected=self._on_selected_material)
    
    def _handling_selected_line(self) -> None:
        if not PermissionService.has_permission(self.current_user, Permission.PRODUCTION_REQUESTS_CREATE):
            self._emit_error("You do not have permission to select production lines for production requests.")
            
            AuditService.log_action(
                user_id=self.current_user.id,
                action=AuditDefinition.PRODUCTION_REQUESTS_DENIED,
                success=False,
                meta={"reason": "Insufficient permissions to select production lines for production requests."}
            )    
            return
        
        self.main_app.open_generic_form(entity_type="production_line", on_item_selected=self._on_selected_line)
        
    def _on_selected_material(self, material: dict) -> None:
        self.view.display_selected_material(material)
        
    def _on_selected_line(self, line: dict) -> None:
        self.view.display_selected_line(line)