from config.logger_config import logger
from database.query_helper import QueryHelper, DatabaseError

class SupplierModel:
    """Model class for managing suppliers in the database."""

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
            tuple[bool, str | None, int | None]: A tuple containing a boolean indicating success,
            an optional error message, and the ID of the created supplier if successful.
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
            logger.error(f"Error adding supplier: {e}")
            return False, str(e), None
       except Exception as e:
            logger.error(f"Unexpected error adding supplier: {e}")
            return False, str(e), None
     
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
            (success, error_message)
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
               return False, "Supplier not found or no changes made."
          return True, None
     
        except DatabaseError as e:
            logger.error(f"Error updating supplier: {e}")
            return False, str(e)
        except Exception as e:
            logger.error(f"Unexpected error updating supplier: {e}")
            return False, str(e)
       
    @staticmethod
    def get_all_suppliers() -> list[tuple]:
        """
        Retrieves all suppliers from the database.

        Returns:
            A list of tuples containing supplier information.
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
            logger.error(f"Error retrieving suppliers: {e}")
            return []
        
        except Exception as e:
            logger.error(f"Unexpected error retrieving suppliers: {e}")
            return []
       
    @staticmethod
    def search_by_supplier_id(supplier_id: int) -> tuple | None:
          """
          Searches for a supplier by its ID.
          Args:
               supplier_id: The ID of the supplier to search for.
          Returns:
                    A tuple containing supplier information if found, otherwise None.
          """
     
          try:
               row = QueryHelper.execute(
                    """
                    SELECT supplier_id, supplier_name, contact_department, phone, email, address, notes, is_active
                    FROM suppliers
                    WHERE supplier_id = :supplier_id
                    """,
                    {"supplier_id": supplier_id},
               )
               if row:
                    return (
                         row[0]["supplier_id"],
                         row[0]["supplier_name"],
                         row[0]["contact_department"],
                         row[0]["phone"],
                         row[0]["email"],
                         row[0]["address"],
                         row[0]["notes"],
                         row[0]["is_active"]
                    )
               return None
          except DatabaseError as e:
               logger.error(f"Error searching for supplier by ID: {e}")
               return None
          except Exception as e:
               logger.error(f"Unexpected error searching for supplier by ID: {e}")
               return None
     
    @staticmethod
    def search_by_supplier_name(supplier_name: str) -> list[tuple]:
         """
         Searches for suppliers by their name using a case-insensitive partial match.
         Args:
               supplier_name: The name (or partial name) of the supplier to search for.
         Returns:
               A list of tuples containing supplier information for all matching suppliers.         
         """
         
         try:
              rows = QueryHelper.execute(
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
               logger.error(f"Error searching for supplier by name: {e}")
               return []
         except Exception as e:
               logger.error(f"Unexpected error searching for supplier by name: {e}")
               return []