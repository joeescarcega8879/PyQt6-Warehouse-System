# Database Migrations

This directory contains SQL migration scripts for the database schema.

## Running Migrations

### Manual Migration

Connect to your PostgreSQL database and run the migration files in order:

```bash
psql -U your_username -d inventory_production_db -f 001_create_login_attempts.sql
```

### Using psql with .env credentials

```bash
# Load environment variables
export $(cat ../.env | grep -v '^#' | xargs)

# Run migration
psql -h $DB_HOST -p $DB_PORT -U $DB_USER -d $DB_NAME -f 001_create_login_attempts.sql
```

## Migration List

| # | Name | Description | Date |
|---|------|-------------|------|
| 001 | create_login_attempts | Creates login_attempts table for rate limiting | 2026-03-06 |

## Creating New Migrations

When creating a new migration:

1. Name it with incrementing number: `XXX_description.sql`
2. Include rollback instructions in comments
3. Update this README with the new migration
4. Test on development database first

## Rollback

To rollback the login_attempts table:

```sql
DROP TABLE IF EXISTS login_attempts;
```
