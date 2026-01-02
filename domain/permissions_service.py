from domain.permissions import PERMISSIONS

class PermissionService:

   @staticmethod
   def has_permission(user, permission: str) -> bool:
        roles = PERMISSIONS.get(permission, set())
        return user.user_role in roles
