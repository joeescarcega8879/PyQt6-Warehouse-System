from config.logger_config import logger
from database.query_helper import QueryHelper, DatabaseError

class ProductionLineModel:
    """
    Model class for managing production lines in the database.
    """

    @staticmethod
    def add_production_line(name: str, description: str, is_active: bool)-> tuple[bool, str]:
        """
        Adds a new production line to the database.
        Args:
            name (str): The name of the production line.
            description (str): A brief description of the production line.
            is_active (bool): Status indicating if the production line is active.
        Returns:
            bool: True if the production line was added successfully, False otherwise.
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
                return False, "Failed to add production line."
            
            return True, None
        
        except DatabaseError as e:
            logger.error(f"Error adding production line: {e}")
            return False, str(e)
        
        except Exception as e:
            logger.error(f"Unexpected error adding production line: {e}")
            return False, str(e)

    @staticmethod
    def update_production_line(line_id: int, line_name: str, description: str, is_active: bool)-> tuple[bool, str]:
        """
        Updates an existing production line in the database.
        Args:
            line_id (int): The ID of the production line to update.
            line_name (str): The new name of the production line.
            description (str): The new description of the production line.
            is_active (bool): The new active status of the production line.
        Returns:
            bool: True if the production line was updated successfully, False otherwise.
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
                return False, "Production line not found."
            
            return True, None
        
        except DatabaseError as e:
            logger.error(f"Error updating production line {line_id}: {e}")
            return False, str(e)
        
        except Exception as e:
            logger.error(f"Unexpected error updating production line {line_id}: {e}")
            return False, str(e)
        
    @staticmethod
    def get_all_production_lines() -> list[tuple]:
        """
        Retrieves all production lines from the database.
        Returns:
            list[tuple]: A list of tuples representing production lines.
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
            logger.error(f"Error retrieving production lines: {e}")
            return []
        
        except Exception as e:
            logger.error(f"Unexpected error retrieving production lines: {e}")
            return []
        
    @staticmethod
    def search_by_id(line_id: int) -> list[tuple] | None:
        """
        Searches for a production line by its ID.
        Args:
            line_id (int): The ID of the production line to search for.
        Returns:
            tuple | None: A tuple representing the production line if found, None otherwise.
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
            
            if rows is None:
                return None

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
            logger.error(f"Error searching for production line {line_id}: {e}")
            return []
        
        except Exception as e:
            logger.error(f"Unexpected error searching for production line {line_id}: {e}")
            return []
        
    @staticmethod
    def search_by_name(line_name: str) -> list[tuple]:
        """
        Searches for production lines by their name.
        Args:
            line_name (str): The name of the production line to search for.  
        Returns:
            list[tuple]: A list of tuples representing matching production lines.
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
            logger.error(f"Error searching production lines by name '{line_name}': {e}")
            return []
        
        except Exception as e:
            logger.error(f"Unexpected error searching production lines by name '{line_name}': {e}")
            return []