from __future__ import annotations

from models.base_model import BaseModel
from PyQt6.QtCore import QDateTime


class SupplierReceiptModel(BaseModel):
    """
    Model class for managing supplier receipts in the database.
    Handles secure error logging and provides generic error messages to users.
    """

    ENTITY_NAME = "supplier receipt"

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
    def _map_row(row: dict) -> tuple:
        return (
            row["receipt_id"],
            row["material_id"],
            row["supplier_id"],
            row["supplier_name"] or "Unknown Supplier",
            row["quantity_received"],
            SupplierReceiptModel._format_timestamp(row["receipt_timestamp"]),
            row["notes"],
            row["created_by"],
        )

    _RECEIPT_COLUMNS = """
        sr.receipt_id,
        sr.material_id,
        sr.supplier_id,
        s.supplier_name,
        sr.quantity_received,
        sr.receipt_timestamp,
        sr.notes,
        sr.created_by
    """

    _RECEIPT_FROM = """
        FROM supplier_receipts sr
        LEFT JOIN suppliers s ON sr.supplier_id = s.supplier_id
    """

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
            notes: Optional notes.

        Returns:
            tuple[bool, str | None, int | None]: (success, error_message, receipt_id)
                - success: True if receipt was created successfully
                - error_message: None if successful, generic error message if failed
                - receipt_id: ID of created receipt if successful, None otherwise
        """
        return BaseModel._execute_insert(
            sql="""
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
            params={
                "material_id": material_id,
                "supplier_id": supplier_id,
                "quantity_received": quantity_received,
                "notes": notes,
                "created_by": created_by,
            },
            entity_name=SupplierReceiptModel.ENTITY_NAME,
            context=f"adding supplier receipt for material ID {material_id}",
        )

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
        return BaseModel._execute_update(
            sql="""
                UPDATE supplier_receipts
                SET material_id = :material_id,
                    supplier_id = :supplier_id,
                    quantity_received = :quantity_received,
                    notes = :notes
                WHERE receipt_id = :receipt_id
                """,
            params={
                "receipt_id": receipt_id,
                "material_id": material_id,
                "supplier_id": supplier_id,
                "quantity_received": quantity_received,
                "notes": notes,
            },
            entity_name=SupplierReceiptModel.ENTITY_NAME,
            entity_id=receipt_id,
            context=f"updating supplier receipt ID {receipt_id}",
        )

    @staticmethod
    def delete_receipt(receipt_id: int) -> tuple[bool, str | None]:
        """Delete a supplier receipt.
        
        Returns:
            tuple[bool, str | None]: (success, error_message)
                - success: True if receipt was deleted successfully
                - error_message: None if successful, generic error message if failed
        """
        return BaseModel._execute_delete(
            sql="""
                DELETE FROM supplier_receipts
                WHERE receipt_id = :receipt_id
                """,
            params={"receipt_id": receipt_id},
            entity_name=SupplierReceiptModel.ENTITY_NAME,
            entity_id=receipt_id,
            context=f"deleting supplier receipt ID {receipt_id}",
        )

    @staticmethod
    def get_all_receipts() -> list[tuple]:
        """Return all receipts ordered by newest first.
        
        Returns:
            list[tuple]: A list of tuples containing (receipt_id, material_id, supplier_id,
                supplier_name, quantity_received, receipt_timestamp, notes, created_by).
                Returns empty list if error occurs.
        """
        rows = BaseModel._fetch_all_safe(
            sql=f"""
                SELECT {SupplierReceiptModel._RECEIPT_COLUMNS}
                {SupplierReceiptModel._RECEIPT_FROM}
                ORDER BY sr.receipt_id DESC
                """,
            params=None,
            context="retrieving all supplier receipts",
        )
        return [SupplierReceiptModel._map_row(row) for row in rows]

    @staticmethod
    def search_by_id(receipt_id: int) -> tuple | None:
        """Search receipt by receipt_id.
        
        Args:
            receipt_id: The receipt ID to search for.
            
        Returns:
            A tuple containing (receipt_id, material_id, supplier_id, supplier_name,
            quantity_received, receipt_timestamp, notes, created_by) if found, None otherwise.
        """
        row = BaseModel._fetch_one_safe(
            sql=f"""
                SELECT {SupplierReceiptModel._RECEIPT_COLUMNS}
                {SupplierReceiptModel._RECEIPT_FROM}
                WHERE sr.receipt_id = :receipt_id
                """,
            params={"receipt_id": receipt_id},
            context=f"searching supplier receipt by ID {receipt_id}",
        )
        return SupplierReceiptModel._map_row(row) if row else None

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
        rows = BaseModel._fetch_all_safe(
            sql=f"""
                SELECT {SupplierReceiptModel._RECEIPT_COLUMNS}
                {SupplierReceiptModel._RECEIPT_FROM}
                WHERE s.supplier_name ILIKE :supplier_name
                ORDER BY sr.receipt_id DESC
                """,
            params={"supplier_name": f"%{supplier_name}%"},
            context=f"searching supplier receipts by supplier name '{supplier_name}'",
        )
        return [SupplierReceiptModel._map_row(row) for row in rows]
