from config.logger_config import logger

from common.enums import StatusType

from models.supplier_model import SupplierModel

from domain.audit_service import AuditService
from domain.audit_definitions import AuditDefinition
from domain.permissions import Permission
from domain.permissions_service import PermissionService


class SupplierPresenter:
    def __init__(self, view, main_app, status_handler, current_user):
        self.view = view
        self.main_app = main_app
        self.status_handler = status_handler
        self.current_user = current_user
        
        self._is_editing = False
        self._current_supplier_id: int | None = None

        self._connect_signals()
        self._load_suppliers()
        self._load_user_information()

    def _connect_signals(self) -> None:
        self.view.save_requested.connect(self._handle_save)
    
    def _handle_save(self) -> None:
        
        data  = self.view.get_supplier_form_data() or {}
        error = self._validate(data)
        
        if error:
            self._emit_error(error)
            return
        
        supplier_name = data.get("supplier_name", "").strip()
        contact_department = data.get("contact_department", "").strip()
        phone = data.get("phone", "").strip()
        email = data.get("email", "").strip()
        address = data.get("address", "").strip()
        is_active = data.get("is_active", True)
        notes = data.get("notes", "").strip()
        
        
    def _load_suppliers(self) -> None:
        suppliers = SupplierModel.get_all_suppliers()
        self.view.load_suppliers(suppliers)

    def _load_user_information(self) -> None:
        user_info = {
            "username": self.current_user.username,
            "user_role": self.current_user.user_role
        }
        self.view.load_user_information(user_info)
    
    def _validate(self, data: dict) -> str | None:
        supplier_name = (data.get("supplier_name") or "").strip()
        contact_department = (data.get("contact_department") or "").strip()
        
        if not supplier_name:
            return "Supplier name is required"
        if not contact_department:
            return "Contact department is required"
        
        return None
    
    def _emit_error(self, message: str) -> None:
        self.status_handler(message, 3000, StatusType.ERROR)

    def _emit_success(self, message: str) -> None:
        self.status_handler(message, 3000, StatusType.SUCCESS)

