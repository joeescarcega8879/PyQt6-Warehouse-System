from config.logger_config import logger
from common.enums import StatusType

from domain.permissions import Permission
from domain.audit_service import AuditService
from domain.audit_definitions import AuditDefinition
from domain.permissions_service import PermissionService

from models.supplier_receipt_model import SupplierReceiptModel

class SupplierReceiptPresenter:
    def __init__(self, view, main_app ,status_handler, current_user):
        self.view = view
        self.main_app = main_app
        self.status_handler = status_handler
        self.current_user = current_user

        self._is_editing = False
        self._current_receipt_id: int | None = None
        self._selected_material: dict | None = None

        self._connect_signals()
        self._load_user_information()
        self._load_receipts_data()

    def _connect_signals(self) -> None:
        self.view.material_selected.connect(self._handle_select_material)
        self.view.save_requested.connect(self._handle_save)
      
   
    def _handle_save(self) -> None: 
        data = self.view.get_receipt_form_data() or {}

        print("Receipt form data:", data)  # Debugging line
    
    def _load_user_information(self) -> None:
        user_info = {
            "user_id": self.current_user.user_id,
            "user_role": self.current_user.user_role
        }

        self.view.load_user_information(user_info)

    def _load_receipts_data(self) -> None:
        pass

    def _handle_select_material(self) -> None:

        if not PermissionService.has_permission(self.current_user, Permission.RECEIPTS_CREATE):
            self._emit_error("You do not have permission to select materials for receipts")
            AuditService.log_action(
                user_id=self.current_user.user_id,
                action=AuditDefinition.RECEIPTS_CREATED,
                success=False,
                meta={"reason": "Insufficient permissions"}
            )
            return
        
        self.main_app.open_generic_form(on_material_selected=self._on_material_selected)

    def _on_material_selected(self, material: dict) -> None:

        # Save matierial selected
        self._selected_material = material

        self.view.display_selected_material(material)

        material_name = material.get("material_name", "")
        self._emit_success(f"Material '{material_name}' selected successfully")

    def _emit_error(self, message: str) -> None:
        self.status_handler(message, 3000, StatusType.ERROR)

    def _emit_success(self, message: str) -> None:
        self.status_handler(message, 3000, StatusType.SUCCESS)
