from __future__ import annotations

from config.logger_config import logger
from database.query_helper import QueryHelper, DatabaseError


class SupplierReceiptModel:
    """Model class for managing supplier receipts in the database."""

    @staticmethod
    def add_receipt(
        material_id: int,
        supplier_name: str,
        quantity_received: float,
        created_by: int,
        receipt_timestamp: str | None = None,
        notes: str | None = None,
    ) -> tuple[bool, str | None, int | None]:
        """Insert a new supplier receipt.

        Args:
            material_id: Related material id.
            supplier_name: Supplier name.
            quantity_received: Quantity received.
            created_by: User ID who created the receipt.
            receipt_timestamp: Timestamp value (or None to default to NOW()).
            notes: Optional notes.

        Returns:
            (success, error_message, receipt_id)
        """

        try:
            result = QueryHelper.execute(
                """
                INSERT INTO supplier_receipts (
                    material_id,
                    supplier_name,
                    quantity_received,
                    receipt_timestamp,
                    notes,
                    created_by
                )
                VALUES (
                    :material_id,
                    :supplier_name,
                    :quantity_received,
                    COALESCE(:receipt_timestamp, NOW()),
                    :notes,
                    :created_by
                )
                """,
                {
                    "material_id": material_id,
                    "supplier_name": supplier_name,
                    "quantity_received": quantity_received,
                    "receipt_timestamp": receipt_timestamp,
                    "notes": notes,
                    "created_by": created_by,
                },
            )

            receipt_id = result.get("last_insert_id")
            return True, None, int(receipt_id) if receipt_id is not None else None

        except DatabaseError as e:
            logger.error(f"Error adding supplier receipt: {e}")
            return False, str(e), None

        except Exception as e:
            logger.error(f"Unexpected error adding supplier receipt: {e}")
            return False, str(e), None

    @staticmethod
    def update_receipt(
        receipt_id: int,
        material_id: int,
        supplier_name: str,
        quantity_received: float,
        receipt_timestamp: str | None,
        notes: str | None,
    ) -> tuple[bool, str | None]:
        """Update an existing supplier receipt.
        
        Note: created_by field is intentionally not updated to preserve audit trail.
        """

        try:
            result = QueryHelper.execute(
                """
                UPDATE supplier_receipts
                SET material_id = :material_id,
                    supplier_name = :supplier_name,
                    quantity_received = :quantity_received,
                    receipt_timestamp = :receipt_timestamp,
                    notes = :notes
                WHERE receipt_id = :receipt_id
                """,
                {
                    "receipt_id": receipt_id,
                    "material_id": material_id,
                    "supplier_name": supplier_name,
                    "quantity_received": quantity_received,
                    "receipt_timestamp": receipt_timestamp,
                    "notes": notes,
                },
            )

            if result.get("rows_affected", 0) != 1:
                return False, "Receipt not found."

            return True, None

        except DatabaseError as e:
            logger.error(f"Error updating supplier receipt {receipt_id}: {e}")
            return False, str(e)

        except Exception as e:
            logger.error(f"Unexpected error updating supplier receipt {receipt_id}: {e}")
            return False, str(e)

    @staticmethod
    def delete_receipt(receipt_id: int) -> tuple[bool, str | None]:
        """Delete a supplier receipt."""

        try:
            result = QueryHelper.execute(
                """
                DELETE FROM supplier_receipts
                WHERE receipt_id = :receipt_id
                """,
                {"receipt_id": receipt_id},
            )

            if result.get("rows_affected", 0) != 1:
                return False, "Receipt not found."

            return True, None

        except DatabaseError as e:
            logger.error(f"Error deleting supplier receipt {receipt_id}: {e}")
            return False, str(e)

        except Exception as e:
            logger.error(f"Unexpected error deleting supplier receipt {receipt_id}: {e}")
            return False, str(e)

    @staticmethod
    def get_all_receipts() -> list[tuple]:
        """Return all receipts ordered by newest first."""

        try:
            rows = QueryHelper.fetch_all(
                """
                SELECT receipt_id, material_id, supplier_name, quantity_received, receipt_timestamp, notes, created_by
                FROM supplier_receipts
                ORDER BY receipt_id DESC
                """
            )

            return [
                (
                    row["receipt_id"],
                    row["material_id"],
                    row["supplier_name"],
                    row["quantity_received"],
                    row["receipt_timestamp"],
                    row["notes"],
                    row["created_by"],
                )
                for row in rows
            ]

        except DatabaseError as e:
            logger.error(f"Error retrieving supplier receipts: {e}")
            return []

        except Exception as e:
            logger.error(f"Unexpected error retrieving supplier receipts: {e}")
            return []

    @staticmethod
    def search_by_id(receipt_id: int) -> tuple | None:
        """Search receipt by receipt_id.
        
        Args:
            receipt_id: The receipt ID to search for.
            
        Returns:
            A tuple containing (receipt_id, material_id, supplier_name, quantity_received, 
            receipt_timestamp, notes, created_by) if found, None otherwise.
        """

        try:
            row = QueryHelper.fetch_one(
                """
                SELECT receipt_id, material_id, supplier_name, quantity_received, receipt_timestamp, notes, created_by
                FROM supplier_receipts
                WHERE receipt_id = :receipt_id
                """,
                {"receipt_id": receipt_id},
            )

            if row:
                return (
                    row["receipt_id"],
                    row["material_id"],
                    row["supplier_name"],
                    row["quantity_received"],
                    row["receipt_timestamp"],
                    row["notes"],
                    row["created_by"],
                )
            
            return None

        except DatabaseError as e:
            logger.error(f"Error searching supplier receipt by id {receipt_id}: {e}")
            return None

        except Exception as e:
            logger.error(f"Unexpected error searching supplier receipt by id {receipt_id}: {e}")
            return None

    @staticmethod
    def search_by_supplier_name(supplier_name: str) -> list[tuple]:
        """Search receipts by supplier name (ILIKE match)."""

        try:
            rows = QueryHelper.fetch_all(
                """
                SELECT receipt_id, material_id, supplier_name, quantity_received, receipt_timestamp, notes, created_by
                FROM supplier_receipts
                WHERE supplier_name ILIKE :supplier_name
                ORDER BY receipt_id DESC
                """,
                {"supplier_name": f"%{supplier_name}%"},
            )

            return [
                (
                    row["receipt_id"],
                    row["material_id"],
                    row["supplier_name"],
                    row["quantity_received"],
                    row["receipt_timestamp"],
                    row["notes"],
                    row["created_by"],
                )
                for row in rows
            ]

        except DatabaseError as e:
            logger.error(f"Error searching supplier receipts by supplier '{supplier_name}': {e}")
            return []

        except Exception as e:
            logger.error(f"Unexpected error searching supplier receipts by supplier '{supplier_name}': {e}")
            return []

