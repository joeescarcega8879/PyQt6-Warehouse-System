import logging
from database.query_helper import QueryHelper, DatabaseError
from common.error_messages import ErrorMessages

logger = logging.getLogger(__name__)

class AuditModel:
    """
    Model for handling audit logs in the database.
    Handles secure error logging and provides generic error messages to users.
    """

    @staticmethod
    def insert_log(user_id: int, action: str, success: bool, entity: str | None = None, entity_id: int | None = None, meta: dict | None = None) -> tuple[bool, str | None]:
        """
        Inserts a new audit log entry into the database.
        
        Args:
            user_id (int): The ID of the user performing the action.
            action (str): The action performed by the user.
            success (bool): Whether the action was successful.
            entity (str | None): The type of entity affected by the action (optional).
            entity_id (int | None): The ID of the entity affected by the action (optional).
            meta (dict | None): Additional metadata related to the action (optional).
        
        Returns:
            tuple[bool, str | None]: (success, error_message)
                - success: True if the log entry was added successfully, False otherwise.
                - error_message: None if successful, generic error message if failed.
        """
        meta_json = QueryHelper._to_json_(meta) if meta is not None else None

        try:
            result = QueryHelper.execute(
                """
                INSERT INTO audit_log (user_id, action, success, entity, entity_id, meta)
                VALUES (:user_id, :action, :success, :entity, :entity_id, :meta)
                """,
                {
                    "user_id": user_id,
                    "action": action,
                    "success": success,
                    "entity": entity,
                    "entity_id": entity_id,
                    "meta":  meta_json
                },
            )

            if result.get("rows_affected", 0) != 1:
                logger.warning(f"Failed to insert audit log for user {user_id}, action: {action}")
                return False, ErrorMessages.SAVE_FAILED
            
            return True, None
            
        except DatabaseError as e:
            return False, ErrorMessages.log_and_mask_error(
                error=e,
                context=f"inserting audit log for user {user_id}, action: {action}",
                user_message=ErrorMessages.DATABASE_ERROR
            )
        except Exception as e:
            return False, ErrorMessages.log_and_mask_error(
                error=e,
                context=f"inserting audit log for user {user_id}, action: {action}",
                user_message=ErrorMessages.GENERIC_ERROR
            )
        
