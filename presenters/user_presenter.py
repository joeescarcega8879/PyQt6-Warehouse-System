import logging
from common.enums import StatusType
from models.user_model import UserModel

from domain.permissions import Permission
from domain.permissions_service import PermissionService
from domain.audit_service import AuditService
from domain.audit_definitions import AuditDefinition

class UserPresenter:
    def __init__(self, view,main_app, status_handler, current_user):
        self.view = view
        self.main_app = main_app
        self.status_handler = status_handler
        self.current_user = current_user

        self._is_editing = False
        self._current_user_id: int | None = None

        self._connect_signals()
        self._load_init_data()
        self._load_user_information()
        self._apply_permissions()

    def _connect_signals(self) -> None:
        self.view.save_requested.connect(self._handle_save)
        self.view.edit_requested.connect(self._handle_edit)
        self.view.search_text_changed.connect(self._on_text_search_changed)
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
                if self._current_user_id is None:
                    self._emit_error("Please select a valid user to edit")
                    return
                
                success = UserModel.update_user_info(
                    user_id=self._current_user_id,
                    username=user_name,
                    full_name=full_name,
                    user_role=user_role,
                    is_active=is_active,
                )
            else:
                success = UserModel.create_user(
                    username=user_name,
                    password=password,
                    full_name=full_name,
                    user_role=user_role,
                    is_active=is_active,
                )

            if success:
                self._emit_success("User saved successfully")
                self._post_save_cleanup()
                self._load_init_data()
            else:
                self._emit_error("Failed to save user. Username might already exist.")
        except Exception:
            logging.exception("Error saving user")
            self._emit_error("An unexpected error occurred while saving the user.")

    def _handle_edit(self) -> None:
        user_data = self.view.get_selected_user_data() or {}
        if not user_data or user_data.get("user_id") is None:
            self._emit_error("Please select a valid user to edit")
            return
        
        self._is_editing = True
        self._current_user_id = user_data["user_id"]
        self.view.set_form_data(user_data)

    def _on_text_search_changed(self, text: str) -> None:
        query = (text or "").strip()

        if not query:
            self._load_init_data()
            return
        
        if query.isdigit():
            try:
                user_id = UserModel.get_user_by_id(int(query))
                self.view.load_users(user_id)
            except Exception:
                logging.exception("Error searching user by ID")
                self._emit_error("Error searching user by ID")
        
        if len(query) < 3:
            return
        
        try:
            users = UserModel.get_user_by_name(query)
            self.view.load_users(users)
        except Exception:
            logging.exception("Error searching users by name")
            self._emit_error("Error searching users by name")


    def _handle_change_password(self) -> None:
        
        user_id = self.view.get_selected_user_id()
        if not user_id:
            self._emit_error("Please select a valid user to change password")
            return
        
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

        self.main_app.open_change_password_form(user_id)
    
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
    
    def _load_user_information(self) -> None:
        user_info = {
            "username": self.current_user.username,
            "user_role": self.current_user.user_role,
        }
        self.view.load_user_information(user_info)

    def _load_init_data(self) -> None:
        users, error = UserModel.get_all_users()
        if error:
            self._emit_error(f"Error loading users: {error}")
            return
        self.view.load_users(users)

    def _emit_error(self, message: str) -> None:
        self.status_handler(message, 3000, StatusType.ERROR)

    def _emit_success(self, message: str) -> None:
        self.status_handler(message, 3000, StatusType.SUCCESS)

    def _post_save_cleanup(self) -> None:
        self._is_editing = False
        self._current_user_id = None
        self.view.clear_form()
        self._enable_password_fields()

    def _enable_password_fields(self) -> None:
        self.view.enable_password_fields(True)

