import logging
from database.query_helper import DatabaseError, QueryHelper

logger = logging.getLogger(__name__)

class MaterialModel:

    @staticmethod
    def add_material(name: str, description: str, unit: str) -> bool:
        """
        Adds a new material to the database.
        Args:
            name (str): The name of the material.
            description (str): A brief description of the material.
            unit (str): The unit of measurement for the material.
        Returns:
            bool: True if the material was added successfully, False otherwise.
        """
        try:
            result = QueryHelper.execute(
                """
                INSERT INTO materials (material_name, description, unit_of_measure)
                VALUES (:name, :description, :unit)
                """,
                {
                    "name": name,
                    "description": description,
                    "unit": unit
                },
            )
            return result['success']
        except DatabaseError as e:
            logger.error(f"Error adding material: {e}")
            return False
    
    @staticmethod
    def update_material(material_id: int, name: str, description: str, unit: str) -> bool:
        """
        Updates an existing material in the database.
        Args:
            material_id (int): The ID of the material to update.
            name (str): The new name of the material.
            description (str): The new description of the material.
            unit (str): The new unit of measurement for the material.
        Returns:
            bool: True if the material was updated successfully, False otherwise.
        """
        try:
            result = QueryHelper.execute(
                """
                UPDATE materials
                SET material_name = :name,
                    description = :description,
                    unit_of_measure = :unit
                WHERE material_id = :material_id
                """,
                {
                    "material_id": material_id,
                    "name": name,
                    "description": description,
                    "unit": unit
                },
            )
            return result['success']
        except DatabaseError as e:
            logger.error(f"Error updating material {material_id}: {e}")
            return False
    
    @staticmethod
    def delete_material(material_id: int) -> bool:
        """
        Deletes a material from the database.
        Args:
            material_id (int): The ID of the material to delete.
        Returns:
            bool: True if the material was deleted successfully, False otherwise.
        """
        try:
            result = QueryHelper.execute(
                """
                DELETE FROM materials
                WHERE material_id = :material_id
                """,
                {
                    "material_id": material_id
                },
            )
            return result['success']
        except DatabaseError as e:
            logger.error(f"Error deleting material {material_id}: {e}")
            return False
    
    @staticmethod
    def get_all_materials() -> list[tuple]:
        """
        Retrieves all materials from the database.
        Returns:
            list[tuple]: Tuples in the order (material_id, material_name, description, unit_of_measure).
        """
        try:
            rows = QueryHelper.fetch_all(
                """
                SELECT material_id, material_name, description, unit_of_measure
                FROM materials
                ORDER BY material_id ASC
                """
            )

            return [
                (
                    row["material_id"],
                    row["material_name"],
                    row["description"],
                    row["unit_of_measure"],
                )
                for row in rows
            ]
        except DatabaseError as e:
            logger.error(f"Error fetching materials: {e}")
            return []

    @staticmethod
    def search_by_id(material_id: int)-> list[tuple]:
        """
        Searches for a material by its ID.
        Args:
            material_id (int): The ID of the material to search for.
        Returns:
            list[tuple]: Tuples in the order (material_id, material_name, description, unit_of_measure).   
        """

        try:
            rows = QueryHelper.fetch_all( 
            """
                SELECT material_id, material_name, description, unit_of_measure
                FROM materials
                WHERE material_id = :id
                ORDER BY material_id
            """,
            {"id": material_id}

            )

            return [
                (
                    row["material_id"],
                    row["material_name"],
                    row["description"],
                    row["unit_of_measure"],
                )
                for row in rows
            ]

        except DatabaseError as e:
            logger.exception(f"Error searching material by ID {material_id}: {e}")
            return []
        
    @staticmethod
    def search_by_name(material_name: str) -> list[tuple]:
        """
        Searches for materials by their name.
        Args:
            material_name (str): The name of the material to search for.
        Returns:
            list[tuple]: Tuples in the order (material_id, material_name, description, unit_of_measure).
        """
        try:
            rows = QueryHelper.fetch_all( 
            """
                SELECT material_id, material_name, description, unit_of_measure
                FROM materials
                WHERE material_name ILIKE :name
                ORDER BY material_id
            """,
            {"name": f"%{material_name}%"}

            )

            return [
                (
                    row["material_id"],
                    row["material_name"],
                    row["description"],
                    row["unit_of_measure"],
                )
                for row in rows
            ]

        except DatabaseError as e:
            logger.exception(f"Error searching material by name {material_name}: {e}")
            return []

