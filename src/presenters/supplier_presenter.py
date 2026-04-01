from src.config.logger_config import logger
from src.common.enums import StatusType
from src.models.supplier_model import SupplierModel

from src.domain.audit_service import AuditService
from src.domain.audit_definitions import AuditDefinition
from src.domain.permissions import Permission
from src.domain.permissions_service import PermissionService


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
        self.view.edit_requested.connect(self._handle_edit)
        self.view.search_text_changed.connect(self._on_search_text_changed)
        self.view.cancel_requested.connect(self._handle_cancel)
    
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
        
        try:
            if self._is_editing:
                if self._current_supplier_id is None:
                    self._emit_error("Please select a valid supplier to edit")
                    return
                
                if not PermissionService.has_permission(self.current_user, Permission.SUPPLIER_EDIT):
                    self._emit_error("You do not have permission to edit suppliers")
                    AuditService.log_action(
                        user_id=self.current_user.user_id,
                        action=AuditDefinition.SUPPLIER_EDITED,
                        success=False,
                        entity="Supplier",
                        meta={"reason": "Insufficient permissions"}
                    )
                    return
            
                success = SupplierModel.update_supplier(
                    supplier_id=self._current_supplier_id,
                    supplier_name=supplier_name,
                    contact_department=contact_department,
                    phone=phone,
                    email=email,
                    address=address,
                    is_active=is_active,
                    notes=notes
                )
                
                if success:
                    AuditService.log_action(
                        user_id=self.current_user.user_id,
                        action=AuditDefinition.SUPPLIER_EDITED,
                        success=True,
                        entity="Supplier",
                        meta={"supplier_id": self._current_supplier_id, "supplier_name": supplier_name}
                    )
                    
                    self._emit_success("Supplier updated successfully")
                    self._post_save_cleanup()
                else:
                    self._emit_error("Failed to update supplier") 
            else:
                if not PermissionService.has_permission(self.current_user, Permission.SUPPLIER_CREATE):
                    self._emit_error("You do not have permission to add suppliers")
                    AuditService.log_action(
                        user_id=self.current_user.user_id,
                        action=AuditDefinition.SUPPLIER_CREATED,
                        success=False,
                        entity="Supplier",
                        meta={"reason": "Insufficient permissions"}
                    )
                    return
                
                result = SupplierModel.add_supplier(
                    supplier_name=supplier_name,
                    created_by=self.current_user.user_id,
                    contact_department=contact_department,
                    phone=phone,
                    email=email,
                    address=address,
                    is_active=is_active,
                    notes=notes
                )
                
                success = result[0] if isinstance(result, tuple) else result
                
                if success:
                    AuditService.log_action(
                        user_id=self.current_user.user_id,
                        action=AuditDefinition.SUPPLIER_CREATED,
                        success=True,
                        entity="Supplier",
                        meta={"supplier_name": supplier_name, "contact_department": contact_department}
                    )
                    
                    self._emit_success("Supplier added successfully")
                    self._post_save_cleanup()
                else:
                    self._emit_error("Failed to add supplier")
        except Exception as e:
            logger.exception("Error saving supplier")
            self._emit_error("An error occurred while saving the supplier")
        
    def _handle_edit(self) -> None:
        data = self.view.get_selected_supplier_data()
        
        if not data or data.get("id") is None:
            self._emit_error("Please select a valid supplier to edit")
            return
        
        self._is_editing = True
        self._current_supplier_id = data["id"]
        self.view.set_form_data(data)
        
    def _handle_cancel(self) -> None:
        self._post_save_cleanup()
        
    def _load_suppliers(self) -> None:
        suppliers = SupplierModel.get_all_suppliers()
        self.view.load_suppliers(suppliers)

    def _load_user_information(self) -> None:
        user_info = {
            "username": self.current_user.username,
            "user_role": self.current_user.user_role
        }
        self.view.load_user_information(user_info)
    
    def _on_search_text_changed(self, text: str) -> None:
        query = (text or "").strip()
        
        if not query:
            self._load_suppliers()
            return
        
        # If the query is numeric, search by ID
        if query.isdigit():
            try:
                suppliers = SupplierModel.search_by_supplier_id(int(query))
                self.view.load_suppliers(suppliers)
            except Exception:
                logger.exception("Error searching suppliers by id")
                self._emit_error("Unexpected error during search")
            return
        
        # Validate minimum length for name search
        if len(query) < 3:
            return
        
        # Search by name
        try:
            suppliers = SupplierModel.search_by_supplier_name(query)
            self.view.load_suppliers(suppliers)
        except Exception:
            logger.exception("Error searching suppliers by name")
            self._emit_error("Unexpected error during search")
        
    def _post_save_cleanup(self) -> None:
        self._current_supplier_id = None
        self._is_editing = False
        self.view.clear_form()
        self._load_suppliers()
    
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

