from src.config.logger_config import logger
from src.models.user_model import UserModel

from src.domain.permissions import Permission
from src.domain.permissions_service import PermissionService
from src.domain.audit_service import AuditService
from src.domain.audit_definitions import AuditDefinition

from src.presenters.base_presenter import BasePresenter


class UserPresenter(BasePresenter):
    def __init__(self, view, main_app, status_handler, current_user):
        super().__init__(view, status_handler, current_user, main_app=main_app)

        self._connect_signals()
        self._load_init_data()
        self._load_user_information_to_view()
        self._apply_permissions()

    def _connect_signals(self) -> None:
        self.view.save_requested.connect(self._handle_save)
        self.view.edit_requested.connect(self._handle_edit)
        self.view.search_text_changed.connect(self._on_search_text_changed)
        self.view.change_password_requested.connect(self._handle_change_password)

    def _handle_save(self) -> None:
        user_data = self.view.get_user_form_data() or {}

        error = self._validate(user_data)
        if error:
            self._emit_error(error)
            return

        user_name = user_data.get("username", "").strip()
        password = user_data.get("password", "")
        full_name = user_data.get("full_name", "").strip()
        user_role = user_data.get("user_role", "").strip()
        is_active = user_data.get("is_active", True)

        try:
            if self._is_editing:
                if self._current_entity_id is None:
                    self._emit_error("Please select a valid user to edit")
                    return

                if not PermissionService.has_permission(self.current_user, Permission.USERS_EDIT):
                    self._emit_error("You do not have permission to edit users")
                    AuditService.log_action(
                        user_id=self.current_user.user_id,
                        action=AuditDefinition.USERS_EDITED,
                        success=False,
                        entity="User",
                        meta={"reason": "Insufficient permissions"}
                    )
                    return

                success = UserModel.update_user_info(
                    user_id=self._current_entity_id,
                    username=user_name,
                    full_name=full_name,
                    user_role=user_role,
                    is_active=is_active,
                )

                if success:
                    AuditService.log_action(
                        user_id=self.current_user.user_id,
                        action=AuditDefinition.USERS_EDITED,
                        success=True,
                        entity="User",
                        entity_id=self._current_entity_id,
                        meta={"username": user_name, "user_role": user_role}
                    )
                    self._emit_success("User updated successfully")
                    self._post_save_cleanup()
                    self._load_init_data()
                else:
                    self._emit_error("Failed to update user. Username might already exist.")
            else:
                if not PermissionService.has_permission(self.current_user, Permission.USERS_CREATE):
                    self._emit_error("You do not have permission to create users")
                    AuditService.log_action(
                        user_id=self.current_user.user_id,
                        action=AuditDefinition.USERS_CREATED,
                        success=False,
                        entity="User",
                        meta={"reason": "Insufficient permissions"}
                    )
                    return

                success = UserModel.create_user(
                    username=user_name,
                    password=password,
                    full_name=full_name,
                    user_role=user_role,
                    is_active=is_active,
                )

                if success:
                    AuditService.log_action(
                        user_id=self.current_user.user_id,
                        action=AuditDefinition.USERS_CREATED,
                        success=True,
                        entity="User",
                        meta={"username": user_name, "user_role": user_role}
                    )
                    self._emit_success("User created successfully")
                    self._post_save_cleanup()
                    self._load_init_data()
                else:
                    self._emit_error("Failed to create user. Username might already exist.")
        except Exception:
            logger.exception("Error saving user")
            self._emit_error("An unexpected error occurred while saving the user.")

    def _handle_edit(self) -> None:
        user_data = self.view.get_selected_user_data() or {}
        if not user_data or user_data.get("user_id") is None:
            self._emit_error("Please select a valid user to edit")
            return

        self._enter_edit_mode(user_data["user_id"])
        self.view.set_form_data(user_data)

    def _on_search_text_changed(self, text: str) -> None:
        self._handle_search_with_id_and_name(
            query=text,
            search_by_id_func=lambda id: UserModel.get_user_by_id(id),
            search_by_name_func=lambda name: UserModel.get_user_by_name(name),
            load_all_func=self._load_init_data,
            load_results_func=self.view.load_users,
            entity_name="user"
        )

    def _handle_change_password(self) -> None:
        if not PermissionService.has_permission(self.current_user, Permission.USERS_CHANGE_PASSWORD):
            self._emit_error("You do not have permission to change user passwords")
            AuditService.log_action(
                user_id=self.current_user.user_id,
                action=AuditDefinition.USERS_PASSWORD_CHANGED,
                success=False,
                entity="User",
                meta={"reason": "Insufficient permissions"}
            )
            return

        target_id = self.view.get_selected_user_id()
        if target_id is None:
            self._emit_error("Please select a user to change their password")
            return

        self.main_app.open_change_password_form(target_id)

    def _apply_permissions(self) -> None:
        self.view.enable_create(PermissionService.has_permission(self.current_user, Permission.USERS_CREATE))
        self.view.enable_edit(PermissionService.has_permission(self.current_user, Permission.USERS_EDIT))
        self.view.enable_change_password(PermissionService.has_permission(self.current_user, Permission.USERS_CHANGE_PASSWORD))

    def _validate(self, data: dict) -> str | None:
        username = data.get("username", "").strip()
        password = data.get("password", "")
        confirm_password = data.get("confirm_password", "")
        full_name = data.get("full_name", "").strip()
        user_role = data.get("user_role", "")

        if not username:
            return "Username is required"

        if not full_name:
            return "Full name is required"

        if not user_role:
            return "User role is required"

        if not self._is_editing:
            if not password:
                return "Password is required for new users"

            if password != confirm_password:
                return "Passwords do not match"

        return None

    def _load_init_data(self) -> None:
        users, error = UserModel.get_all_users()
        if error:
            self._emit_error(f"Error loading users: {error}")
            return
        self.view.load_users(users)

    def _post_save_cleanup(self) -> None:
        self._exit_edit_mode()
        self.view.clear_form()
        self._enable_password_fields()

    def _enable_password_fields(self) -> None:
        self.view.enable_password_fields(True)
