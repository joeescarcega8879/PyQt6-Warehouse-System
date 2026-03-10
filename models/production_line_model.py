from config.logger_config import logger
from database.query_helper import QueryHelper, DatabaseError
from common.error_messages import ErrorMessages

class ProductionLineModel:
    """
    Model class for managing production lines in the database.
    Handles secure error logging and provides generic error messages to users.
    """

    @staticmethod
    def add_production_line(name: str, description: str, is_active: bool) -> tuple[bool, str | None]:
        """
        Adds a new production line to the database.
        Args:
            name (str): The name of the production line.
            description (str): A brief description of the production line.
            is_active (bool): Status indicating if the production line is active.
        Returns:
            tuple[bool, str | None]: (success, error_message)
                - success: True if the production line was added successfully
                - error_message: None if successful, generic error message if failed
        """
        try:
            result = QueryHelper.execute(
                """
                INSERT INTO production_lines(line_name, description, is_active)
                VALUES (:name, :description, :is_active)
                """,
                {
                    "name":name,
                    "description": description,
                    "is_active": is_active
                }
            )

            if result.get("rows_affected", 0) != 1:
                logger.warning(f"Failed to add production line: {name}")
                return False, ErrorMessages.SAVE_FAILED
            
            return True, None
        
        except DatabaseError as e:
            return False, ErrorMessages.log_and_mask_error(
                error=e,
                context=f"adding production line '{name}'",
                user_message=ErrorMessages.DATABASE_ERROR
            )
        
        except Exception as e:
            return False, ErrorMessages.log_and_mask_error(
                error=e,
                context=f"adding production line '{name}'",
                user_message=ErrorMessages.GENERIC_ERROR
            )

    @staticmethod
    def update_production_line(line_id: int, line_name: str, description: str, is_active: bool) -> tuple[bool, str | None]:
        """
        Updates an existing production line in the database.
        Args:
            line_id (int): The ID of the production line to update.
            line_name (str): The new name of the production line.
            description (str): The new description of the production line.
            is_active (bool): The new active status of the production line.
        Returns:
            tuple[bool, str | None]: (success, error_message)
                - success: True if the production line was updated successfully
                - error_message: None if successful, generic error message if failed
        """
        try:
            result = QueryHelper.execute(
                """
                UPDATE production_lines
                SET line_name = :line_name,
                    description = :description,
                    is_active = :is_active
                WHERE line_id = :line_id
                """,
                {
                    "line_id": line_id,
                    "line_name": line_name,
                    "description": description,
                    "is_active": is_active
                },
            )

            if result.get("rows_affected", 0) != 1:
                logger.warning(f"Production line not found for update: ID {line_id}")
                return False, ErrorMessages.NOT_FOUND
            
            return True, None
        
        except DatabaseError as e:
            return False, ErrorMessages.log_and_mask_error(
                error=e,
                context=f"updating production line ID {line_id}",
                user_message=ErrorMessages.DATABASE_ERROR
            )
        
        except Exception as e:
            return False, ErrorMessages.log_and_mask_error(
                error=e,
                context=f"updating production line ID {line_id}",
                user_message=ErrorMessages.GENERIC_ERROR
            )
        
    @staticmethod
    def get_all_production_lines() -> list[tuple]:
        """
        Retrieves all production lines from the database.
        Returns:
            list[tuple]: A list of tuples representing production lines.
                Returns empty list if error occurs.
        """

        try:
            rows = QueryHelper.fetch_all(
                """
                SELECT line_id, line_name, description, is_active
                FROM production_lines
                """
            )

            return [
                (
                    row["line_id"],
                    row["line_name"],
                    row["description"],
                    row["is_active"]
                )
                for row in rows
            ]
        
        except DatabaseError as e:
            ErrorMessages.log_and_mask_error(
                error=e,
                context="retrieving all production lines",
                user_message=ErrorMessages.DATABASE_ERROR
            )
            return []
        
        except Exception as e:
            ErrorMessages.log_and_mask_error(
                error=e,
                context="retrieving all production lines",
                user_message=ErrorMessages.GENERIC_ERROR
            )
            return []
        
    @staticmethod
    def search_by_id(line_id: int) -> list[tuple]:
        """
        Searches for a production line by its ID.
        Args:
            line_id (int): The ID of the production line to search for.
        Returns:
            list[tuple]: A list containing the production line tuple if found, empty list otherwise.
        """

        try:
            rows = QueryHelper.fetch_all(
                """
                SELECT line_id, line_name, description, is_active
                FROM production_lines
                WHERE line_id = :id
                """,
                {"id": line_id}
            )

            return [
                (
                    row["line_id"],
                    row["line_name"],
                    row["description"],
                    row["is_active"]
                )
                for row in rows
            ]
            
        except DatabaseError as e:
            ErrorMessages.log_and_mask_error(
                error=e,
                context=f"searching production line by ID {line_id}",
                user_message=ErrorMessages.DATABASE_ERROR
            )
            return []
        
        except Exception as e:
            ErrorMessages.log_and_mask_error(
                error=e,
                context=f"searching production line by ID {line_id}",
                user_message=ErrorMessages.GENERIC_ERROR
            )
            return []
        
    @staticmethod
    def search_by_name(line_name: str) -> list[tuple]:
        """
        Searches for production lines by their name.
        Args:
            line_name (str): The name of the production line to search for.  
        Returns:
            list[tuple]: A list of tuples representing matching production lines.
                Returns empty list if not found or error occurs.
        """

        try:
            rows = QueryHelper.fetch_all(
                """
                SELECT line_id, line_name, description, is_active
                FROM production_lines
                WHERE line_name ILIKE :name
                ORDER BY line_id
                """,
                {"name": f"%{line_name}%"}
            )

            return [
                (
                    row["line_id"],
                    row["line_name"],
                    row["description"],
                    row["is_active"]
                )
                for row in rows
            ]
        
        except DatabaseError as e:
            ErrorMessages.log_and_mask_error(
                error=e,
                context=f"searching production lines by name '{line_name}'",
                user_message=ErrorMessages.DATABASE_ERROR
            )
            return []
        
        except Exception as e:
            ErrorMessages.log_and_mask_error(
                error=e,
                context=f"searching production lines by name '{line_name}'",
                user_message=ErrorMessages.GENERIC_ERROR
            )
            return []
