import logging
from models.audit_model import AuditModel
from domain.audit_definitions import AuditDefinition

logger = logging.getLogger(__name__)

class AuditService:
    """
    Service for handling audit logging.
    """

    @staticmethod
    def log_action(user_id, action: AuditDefinition, success: bool, entity: str | None = None, entity_id: int | None = None, meta: dict | None = None):
        """
        Logs an action performed by a user.

        Args:
            user_id (int): The ID of the user performing the action.
            action (AuditDefinition): The action performed by the user.
            success (bool): Whether the action was successful.
            entity (str | None): The type of entity affected by the action (optional).
            entity_id (int | None): The ID of the entity affected by the action (optional).
            meta (dict | None): Additional metadata related to the action (optional).

        Returns:
            bool: True if the log entry was added successfully, False otherwise.
        """

        if user_id is None:
            logger.warning("Attempted to log action with no user_id.")
            return False
        
        try:
            result = AuditModel.insert_log(
                user_id=user_id,
                action=action.value,
                success=success,
                entity=entity,
                entity_id=entity_id,
                meta=meta
            )
            return result
        except Exception:
            logger.exception("Failed to log action.",
                             extra={
                                 
                                 "user_id": user_id,
                                 "action": action.value,
                                 "success": success,
                                 "entity": entity,
                                 "entity_id": entity_id,
                                 "meta": meta
                             })
            return False