from src.models.base_model import BaseModel


class SupplierModel(BaseModel):
    """
    Model class for managing suppliers in the database.
    Handles secure error logging and provides generic error messages to users.
    """

    TABLE_NAME = "suppliers"
    ENTITY_NAME = "supplier"
    ID_COLUMN = "supplier_id"
    NAME_COLUMN = "supplier_name"
    COLUMNS = "supplier_id, supplier_name, contact_department, phone, email, address, notes, is_active"

    @staticmethod
    def _map_row(row: dict) -> tuple:
        return (
            row["supplier_id"],
            row["supplier_name"],
            row["contact_department"],
            row["phone"],
            row["email"],
            row["address"],
            row["notes"],
            row["is_active"],
        )

    @staticmethod
    def add_supplier(
        supplier_name: str,
        created_by: int,
        contact_department: str | None,
        phone: str | None = None,
        email: str | None = None,
        address: str | None = None,
        notes: str | None = None,
        is_active: bool = True,
    ) -> tuple[bool, str | None, int | None]:
        """
        Creates a new supplier in the database.
        Args:
            supplier_name (str): The name of the supplier.
            created_by (int): The ID of the user creating the supplier.
            contact_department (str | None): The contact department of the supplier.
            phone (str | None): The phone number of the supplier.
            email (str | None): The email address of the supplier.
            address (str | None): The physical address of the supplier.
            notes (str | None): Additional notes about the supplier.
            is_active (bool): Whether the supplier is active or not. Defaults to True.
        Returns:
            tuple[bool, str | None, int | None]: (success, error_message, supplier_id)
                - success: True if supplier was created successfully
                - error_message: None if successful, generic error message if failed
                - supplier_id: ID of created supplier if successful, None otherwise
        """
        return BaseModel._execute_insert(
            sql="""
                INSERT INTO suppliers (
                    supplier_name,
                    contact_department,
                    phone,
                    email,
                    address,
                    notes,
                    is_active,
                    created_by
                )
                VALUES (
                    :supplier_name,
                    :contact_department,
                    :phone,
                    :email,
                    :address,
                    :notes,
                    :is_active,
                    :created_by
                )
                """,
            params={
                "supplier_name": supplier_name,
                "contact_department": contact_department,
                "phone": phone,
                "email": email,
                "address": address,
                "notes": notes,
                "is_active": is_active,
                "created_by": created_by,
            },
            entity_name=SupplierModel.ENTITY_NAME,
            context=f"adding supplier '{supplier_name}'",
        )

    @staticmethod
    def update_supplier(
        supplier_id: int,
        supplier_name: str,
        contact_department: str | None,
        phone: str | None = None,
        email: str | None = None,
        address: str | None = None,
        notes: str | None = None,
        is_active: bool = True,
    ) -> tuple[bool, str | None]:
        """
        Updates an existing supplier in the database.
        Args:
            supplier_id: ID of the supplier to update.
            supplier_name: Updated supplier name.
            contact_department: Updated contact department.
            phone: Updated phone number.
            email: Updated email address.
            address: Updated physical address.
            notes: Updated notes about the supplier.
            is_active: Updated active status of the supplier.
        Returns:
            tuple[bool, str | None]: (success, error_message)
                - success: True if supplier was updated successfully
                - error_message: None if successful, generic error message if failed
        """
        return BaseModel._execute_update(
            sql="""
                UPDATE suppliers
                SET
                    supplier_name = :supplier_name,
                    contact_department = :contact_department,
                    phone = :phone,
                    email = :email,
                    address = :address,
                    notes = :notes,
                    is_active = :is_active
                WHERE supplier_id = :supplier_id
                """,
            params={
                "supplier_id": supplier_id,
                "supplier_name": supplier_name,
                "contact_department": contact_department,
                "phone": phone,
                "email": email,
                "address": address,
                "notes": notes,
                "is_active": is_active,
            },
            entity_name=SupplierModel.ENTITY_NAME,
            entity_id=supplier_id,
            context=f"updating supplier ID {supplier_id}",
        )

    @staticmethod
    def get_all_suppliers() -> list[tuple]:
        """
        Retrieves all suppliers from the database.
        Returns:
            list[tuple]: A list of tuples containing supplier information.
                Returns empty list if error occurs.
        """
        return BaseModel._get_all_pattern(
            table_name=SupplierModel.TABLE_NAME,
            columns=SupplierModel.COLUMNS,
            entity_name=SupplierModel.ENTITY_NAME,
            row_mapper=SupplierModel._map_row,
            order_by=SupplierModel.ID_COLUMN,
        )

    @staticmethod
    def search_by_supplier_id(supplier_id: int) -> list[tuple]:
        """
        Searches for a supplier by its ID.
        Args:
            supplier_id: The ID of the supplier to search for.
        Returns:
            list[tuple]: A list containing a tuple with supplier information if found, otherwise an empty list.
        """
        return BaseModel._search_by_id_pattern(
            table_name=SupplierModel.TABLE_NAME,
            columns=SupplierModel.COLUMNS,
            id_column=SupplierModel.ID_COLUMN,
            entity_id=supplier_id,
            entity_name=SupplierModel.ENTITY_NAME,
            row_mapper=SupplierModel._map_row,
        )

    @staticmethod
    def search_by_supplier_name(supplier_name: str) -> list[tuple]:
        """
        Searches for suppliers by their name using a case-insensitive partial match.
        Args:
            supplier_name: The name (or partial name) of the supplier to search for.
        Returns:
            list[tuple]: A list of tuples containing supplier information for all matching suppliers.
                Returns empty list if not found or error occurs.
        """
        return BaseModel._search_by_name_pattern(
            table_name=SupplierModel.TABLE_NAME,
            columns=SupplierModel.COLUMNS,
            name_column=SupplierModel.NAME_COLUMN,
            search_term=supplier_name,
            entity_name=SupplierModel.ENTITY_NAME,
            row_mapper=SupplierModel._map_row,
            order_by=SupplierModel.NAME_COLUMN,
        )
