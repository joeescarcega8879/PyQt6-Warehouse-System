from src.domain.roles import UserRole
from src.domain.permissions_definitions import Permission

PERMISSIONS = {
    Permission.MATERIALS_CREATE: {UserRole.ADMIN, UserRole.SUPERVISOR},
    Permission.MATERIALS_EDIT: {UserRole.ADMIN, UserRole.SUPERVISOR},
    Permission.MATERIALS_DELETE: {UserRole.ADMIN, UserRole.SUPERVISOR},

    Permission.PRODUCTION_REQUESTS_CREATE: {UserRole.ADMIN, UserRole.SUPERVISOR, UserRole.LEADER},
    Permission.PRODUCTION_REQUESTS_EDIT: {UserRole.ADMIN, UserRole.SUPERVISOR, UserRole.LEADER},
    Permission.PRODUCTION_REQUESTS_SUBMIT: {UserRole.ADMIN, UserRole.SUPERVISOR, UserRole.LEADER},
    Permission.PRODUCTION_REQUESTS_APPROVE: {UserRole.ADMIN, UserRole.SUPERVISOR},
    Permission.PRODUCTION_REQUESTS_VIEW: {UserRole.ADMIN, UserRole.SUPERVISOR, UserRole.LEADER, UserRole.VIEWER},
    Permission.PRODUCTION_REQUESTS_DEACTIVATE: {UserRole.ADMIN, UserRole.SUPERVISOR},

    Permission.USERS_CREATE: {UserRole.ADMIN, UserRole.SUPERVISOR},
    Permission.USERS_EDIT: {UserRole.ADMIN, UserRole.SUPERVISOR},
    Permission.USERS_CHANGE_PASSWORD: {UserRole.ADMIN, UserRole.SUPERVISOR},

    Permission.PRODUCTION_LINES_CREATE: {UserRole.ADMIN, UserRole.SUPERVISOR},
    Permission.PRODUCTION_LINES_EDIT: {UserRole.ADMIN, UserRole.SUPERVISOR},
    Permission.PRODUCTION_LINES_VIEW: {UserRole.ADMIN, UserRole.SUPERVISOR, UserRole.LEADER, UserRole.VIEWER},

    Permission.RECEIPTS_CREATE: {UserRole.ADMIN, UserRole.SUPERVISOR, UserRole.LEADER},
    Permission.RECEIPTS_EDIT: {UserRole.ADMIN, UserRole.SUPERVISOR},
    Permission.RECEIPTS_DELETE: {UserRole.ADMIN, UserRole.SUPERVISOR},

    Permission.SUPPLIER_CREATE: {UserRole.ADMIN, UserRole.SUPERVISOR},
    Permission.SUPPLIER_EDIT: {UserRole.ADMIN, UserRole.SUPERVISOR},
    

}

