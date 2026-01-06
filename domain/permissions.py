from domain.roles import UserRole
from domain.permissions_definitions import Permission

PERMISSIONS = {
    Permission.MATERIALS_CREATE: {UserRole.ADMIN, UserRole.SUPERVISOR},
    Permission.MATERIALS_EDIT: {UserRole.ADMIN, UserRole.SUPERVISOR},
    Permission.MATERIALS_DELETE: {UserRole.ADMIN, UserRole.SUPERVISOR},

    Permission.PRODUCTION_REQUESTS_CREATE: {UserRole.ADMIN, UserRole.SUPERVISOR, UserRole.LEADER},
    Permission.PRODUCTION_REQUESTS_APPROVE: {UserRole.ADMIN, UserRole.SUPERVISOR},
    Permission.PRODUCTION_REQUESTS_VIEW: {UserRole.ADMIN, UserRole.SUPERVISOR, UserRole.LEADER, UserRole.VIEWER},

    Permission.USERS_CREATE: {UserRole.ADMIN, UserRole.SUPERVISOR},
    Permission.USERS_EDIT: {UserRole.ADMIN, UserRole.SUPERVISOR},
    Permission.USERS_CHANGE_PASSWORD: {UserRole.ADMIN, UserRole.SUPERVISOR},

    Permission.PRODUCTION_LINES_CREATE: {UserRole.ADMIN, UserRole.SUPERVISOR},
    Permission.PRODUCTION_LINES_EDIT: {UserRole.ADMIN, UserRole.SUPERVISOR},
    Permission.PRODUCTION_LINES_VIEW: {UserRole.ADMIN, UserRole.SUPERVISOR, UserRole.LEADER, UserRole.VIEWER},



}

