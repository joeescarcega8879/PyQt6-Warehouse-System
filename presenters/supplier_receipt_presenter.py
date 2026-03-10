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
        self.view.supplier_selected.connect(self._handle_select_supplier)
        self.view.save_requested.connect(self._handle_save)
        self.view.edit_requested.connect(self._handle_edit)
        self.view.cancel_requested.connect(self._handle_cancel)
      
    def _handle_save(self) -> None:
        data = self.view.get_receipt_form_data() or {}
        data["created_by"] = self.current_user.user_id
        
        # Validar datos
        error = self._validate(data)
        if error:
            self._emit_error(error)
            return
        
        # Extraer y convertir datos
        # After validation, we know these are correct types
        material_id: int = data.get("material_id")  # type: ignore
        supplier_id: int = data.get("supplier_id")  # type: ignore
        quantity = float(data.get("quantity", "").strip())
        notes = (data.get("notes") or "").strip() or None
        created_by: int = data["created_by"]
        
        try:
            if self._is_editing:
                # Editar receipt existente
                if self._current_receipt_id is None:
                    self._emit_error("Please select a valid receipt to edit")
                    return
                
                if not PermissionService.has_permission(
                    self.current_user, Permission.RECEIPTS_EDIT
                ):
                    self._emit_error("You do not have permission to edit receipts")
                    AuditService.log_action(
                        user_id=self.current_user.user_id,
                        action=AuditDefinition.RECEIPTS_EDITED,
                        success=False,
                        entity="SupplierReceipt",
                        meta={"reason": "Insufficient permissions"}
                    )
                    return
                
                success, error_msg = SupplierReceiptModel.update_receipt(
                    receipt_id=self._current_receipt_id,
                    material_id=material_id,
                    supplier_id=supplier_id,
                    quantity_received=quantity,  # Keep existing timestamp
                    notes=notes
                )
                
                if success:
                    AuditService.log_action(
                        user_id=self.current_user.user_id,
                        action=AuditDefinition.RECEIPTS_EDITED,
                        success=True,
                        entity="SupplierReceipt",
                        entity_id=self._current_receipt_id,
                        meta={
                            "material_id": material_id,
                            "supplier_id": supplier_id,
                            "quantity": quantity
                        }
                    )
                    self._emit_success("Receipt updated successfully")
                    self._post_save_cleanup()
                else:
                    self._emit_error(f"Error updating receipt: {error_msg}")
            else:
                # Crear nuevo receipt
                if not PermissionService.has_permission(
                    self.current_user, Permission.RECEIPTS_CREATE
                ):
                    self._emit_error("You do not have permission to create receipts")
                    AuditService.log_action(
                        user_id=self.current_user.user_id,
                        action=AuditDefinition.RECEIPTS_CREATED,
                        success=False,
                        entity="SupplierReceipt",
                        meta={"reason": "Insufficient permissions"}
                    )
                    return
                
                success, error_msg, receipt_id = SupplierReceiptModel.add_receipt(
                    material_id=material_id,
                    supplier_id=supplier_id,
                    quantity_received=quantity,
                    created_by=created_by,
                    notes=notes
                )
                
                if success:
                    AuditService.log_action(
                        user_id=self.current_user.user_id,
                        action=AuditDefinition.RECEIPTS_CREATED,
                        success=True,
                        entity="SupplierReceipt",
                        entity_id=receipt_id,
                        meta={
                            "material_id": material_id,
                            "supplier_id": supplier_id,
                            "quantity": quantity
                        }
                    )
                    self._emit_success("Receipt created successfully")
                    self._post_save_cleanup()
                else:
                    self._emit_error(f"Error creating receipt: {error_msg}")
                    
        except ValueError as e:
            logger.exception("Invalid data format in receipt")
            self._emit_error("Invalid quantity format. Must be a valid number.")
        except Exception as e:
            logger.exception("Error saving receipt")
            self._emit_error("Unexpected error saving receipt")
    
    def _load_user_information(self) -> None:
        user_info = {
            "user_id": self.current_user.user_id,
            "user_role": self.current_user.user_role
        }

        self.view.load_user_information(user_info)
    
    def _validate(self, data: dict) -> str | None:
        """Validate receipt form data.
        
        Args:
            data: Dictionary with material_id, supplier_id, quantity, notes, created_by
            
        Returns:
            Error message string if invalid, None if valid
        """
        material_id = int(data.get("material_id"))
        supplier_id = int(data.get("supplier_id"))
        quantity_str = (data.get("quantity") or "").strip()
        created_by = int(data.get("created_by"))
        
        # Validate required fields exist
        if not material_id:
            return "Material is required. Please select a material."
        
        if not supplier_id:
            return "Supplier is required. Please select a supplier."
        
        if not quantity_str:
            return "Quantity is required"
        
        if not created_by:
            return "User information is missing"
        
        # Validate material_id and supplier_id are integers
        if not isinstance(material_id, int):
            return "Invalid material selection"
        
        if not isinstance(supplier_id, int):
            return "Invalid supplier selection"
        
        # Validate created_by is integer
        if not isinstance(created_by, int):
            return "Invalid user information"
        
        # Validate quantity is a valid positive number
        try:
            quantity = float(quantity_str)
            if quantity <= 0:
                return "Quantity must be greater than 0"
        except ValueError:
            return "Quantity must be a valid number"
        
        return None

    def _load_receipts_data(self) -> None:
        """Load all receipts from database into table."""
        receipts = SupplierReceiptModel.get_all_receipts()
        self.view.load_receipts(receipts)

    def _handle_edit(self) -> None:
        """Handle edit button click to load receipt into form."""
        data = self.view.get_selected_receipt_data()
        
        if not data or data.get("id") is None:
            self._emit_error("Please select a valid receipt to edit")
            return
        
        self._is_editing = True
        self._current_receipt_id = data["id"]
        
        # Cargar datos al formulario
        self.view.set_form_data(data)

    def _handle_cancel(self) -> None:
        """Handle cancel button click to reset form."""
        self._is_editing = False
        self._current_receipt_id = None
        self.view.clear_form()
        self._load_receipts_data()

    def _post_save_cleanup(self) -> None:
        """Reset form state after successful save."""
        self._is_editing = False
        self._current_receipt_id = None
        self._selected_material = None
        self.view.clear_form()
        self._load_receipts_data()

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
        
        self.main_app.open_generic_form(entity_type="material", on_item_selected=self._on_material_selected)

    def _handle_select_supplier(self) -> None:

        if not PermissionService.has_permission(self.current_user, Permission.RECEIPTS_CREATE):
            self._emit_error("You do not have permission to select suppliers for receipts")
            AuditService.log_action(
                user_id=self.current_user.user_id,
                action=AuditDefinition.RECEIPTS_CREATED,
                success=False,
                meta={"reason": "Insufficient permissions"}
            )
            return
        
        self.main_app.open_generic_form(entity_type="supplier", on_item_selected=self._on_supplier_selected)

    def _on_supplier_selected(self, supplier: dict) -> None:
        self.view.display_selected_supplier(supplier)

    def _on_material_selected(self, material: dict) -> None:

        # Save matierial selected
        self._selected_material = material
        self.view.display_selected_material(material)

    def _emit_error(self, message: str) -> None:
        self.status_handler(message, 3000, StatusType.ERROR)

    def _emit_success(self, message: str) -> None:
        self.status_handler(message, 3000, StatusType.SUCCESS)
