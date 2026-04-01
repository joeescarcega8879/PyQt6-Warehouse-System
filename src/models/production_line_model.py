from src.models.base_model import BaseModel


class ProductionLineModel(BaseModel):
    """
    Model class for managing production lines in the database.
    Handles secure error logging and provides generic error messages to users.
    """

    TABLE_NAME = "production_lines"
    ENTITY_NAME = "production line"
    ID_COLUMN = "line_id"
    NAME_COLUMN = "line_name"
    COLUMNS = "line_id, line_name, description, is_active"

    @staticmethod
    def _map_row(row: dict) -> tuple:
        return (
            row["line_id"],
            row["line_name"],
            row["description"],
            row["is_active"],
        )

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
        ok, error, _ = BaseModel._execute_insert(
            sql="""
                INSERT INTO production_lines(line_name, description, is_active)
                VALUES (:name, :description, :is_active)
                """,
            params={"name": name, "description": description, "is_active": is_active},
            entity_name=ProductionLineModel.ENTITY_NAME,
            context=f"adding production line '{name}'",
        )
        return ok, error

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
        return BaseModel._execute_update(
            sql="""
                UPDATE production_lines
                SET line_name = :line_name,
                    description = :description,
                    is_active = :is_active
                WHERE line_id = :line_id
                """,
            params={
                "line_id": line_id,
                "line_name": line_name,
                "description": description,
                "is_active": is_active,
            },
            entity_name=ProductionLineModel.ENTITY_NAME,
            entity_id=line_id,
            context=f"updating production line ID {line_id}",
        )

    @staticmethod
    def get_all_production_lines() -> list[tuple]:
        """
        Retrieves all production lines from the database.
        Returns:
            list[tuple]: A list of tuples representing production lines.
                Returns empty list if error occurs.
        """
        return BaseModel._get_all_pattern(
            table_name=ProductionLineModel.TABLE_NAME,
            columns=ProductionLineModel.COLUMNS,
            entity_name=ProductionLineModel.ENTITY_NAME,
            row_mapper=ProductionLineModel._map_row,
            order_by=ProductionLineModel.ID_COLUMN,
        )

    @staticmethod
    def search_by_id(line_id: int) -> list[tuple]:
        """
        Searches for a production line by its ID.
        Args:
            line_id (int): The ID of the production line to search for.
        Returns:
            list[tuple]: A list containing the production line tuple if found, empty list otherwise.
        """
        return BaseModel._search_by_id_pattern(
            table_name=ProductionLineModel.TABLE_NAME,
            columns=ProductionLineModel.COLUMNS,
            id_column=ProductionLineModel.ID_COLUMN,
            entity_id=line_id,
            entity_name=ProductionLineModel.ENTITY_NAME,
            row_mapper=ProductionLineModel._map_row,
        )

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
        return BaseModel._search_by_name_pattern(
            table_name=ProductionLineModel.TABLE_NAME,
            columns=ProductionLineModel.COLUMNS,
            name_column=ProductionLineModel.NAME_COLUMN,
            search_term=line_name,
            entity_name=ProductionLineModel.ENTITY_NAME,
            row_mapper=ProductionLineModel._map_row,
            order_by=ProductionLineModel.ID_COLUMN,
        )
