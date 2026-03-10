from __future__ import annotations

from config.logger_config import logger
from database.query_helper import QueryHelper, DatabaseError
from common.error_messages import ErrorMessages
from PyQt6.QtCore import QDateTime

class SupplierReceiptModel:
    """
    Model class for managing supplier receipts in the database.
    Handles secure error logging and provides generic error messages to users.
    """

    @staticmethod
    def _format_timestamp(timestamp) -> str:
        """Convert QDateTime or other timestamp formats to readable string.
        
        Args:
            timestamp: Can be QDateTime, datetime, or string
            
        Returns:
            Formatted string like "2026-03-03 14:30:45" or empty string if None
        """
        if timestamp is None:
            return ""
        
        # If it's a QDateTime object from PyQt6
        if isinstance(timestamp, QDateTime):
            return timestamp.toString("yyyy-MM-dd HH:mm:ss")
        
        # If it's already a string, return as-is
        if isinstance(timestamp, str):
            return timestamp
        
        # For other types (datetime, etc), convert to string
        return str(timestamp)

    @staticmethod
    def add_receipt(
        material_id: int,
        supplier_id: int,
        quantity_received: float,
        created_by: int,
        notes: str | None = None,
    ) -> tuple[bool, str | None, int | None]:
        """Insert a new supplier receipt.

        Args:
            material_id: Related material id.
            supplier_id: Supplier id (foreign key to suppliers table).
            quantity_received: Quantity received.
            created_by: User ID who created the receipt.
            receipt_timestamp: Timestamp value (or None to default to NOW()).
            notes: Optional notes.

        Returns:
            tuple[bool, str | None, int | None]: (success, error_message, receipt_id)
                - success: True if receipt was created successfully
                - error_message: None if successful, generic error message if failed
                - receipt_id: ID of created receipt if successful, None otherwise
        """

        try:
            result = QueryHelper.execute(
                """
                INSERT INTO supplier_receipts (
                    material_id,
                    supplier_id,
                    quantity_received,
                    notes,
                    created_by
                )
                VALUES (
                    :material_id,
                    :supplier_id,
                    :quantity_received,
                    :notes,
                    :created_by
                )
                """,
                {
                    "material_id": material_id,
                    "supplier_id": supplier_id,
                    "quantity_received": quantity_received,
                    "notes": notes,
                    "created_by": created_by,
                },
            )

            receipt_id = result.get("last_insert_id")
            return True, None, int(receipt_id) if receipt_id is not None else None

        except DatabaseError as e:
            error_msg = ErrorMessages.log_and_mask_error(
                error=e,
                context=f"adding supplier receipt for material ID {material_id}",
                user_message=ErrorMessages.DATABASE_ERROR
            )
            return False, error_msg, None

        except Exception as e:
            error_msg = ErrorMessages.log_and_mask_error(
                error=e,
                context=f"adding supplier receipt for material ID {material_id}",
                user_message=ErrorMessages.GENERIC_ERROR
            )
            return False, error_msg, None

    @staticmethod
    def update_receipt(
        receipt_id: int,
        material_id: int,
        supplier_id: int,
        quantity_received: float,
        notes: str | None,
    ) -> tuple[bool, str | None]:
        """Update an existing supplier receipt.
        
        Note: created_by field is intentionally not updated to preserve audit trail.
        
        Args:
            receipt_id: Receipt ID to update.
            material_id: Material ID.
            supplier_id: Supplier ID (foreign key to suppliers table).
            quantity_received: Quantity received.
            notes: Optional notes.
            
        Returns:
            tuple[bool, str | None]: (success, error_message)
                - success: True if receipt was updated successfully
                - error_message: None if successful, generic error message if failed
        """

        try:
            result = QueryHelper.execute(
                """
                UPDATE supplier_receipts
                SET material_id = :material_id,
                    supplier_id = :supplier_id,
                    quantity_received = :quantity_received,
                    notes = :notes
                WHERE receipt_id = :receipt_id
                """,
                {
                    "receipt_id": receipt_id,
                    "material_id": material_id,
                    "supplier_id": supplier_id,
                    "quantity_received": quantity_received,
                    "notes": notes,
                },
            )

            if result.get("rows_affected", 0) != 1:
                logger.warning(f"Supplier receipt not found for update: ID {receipt_id}")
                return False, ErrorMessages.NOT_FOUND

            return True, None

        except DatabaseError as e:
            return False, ErrorMessages.log_and_mask_error(
                error=e,
                context=f"updating supplier receipt ID {receipt_id}",
                user_message=ErrorMessages.DATABASE_ERROR
            )

        except Exception as e:
            return False, ErrorMessages.log_and_mask_error(
                error=e,
                context=f"updating supplier receipt ID {receipt_id}",
                user_message=ErrorMessages.GENERIC_ERROR
            )

    @staticmethod
    def delete_receipt(receipt_id: int) -> tuple[bool, str | None]:
        """Delete a supplier receipt.
        
        Returns:
            tuple[bool, str | None]: (success, error_message)
                - success: True if receipt was deleted successfully
                - error_message: None if successful, generic error message if failed
        """

        try:
            result = QueryHelper.execute(
                """
                DELETE FROM supplier_receipts
                WHERE receipt_id = :receipt_id
                """,
                {"receipt_id": receipt_id},
            )

            if result.get("rows_affected", 0) != 1:
                logger.warning(f"Supplier receipt not found for deletion: ID {receipt_id}")
                return False, ErrorMessages.NOT_FOUND

            return True, None

        except DatabaseError as e:
            return False, ErrorMessages.log_and_mask_error(
                error=e,
                context=f"deleting supplier receipt ID {receipt_id}",
                user_message=ErrorMessages.DATABASE_ERROR
            )

        except Exception as e:
            return False, ErrorMessages.log_and_mask_error(
                error=e,
                context=f"deleting supplier receipt ID {receipt_id}",
                user_message=ErrorMessages.GENERIC_ERROR
            )

    @staticmethod
    def get_all_receipts() -> list[tuple]:
        """Return all receipts ordered by newest first.
        
        Returns:
            list[tuple]: A list of tuples containing (receipt_id, material_id, supplier_id,
                supplier_name, quantity_received, receipt_timestamp, notes, created_by).
                Returns empty list if error occurs.
        """

        try:
            rows = QueryHelper.fetch_all(
                """
                SELECT 
                    sr.receipt_id, 
                    sr.material_id, 
                    sr.supplier_id,
                    s.supplier_name,
                    sr.quantity_received, 
                    sr.receipt_timestamp, 
                    sr.notes, 
                    sr.created_by
                FROM supplier_receipts sr
                LEFT JOIN suppliers s ON sr.supplier_id = s.supplier_id
                ORDER BY sr.receipt_id DESC
                """
            )

            return [
                (
                    row["receipt_id"],
                    row["material_id"],
                    row["supplier_id"],
                    row["supplier_name"] or "Unknown Supplier",  # Handle NULL supplier_name
                    row["quantity_received"],
                    SupplierReceiptModel._format_timestamp(row["receipt_timestamp"]),
                    row["notes"],
                    row["created_by"],
                )
                for row in rows
            ]

        except DatabaseError as e:
            ErrorMessages.log_and_mask_error(
                error=e,
                context="retrieving all supplier receipts",
                user_message=ErrorMessages.DATABASE_ERROR
            )
            return []

        except Exception as e:
            ErrorMessages.log_and_mask_error(
                error=e,
                context="retrieving all supplier receipts",
                user_message=ErrorMessages.GENERIC_ERROR
            )
            return []

    @staticmethod
    def search_by_id(receipt_id: int) -> tuple | None:
        """Search receipt by receipt_id.
        
        Args:
            receipt_id: The receipt ID to search for.
            
        Returns:
            A tuple containing (receipt_id, material_id, supplier_id, supplier_name,
            quantity_received, receipt_timestamp, notes, created_by) if found, None otherwise.
        """

        try:
            row = QueryHelper.fetch_one(
                """
                SELECT 
                    sr.receipt_id, 
                    sr.material_id, 
                    sr.supplier_id,
                    s.supplier_name,
                    sr.quantity_received, 
                    sr.receipt_timestamp, 
                    sr.notes, 
                    sr.created_by
                FROM supplier_receipts sr
                LEFT JOIN suppliers s ON sr.supplier_id = s.supplier_id
                WHERE sr.receipt_id = :receipt_id
                """,
                {"receipt_id": receipt_id},
            )

            if row:
                return (
                    row["receipt_id"],
                    row["material_id"],
                    row["supplier_id"],
                    row["supplier_name"] or "Unknown Supplier",  # Handle NULL supplier_name
                    row["quantity_received"],
                    SupplierReceiptModel._format_timestamp(row["receipt_timestamp"]),
                    row["notes"],
                    row["created_by"],
                )
            
            return None

        except DatabaseError as e:
            ErrorMessages.log_and_mask_error(
                error=e,
                context=f"searching supplier receipt by ID {receipt_id}",
                user_message=ErrorMessages.DATABASE_ERROR
            )
            return None

        except Exception as e:
            ErrorMessages.log_and_mask_error(
                error=e,
                context=f"searching supplier receipt by ID {receipt_id}",
                user_message=ErrorMessages.GENERIC_ERROR
            )
            return None

    @staticmethod
    def search_by_supplier_name(supplier_name: str) -> list[tuple]:
        """Search receipts by supplier name (ILIKE match on suppliers table).
        
        Args:
            supplier_name: Supplier name or part of name to search for.
            
        Returns:
            list[tuple]: A list of tuples containing (receipt_id, material_id, supplier_id,
                supplier_name, quantity_received, receipt_timestamp, notes, created_by).
                Returns empty list if not found or error occurs.
        """

        try:
            rows = QueryHelper.fetch_all(
                """
                SELECT 
                    sr.receipt_id, 
                    sr.material_id, 
                    sr.supplier_id,
                    s.supplier_name,
                    sr.quantity_received, 
                    sr.receipt_timestamp, 
                    sr.notes, 
                    sr.created_by
                FROM supplier_receipts sr
                LEFT JOIN suppliers s ON sr.supplier_id = s.supplier_id
                WHERE s.supplier_name ILIKE :supplier_name
                ORDER BY sr.receipt_id DESC
                """,
                {"supplier_name": f"%{supplier_name}%"},
            )

            return [
                (
                    row["receipt_id"],
                    row["material_id"],
                    row["supplier_id"],
                    row["supplier_name"] or "Unknown Supplier",  # Handle NULL supplier_name
                    row["quantity_received"],
                    SupplierReceiptModel._format_timestamp(row["receipt_timestamp"]),
                    row["notes"],
                    row["created_by"],
                )
                for row in rows
            ]

        except DatabaseError as e:
            ErrorMessages.log_and_mask_error(
                error=e,
                context=f"searching supplier receipts by supplier name '{supplier_name}'",
                user_message=ErrorMessages.DATABASE_ERROR
            )
            return []

        except Exception as e:
            ErrorMessages.log_and_mask_error(
                error=e,
                context=f"searching supplier receipts by supplier name '{supplier_name}'",
                user_message=ErrorMessages.GENERIC_ERROR
            )
            return []
