from src.config.logger_config import logger
from src.models.user_model import UserModel

from src.common.error_messages import ErrorMessages
from src.presenters.base_presenter import BasePresenter

from src.domain.audit_service import AuditService
from src.domain.audit_definitions import AuditDefinition
from src.domain.password_policy import PasswordPolicy


class ChangePasswordPresenter(BasePresenter):
    def __init__(self, view, user_id, current_user, status_handler):
        super().__init__(view=view, status_handler=status_handler, current_user=current_user)
        self.user_id = user_id

        self._connect_signals()

    def _connect_signals(self):
        self.view.get_button_box().accepted.connect(self._change_password)
        self.view.get_button_box().rejected.connect(self.view.close)

    def _change_password(self):
        password = self.view.get_password()
        confirm_password = self.view.get_confirm_password()

        # Basic validation
        if not password or not confirm_password:
            self._emit_error(ErrorMessages.VALIDATION_ERROR)
            return

        if password != confirm_password:
            self._emit_error(ErrorMessages.PASSWORD_MISMATCH)
            return

        # Password policy validation
        is_valid, policy_error = PasswordPolicy.validate(password)
        if not is_valid:
            self._emit_error(policy_error)
            return

        try:
            success = UserModel.change_user_password(self.user_id, password)

            if success:
                AuditService.log_action(
                    user_id=self.current_user.user_id,
                    action=AuditDefinition.USERS_PASSWORD_CHANGED,
                    success=True,
                    entity="User",
                    entity_id=self.user_id,
                    meta={"changed_by": self.current_user.username}
                )

                self._emit_success(ErrorMessages.PASSWORD_CHANGE_SUCCESS)
                self.view.accept()
            else:
                self._emit_error(ErrorMessages.PASSWORD_CHANGE_FAILED)
                return
        except Exception as e:
            logger.exception("Error changing password for user")
            error_msg = ErrorMessages.log_and_mask_error(
                e,
                f"Change password for user {self.user_id}",
                ErrorMessages.PASSWORD_CHANGE_FAILED
            )
            self._emit_error(error_msg)
            return