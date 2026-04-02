from src.config.logger_config import logger
from src.models.supplier_model import SupplierModel

from src.domain.audit_service import AuditService
from src.domain.audit_definitions import AuditDefinition
from src.domain.permissions import Permission
from src.domain.permissions_service import PermissionService

from src.presenters.base_presenter import BasePresenter


class SupplierPresenter(BasePresenter):
    def __init__(self, view, main_app, status_handler, current_user):
        super().__init__(view, status_handler, current_user, main_app=main_app)

        self._connect_signals()
        self._load_suppliers()
        self._load_user_information_to_view()

    def _connect_signals(self) -> None:
        self.view.save_requested.connect(self._handle_save)
        self.view.edit_requested.connect(self._handle_edit)
        self.view.search_text_changed.connect(self._on_search_text_changed)
        self.view.cancel_requested.connect(self._handle_cancel)

    def _handle_save(self) -> None:
        data = self.view.get_supplier_form_data() or {}
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
                if self._current_entity_id is None:
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
                    supplier_id=self._current_entity_id,
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
                        meta={"supplier_id": self._current_entity_id, "supplier_name": supplier_name}
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
        except Exception:
            logger.exception("Error saving supplier")
            self._emit_error("An error occurred while saving the supplier")

    def _handle_edit(self) -> None:
        data = self.view.get_selected_supplier_data()

        if not data or data.get("id") is None:
            self._emit_error("Please select a valid supplier to edit")
            return

        self._enter_edit_mode(data["id"])
        self.view.set_form_data(data)

    def _handle_cancel(self) -> None:
        self._post_save_cleanup()

    def _on_search_text_changed(self, text: str) -> None:
        self._handle_search_with_id_and_name(
            query=text,
            search_by_id_func=lambda id: SupplierModel.search_by_supplier_id(id),
            search_by_name_func=lambda name: SupplierModel.search_by_supplier_name(name),
            load_all_func=self._load_suppliers,
            load_results_func=self.view.load_suppliers,
            entity_name="supplier"
        )

    def _post_save_cleanup(self) -> None:
        self._exit_edit_mode()
        self.view.clear_form()
        self._load_suppliers()

    def _load_suppliers(self) -> None:
        suppliers = SupplierModel.get_all_suppliers()
        self.view.load_suppliers(suppliers)

    def _validate(self, data: dict) -> str | None:
        supplier_name = (data.get("supplier_name") or "").strip()
        contact_department = (data.get("contact_department") or "").strip()

        if not supplier_name:
            return "Supplier name is required"
        if not contact_department:
            return "Contact department is required"

        return None
