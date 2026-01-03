from enum import StrEnum

class AuditDefinition(StrEnum):

    MATERIALS_CREATED = "materials.created"
    MATERIALS_EDITED = "materials.edited"
    MATERIALS_DELETED = "materials.deleted"

    PRODUCTION_REQUESTS_CREATED = "production.requests.created"
    PRODUCTION_REQUESTS_APPROVED = "production.requests.approved"
    PRODUCTION_REQUESTS_VIEWED = "production.requests.viewed"

    USERS_CREATED = "users.created"
    USERS_EDITED = "users.edited"
    USERS_PASSWORD_CHANGED = "users.password.changed"