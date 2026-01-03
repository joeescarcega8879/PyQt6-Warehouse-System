import logging
from database.query_helper import QueryHelper, DatabaseError

logger = logging.getLogger(__name__)

class AuditModel:
    """
    Model for handling audit logs in the database.
    """

    @staticmethod
    def insert_log(user_id: int, action: str, success: bool, entity: str | None = None, entity_id: int | None = None, meta: dict | None = None) -> bool:
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
            bool: True if the log entry was added successfully, False otherwise.
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
                return False, "Failed to insert audit log entry."
            
            return True
        except DatabaseError as e:
            logger.error(f"Error inserting audit log: {e}")
            return False
        
