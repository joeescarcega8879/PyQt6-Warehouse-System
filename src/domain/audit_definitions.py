from enum import StrEnum

class AuditDefinition(StrEnum):

    MATERIALS_CREATED = "materials.created"
    MATERIALS_EDITED = "materials.edited"
    MATERIALS_DELETED = "materials.deleted"

    PRODUCTION_REQUESTS_CREATED = "production.requests.created"
    PRODUCTION_REQUESTS_EDITED = "production.requests.edited"
    PRODUCTION_REQUESTS_SUBMITTED = "production.requests.submitted"
    PRODUCTION_REQUESTS_REJECTED = "production.requests.rejected"
    PRODUCTION_REQUESTS_CANCELED = "production.requests.canceled"
    PRODUCTION_REQUESTS_APPROVED = "production.requests.approved"
    PRODUCTION_REQUESTS_VIEWED = "production.requests.viewed"
    PRODUCTION_REQUESTS_DEACTIVATED = "production.requests.deactivated"
    PRODUCTION_REQUESTS_DENIED = "production.requests.denied"

    USERS_CREATED = "users.created"
    USERS_EDITED = "users.edited"
    USERS_PASSWORD_CHANGED = "users.password.changed"

    PRODUCTION_LINES_CREATED = "production.lines.created"
    PRODUCTION_LINES_EDITED = "production.lines.edited"

    RECEIPTS_CREATED = "receipts.created"
    RECEIPTS_EDITED = "receipts.edited"
    RECEIPTS_DELETED = "receipts.deleted"

    SUPPLIERS_CREATED = "suppliers.created"
    SUPPLIERS_EDITED = "suppliers.edited"
    SUPPLIERS_DELETED = "suppliers.deleted"
    
    GENERIC_ENTITY_DENIED = "generic.entity.denied"
    