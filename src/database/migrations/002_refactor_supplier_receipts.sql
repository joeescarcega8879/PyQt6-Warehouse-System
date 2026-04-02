-- Migration 002: Refactor supplier_receipts table
-- Replaces the supplier_name text column with a supplier_id FK referencing suppliers table.
-- Safe to run on empty table; includes a fallback UPDATE for tables with existing data.

BEGIN;

-- Step 1: Add supplier_id column (nullable initially to allow data backfill)
ALTER TABLE supplier_receipts
    ADD COLUMN supplier_id INTEGER;

-- Step 2: Backfill supplier_id from existing supplier_name values (if any rows exist)
UPDATE supplier_receipts sr
SET supplier_id = s.supplier_id
FROM suppliers s
WHERE s.supplier_name = sr.supplier_name;

-- Step 3: Add FK constraint
ALTER TABLE supplier_receipts
    ADD CONSTRAINT fk_supplier_receipts_supplier_id
    FOREIGN KEY (supplier_id) REFERENCES suppliers(supplier_id) ON DELETE RESTRICT;

-- Step 4: Drop the old supplier_name column
ALTER TABLE supplier_receipts
    DROP COLUMN supplier_name;

-- Step 5: Add index for performance
CREATE INDEX idx_supplier_receipts_supplier_id ON supplier_receipts(supplier_id);

COMMIT;
