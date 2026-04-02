from PyQt6.QtWidgets import QMessageBox

from src.config.logger_config import logger

from src.domain.permissions import Permission
from src.domain.audit_service import AuditService
from src.domain.audit_definitions import AuditDefinition
from src.domain.permissions_service import PermissionService

from src.models.supplier_receipt_model import SupplierReceiptModel
from src.presenters.base_presenter import BasePresenter


class SupplierReceiptPresenter(BasePresenter):
    def __init__(self, view, main_app, status_handler, current_user):
        super().__init__(view, status_handler, current_user, main_app=main_app)

        self._selected_material: dict | None = None

        self._connect_signals()
        self._load_user_information_to_view()
        self._apply_permissions()
        self._load_receipts_data()

    def _connect_signals(self) -> None:
        self.view.material_selected.connect(self._handle_select_material)
        self.view.supplier_selected.connect(self._handle_select_supplier)
        self.view.save_requested.connect(self._handle_save)
        self.view.edit_requested.connect(self._handle_edit)
        self.view.delete_requested.connect(self._handle_delete)
        self.view.cancel_requested.connect(self._handle_cancel)

    def _handle_save(self) -> None:
        data = self.view.get_receipt_form_data() or {}
        data["created_by"] = self.current_user.user_id

        error = self._validate(data)
        if error:
            self._emit_error(error)
            return

        # After validation, we know these are correct types
        material_id: int = data.get("material_id")  # type: ignore
        supplier_id: int = data.get("supplier_id")  # type: ignore
        quantity = float(data.get("quantity", "").strip())
        notes = (data.get("notes") or "").strip() or None
        created_by: int = data["created_by"]

        try:
            if self._is_editing:
                if self._current_entity_id is None:
                    self._emit_error("Please select a valid receipt to edit")
                    return

                if not PermissionService.has_permission(self.current_user, Permission.RECEIPTS_EDIT):
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
                    receipt_id=self._current_entity_id,
                    material_id=material_id,
                    supplier_id=supplier_id,
                    quantity_received=quantity,
                    notes=notes
                )

                if success:
                    AuditService.log_action(
                        user_id=self.current_user.user_id,
                        action=AuditDefinition.RECEIPTS_EDITED,
                        success=True,
                        entity="SupplierReceipt",
                        entity_id=self._current_entity_id,
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
                if not PermissionService.has_permission(self.current_user, Permission.RECEIPTS_CREATE):
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
            self._emit_error(f"Invalid quantity format. Must be a valid number. {e}")

        except Exception as e:
            logger.exception("Error saving receipt")
            self._emit_error(f"Unexpected error saving receipt: {e}")

    def _handle_edit(self) -> None:
        data = self.view.get_selected_receipt_data()

        if not data or data.get("id") is None:
            self._emit_error("Please select a valid receipt to edit")
            return

        self._enter_edit_mode(data["id"])
        self.view.set_form_data(data)

    def _handle_delete(self) -> None:
        data = self.view.get_selected_receipt_data()

        if not data or data.get("id") is None:
            self._emit_error("Please select a valid receipt to delete")
            return

        receipt_id = data["id"]

        try:
            if not PermissionService.has_permission(self.current_user, Permission.RECEIPTS_DELETE):
                self._emit_error("You do not have permission to delete receipts")
                AuditService.log_action(
                    user_id=self.current_user.user_id,
                    action=AuditDefinition.RECEIPTS_DELETED,
                    success=False,
                    entity="SupplierReceipt",
                    entity_id=receipt_id,
                    meta={"reason": "Insufficient permissions"}
                )
                return

            confirm = QMessageBox.question(
                self.view,
                "Confirm Delete",
                f"Are you sure you want to delete receipt ID {receipt_id}? This action cannot be undone.",
                QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
                QMessageBox.StandardButton.No
            )
            if confirm != QMessageBox.StandardButton.Yes:
                return

            success, error_msg = SupplierReceiptModel.delete_receipt(receipt_id)

            if success:
                AuditService.log_action(
                    user_id=self.current_user.user_id,
                    action=AuditDefinition.RECEIPTS_DELETED,
                    success=True,
                    entity="SupplierReceipt",
                    entity_id=receipt_id
                )
                self._emit_success("Receipt deleted successfully")
                self._load_receipts_data()
            else:
                self._emit_error(f"Error deleting receipt: {error_msg}")
                AuditService.log_action(
                    user_id=self.current_user.user_id,
                    action=AuditDefinition.RECEIPTS_DELETED,
                    success=False,
                    entity="SupplierReceipt",
                    entity_id=receipt_id,
                    meta={"reason": error_msg}
                )

        except Exception:
            logger.exception("Error deleting receipt")
            self._emit_error("Unexpected error deleting receipt")

    def _handle_cancel(self) -> None:
        self._exit_edit_mode()
        self.view.clear_form()
        self._load_receipts_data()

    def _apply_permissions(self) -> None:
        can_create = PermissionService.has_permission(self.current_user, Permission.RECEIPTS_CREATE)
        can_edit   = PermissionService.has_permission(self.current_user, Permission.RECEIPTS_EDIT)
        can_delete = PermissionService.has_permission(self.current_user, Permission.RECEIPTS_DELETE)
        self.view.enable_create(can_create)
        self.view.enable_edit(can_edit)
        self.view.enable_delete(can_delete)

    def _load_receipts_data(self) -> None:
        receipts = SupplierReceiptModel.get_all_receipts()
        self.view.load_receipts(receipts)

    def _post_save_cleanup(self) -> None:
        self._exit_edit_mode()
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
        self._selected_material = material
        self.view.display_selected_material(material)

    def _validate(self, data: dict) -> str | None:
        raw_material = data.get("material_id")
        raw_supplier = data.get("supplier_id")
        quantity_str = (data.get("quantity") or "").strip()
        created_by = data.get("created_by")

        # Validate required fields exist before any conversion
        if not raw_material:
            return "Material is required. Please select a material."

        if not raw_supplier:
            return "Supplier is required. Please select a supplier."

        if not quantity_str:
            return "Quantity is required"

        if not created_by:
            return "User information is missing"

        if not isinstance(created_by, int):
            return "Invalid user information"

        int(raw_material)
        int(raw_supplier)

        # Validate quantity is a valid positive number
        try:
            quantity = float(quantity_str)
            if quantity <= 0:
                return "Quantity must be greater than 0"
        except ValueError:
            return "Quantity must be a valid number"

        return None
