from enum import Enum

class UserRole(str, Enum):
    ADMIN = "admin"
    SUPERVISOR = "supervisor"
    LEADER = "leader"
    OPERATOR = "operator"
    VIEWER = "viewer"