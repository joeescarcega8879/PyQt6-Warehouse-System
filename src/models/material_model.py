import logging
from src.models.base_model import BaseModel

logger = logging.getLogger(__name__)

class MaterialModel(BaseModel):
    """
    Model for managing materials in the database.
    Handles secure error logging and provides generic error messages to users.
    Extends BaseModel for common database operations.
    """

    # Table metadata
    TABLE_NAME = "materials"
    ENTITY_NAME = "material"
    ID_COLUMN = "material_id"
    NAME_COLUMN = "material_name"
    COLUMNS = "material_id, material_name, description, unit_of_measure"

    @staticmethod
    def _map_material_row(row: dict) -> tuple:
        """Map database row to material tuple."""
        return (
            row["material_id"],
            row["material_name"],
            row["description"],
            row["unit_of_measure"],
        )

    @staticmethod
    def add_material(name: str, description: str, unit: str) -> tuple[bool, str | None]:
        """
        Adds a new material to the database.
        Args:
            name (str): The name of the material.
            description (str): A brief description of the material.
            unit (str): The unit of measurement for the material.
        Returns:
            tuple[bool, str | None]: (success, error_message)
                - success: True if material was added successfully
                - error_message: None if successful, generic error message if failed
        """
        sql = """
            INSERT INTO materials (material_name, description, unit_of_measure)
            VALUES (:name, :description, :unit)
        """
        params = {
            "name": name,
            "description": description,
            "unit": unit
        }
        
        success, error, _ = MaterialModel._execute_insert(
            sql=sql,
            params=params,
            entity_name=MaterialModel.ENTITY_NAME,
            context=f"adding material '{name}'"
        )
        
        return success, error

    @staticmethod
    def update_material(material_id: int, name: str, description: str, unit: str) -> tuple[bool, str | None]:
        """
        Updates an existing material in the database.
        Args:
            material_id (int): The ID of the material to update.
            name (str): The new name of the material.
            description (str): The new description of the material.
            unit (str): The new unit of measurement for the material.
        Returns:
            tuple[bool, str | None]: (success, error_message)
                - success: True if material was updated successfully
                - error_message: None if successful, generic error message if failed
        """
        sql = """
            UPDATE materials
            SET material_name = :name,
                description = :description,
                unit_of_measure = :unit
            WHERE material_id = :material_id
        """
        params = {
            "material_id": material_id,
            "name": name,
            "description": description,
            "unit": unit
        }
        
        return MaterialModel._execute_update(
            sql=sql,
            params=params,
            entity_name=MaterialModel.ENTITY_NAME,
            entity_id=material_id,
            context=f"updating material ID {material_id}"
        )

    @staticmethod
    def delete_material(material_id: int) -> tuple[bool, str | None]:
        """
        Deletes a material from the database.
        Args:
            material_id (int): The ID of the material to delete.
        Returns:
            tuple[bool, str | None]: (success, error_message)
                - success: True if material was deleted successfully
                - error_message: None if successful, generic error message if failed
        """
        sql = """
            DELETE FROM materials
            WHERE material_id = :material_id
        """
        params = {"material_id": material_id}
        
        return MaterialModel._execute_delete(
            sql=sql,
            params=params,
            entity_name=MaterialModel.ENTITY_NAME,
            entity_id=material_id,
            context=f"deleting material ID {material_id}"
        )

    @staticmethod
    def get_all_materials() -> list[tuple]:
        """
        Retrieves all materials from the database.
        Returns:
            list[tuple]: Tuples in the order (material_id, material_name, description, unit_of_measure).
                Returns empty list if error occurs.
        """
        return MaterialModel._get_all_pattern(
            table_name=MaterialModel.TABLE_NAME,
            columns=MaterialModel.COLUMNS,
            entity_name=MaterialModel.ENTITY_NAME,
            row_mapper=MaterialModel._map_material_row,
            order_by=MaterialModel.ID_COLUMN
        )

    @staticmethod
    def search_by_id(material_id: int) -> list[tuple]:
        """
        Searches for a material by its ID.
        Args:
            material_id (int): The ID of the material to search for.
        Returns:
            list[tuple]: Tuples in the order (material_id, material_name, description, unit_of_measure).
                Returns empty list if not found or error occurs.
        """
        return MaterialModel._search_by_id_pattern(
            table_name=MaterialModel.TABLE_NAME,
            columns=MaterialModel.COLUMNS,
            id_column=MaterialModel.ID_COLUMN,
            entity_id=material_id,
            entity_name=MaterialModel.ENTITY_NAME,
            row_mapper=MaterialModel._map_material_row
        )

    @staticmethod
    def search_by_name(material_name: str) -> list[tuple]:
        """
        Searches for materials by their name.
        Args:
            material_name (str): The name of the material to search for.
        Returns:
            list[tuple]: Tuples in the order (material_id, material_name, description, unit_of_measure).
                Returns empty list if not found or error occurs.
        """
        return MaterialModel._search_by_name_pattern(
            table_name=MaterialModel.TABLE_NAME,
            columns=MaterialModel.COLUMNS,
            name_column=MaterialModel.NAME_COLUMN,
            search_term=material_name,
            entity_name=MaterialModel.ENTITY_NAME,
            row_mapper=MaterialModel._map_material_row,
            order_by=MaterialModel.ID_COLUMN
        )
