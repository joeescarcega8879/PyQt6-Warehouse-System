from config.logger_config import logger
from database.query_helper import QueryHelper, DatabaseError
from common.error_messages import ErrorMessages

class SupplierModel:
    """
    Model class for managing suppliers in the database.
    Handles secure error logging and provides generic error messages to users.
    """

    @staticmethod
    def add_supplier(
        supplier_name: str, 
        created_by: int,
        contact_department: str | None,
        phone: str | None = None,
        email: str | None = None,
        address: str | None = None,
        notes: str | None = None,
        is_active: bool = True) -> tuple[bool, str | None, int | None]:
       

       """
       Creates a new supplier in the database.
       args:
            supplier_name (str): The name of the supplier.
            contact_department (str | None): The contact department of the supplier.
            phone (str | None): The phone number of the supplier.
            email (str | None): The email address of the supplier.
            address (str | None): The physical address of the supplier.
            notes (str | None): Additional notes about the supplier.
            is_active (bool): Whether the supplier is active or not. Defaults to True.
    
        returns:
            tuple[bool, str | None, int | None]: (success, error_message, supplier_id)
                - success: True if supplier was created successfully
                - error_message: None if successful, generic error message if failed
                - supplier_id: ID of created supplier if successful, None otherwise
       """

       try:
           result = QueryHelper.execute(
                """
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
                {
                     "supplier_name": supplier_name,
                     "contact_department": contact_department,
                     "phone": phone,
                     "email": email,
                     "address": address,
                     "notes": notes,
                     "is_active": is_active,
                     "created_by": created_by
                },
           )

           supplier_id = result.get("last_insert_id")
           return True, None, int(supplier_id) if supplier_id is not None else None
       
       except DatabaseError as e:
            error_msg = ErrorMessages.log_and_mask_error(
                error=e,
                context=f"adding supplier '{supplier_name}'",
                user_message=ErrorMessages.DATABASE_ERROR
            )
            return False, error_msg, None
       except Exception as e:
            error_msg = ErrorMessages.log_and_mask_error(
                error=e,
                context=f"adding supplier '{supplier_name}'",
                user_message=ErrorMessages.GENERIC_ERROR
            )
            return False, error_msg, None
     
    @staticmethod
    def update_supplier(
        supplier_id: int,
        supplier_name: str,
        contact_department: str | None,
        phone: str | None = None,
        email: str | None = None,
        address: str | None = None,
        notes: str | None = None,
        is_active: bool = True) -> tuple[bool, str | None]:
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
        try:
          result = QueryHelper.execute(
                    """
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
                    {
                         "supplier_id": supplier_id,
                         "supplier_name": supplier_name,
                         "contact_department": contact_department,
                         "phone": phone,
                         "email": email,
                         "address": address,
                         "notes": notes,
                         "is_active": is_active
                    },
          )
          if result.get("rows_affected", 0) != 1:
               logger.warning(f"Supplier not found for update: ID {supplier_id}")
               return False, ErrorMessages.NOT_FOUND
          return True, None
     
        except DatabaseError as e:
            return False, ErrorMessages.log_and_mask_error(
                error=e,
                context=f"updating supplier ID {supplier_id}",
                user_message=ErrorMessages.DATABASE_ERROR
            )
        except Exception as e:
            return False, ErrorMessages.log_and_mask_error(
                error=e,
                context=f"updating supplier ID {supplier_id}",
                user_message=ErrorMessages.GENERIC_ERROR
            )
       
    @staticmethod
    def get_all_suppliers() -> list[tuple]:
        """
        Retrieves all suppliers from the database.

        Returns:
            list[tuple]: A list of tuples containing supplier information.
                Returns empty list if error occurs.
        """
        
        try:
            rows = QueryHelper.fetch_all(
                """
                SELECT supplier_id, supplier_name, contact_department, phone, email, address, notes, is_active
                FROM suppliers
                ORDER BY supplier_id
                """,
            )
            
            return [
                 (
                    row["supplier_id"],
                    row["supplier_name"],
                    row["contact_department"],
                    row["phone"],
                    row["email"],
                    row["address"],
                    row["notes"],
                    row["is_active"]
                 )
                    for row in rows
            ]
        
        except DatabaseError as e:
            ErrorMessages.log_and_mask_error(
                error=e,
                context="retrieving all suppliers",
                user_message=ErrorMessages.DATABASE_ERROR
            )
            return []
        
        except Exception as e:
            ErrorMessages.log_and_mask_error(
                error=e,
                context="retrieving all suppliers",
                user_message=ErrorMessages.GENERIC_ERROR
            )
            return []
       
    @staticmethod
    def search_by_supplier_id(supplier_id: int) -> list[tuple]:
        """
        Searches for a supplier by its ID.
        Args:
            supplier_id: The ID of the supplier to search for.
        Returns:
            list[tuple]: A list containing a tuple with supplier information if found, otherwise an empty list.
        """
    
        try:
            row = QueryHelper.fetch_one(
                """
                SELECT supplier_id, supplier_name, contact_department, phone, email, address, notes, is_active
                FROM suppliers
                WHERE supplier_id = :supplier_id
                """,
                {"supplier_id": supplier_id},
            )
            if row:
                return [
                    (
                        row["supplier_id"],
                        row["supplier_name"],
                        row["contact_department"],
                        row["phone"],
                        row["email"],
                        row["address"],
                        row["notes"],
                        row["is_active"]
                    )
                ]
            return []
        except DatabaseError as e:
            ErrorMessages.log_and_mask_error(
                error=e,
                context=f"searching supplier by ID {supplier_id}",
                user_message=ErrorMessages.DATABASE_ERROR
            )
            return []
        except Exception as e:
            ErrorMessages.log_and_mask_error(
                error=e,
                context=f"searching supplier by ID {supplier_id}",
                user_message=ErrorMessages.GENERIC_ERROR
            )
            return []
     
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
        
        try:
            rows = QueryHelper.fetch_all(
                """
                SELECT supplier_id, supplier_name, contact_department, phone, email, address, notes, is_active
                FROM suppliers
                WHERE supplier_name ILIKE :supplier_name
                ORDER BY supplier_name
                """,
                {"supplier_name": f"%{supplier_name}%"}
            )
            
            return [
                (
                    row["supplier_id"],
                    row["supplier_name"],
                    row["contact_department"],
                    row["phone"],
                    row["email"],
                    row["address"],
                    row["notes"],
                    row["is_active"]
                )
                for row in rows
            ]
        except DatabaseError as e:
            ErrorMessages.log_and_mask_error(
                error=e,
                context=f"searching supplier by name '{supplier_name}'",
                user_message=ErrorMessages.DATABASE_ERROR
            )
            return []
        except Exception as e:
            ErrorMessages.log_and_mask_error(
                error=e,
                context=f"searching supplier by name '{supplier_name}'",
                user_message=ErrorMessages.GENERIC_ERROR
            )
            return []
