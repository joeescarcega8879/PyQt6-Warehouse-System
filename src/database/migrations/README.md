# Database Migrations

This directory contains SQL migration scripts for the database schema.

## Running Migrations

### Manual Migration

Connect to your PostgreSQL database and run the migration files in order:

```bash
psql -U your_username -d inventory_production_db -f 001_create_login_attempts.sql
psql -U your_username -d inventory_production_db -f 002_refactor_supplier_receipts.sql
```

### Using psql with .env credentials

```bash
# Load environment variables
export $(cat ../.env | grep -v '^#' | xargs)

# Run migrations in order
psql -h $DB_HOST -p $DB_PORT -U $DB_USER -d $DB_NAME -f 001_create_login_attempts.sql
psql -h $DB_HOST -p $DB_PORT -U $DB_USER -d $DB_NAME -f 002_refactor_supplier_receipts.sql
```

## Migration List

| # | Name | Description | Date |
|---|------|-------------|------|
| 001 | create_login_attempts | Creates login_attempts table for rate limiting | 2026-03-06 |
| 002 | refactor_supplier_receipts | Replaces supplier_name (text) with supplier_id FK to suppliers table | 2026-03-15 |

## Creating New Migrations

When creating a new migration:

1. Name it with incrementing number: `XXX_description.sql`
2. Include rollback instructions in comments
3. Update this README with the new migration
4. Test on development database first

## Rollback

To rollback migration 002 (restores supplier_name column):

```sql
BEGIN;
ALTER TABLE supplier_receipts ADD COLUMN supplier_name VARCHAR(255);
UPDATE supplier_receipts sr
    SET supplier_name = s.supplier_name
    FROM suppliers s
    WHERE sr.supplier_id = s.supplier_id;
ALTER TABLE supplier_receipts DROP CONSTRAINT fk_supplier_receipts_supplier;
DROP INDEX IF EXISTS idx_supplier_receipts_supplier_id;
ALTER TABLE supplier_receipts DROP COLUMN supplier_id;
COMMIT;
```

To rollback migration 001:

```sql
DROP TABLE IF EXISTS login_attempts;
```
