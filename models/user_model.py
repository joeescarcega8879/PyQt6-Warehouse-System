import bcrypt
import logging
from dataclasses import dataclass
from database.query_helper import QueryHelper, DatabaseError
from common.error_messages import ErrorMessages

logger = logging.getLogger(__name__)

@dataclass
class AuthenticatedUser:
    """Data class representing an authenticated user."""
    user_id: int
    username: str
    user_role: str

class UserModel:
    """
    Class responsible for data logic and user authentication.
    Handles secure error logging and provides generic error messages to users.
    """

    @staticmethod
    def authenticate_user(username: str, password: str) -> tuple[AuthenticatedUser | None, str | None]:
        """
        Authenticates a user with the given username and password.
        
        Returns:
            tuple[AuthenticatedUser | None, str | None]: (user, error_message)
                - user: AuthenticatedUser object if successful, None otherwise
                - error_message: None if successful, generic error message if failed
        """
        try:
            row = QueryHelper.fetch_one(
                """
                SELECT user_id, username, password_hash, user_role
                FROM users
                WHERE username = :username AND is_active = TRUE
                """,
                {"username": username},
            )
        except Exception as e:
            error_msg = ErrorMessages.log_and_mask_error(
                error=e,
                context=f"authenticating user '{username}'",
                user_message=ErrorMessages.AUTHENTICATION_ERROR
            )
            return None, error_msg

        if not row:
            # Use generic authentication error - don't reveal if user exists
            return None, ErrorMessages.LOGIN_FAILED

        stored_hash = row["password_hash"]
        stored_hash_bytes = stored_hash.encode("utf-8") if isinstance(stored_hash, str) else bytes(stored_hash)

        if not bcrypt.checkpw(password.encode("utf-8"), stored_hash_bytes):
            # Use generic authentication error - don't reveal password is wrong
            return None, ErrorMessages.LOGIN_FAILED

        return AuthenticatedUser(
            user_id=row["user_id"],
            username=row["username"],
            user_role=row["user_role"],
        ), None

    @staticmethod
    def create_user(username: str, password: str, full_name: str, user_role: str, is_active: bool = True) -> tuple[bool, str | None]:
        """
        Creates a new user in the database.
        
        Returns:
            tuple[bool, str | None]: (success, error_message)
                - success: True if user was created successfully
                - error_message: None if successful, generic error message if failed
        """

        if not username or not password or not full_name or not user_role:
            return False, ErrorMessages.VALIDATION_ERROR
        
        try:
            existing = QueryHelper.fetch_one(
                "SELECT 1 FROM users WHERE username = :username",
                {"username": username},
            )
            if existing:
                return False, ErrorMessages.DUPLICATE_ERROR
            
            password_hash = bcrypt.hashpw(password.encode("utf-8"), bcrypt.gensalt(),).decode("utf-8")

            QueryHelper.begin_transaction()
            QueryHelper.execute(
                """
                INSERT INTO users (username, password_hash, full_name, user_role, is_active)
                VALUES (:username, :password_hash, :full_name, :user_role, :is_active)
                """,
                {
                    "username": username,
                    "password_hash": password_hash,
                    "full_name": full_name,
                    "user_role": user_role,
                    "is_active": is_active,
                },
            )

            QueryHelper.commit()
            return True, None
        
        except DatabaseError as e:
            QueryHelper.rollback()
            return False, ErrorMessages.log_and_mask_error(
                error=e,
                context=f"creating user '{username}'",
                user_message=ErrorMessages.DATABASE_ERROR
            )
        except Exception as e:
            QueryHelper.rollback()
            return False, ErrorMessages.log_and_mask_error(
                error=e,
                context=f"creating user '{username}'",
                user_message=ErrorMessages.GENERIC_ERROR
            )

    @staticmethod
    def update_user_info(user_id: int, username: str, full_name: str, user_role: str, is_active: bool) -> tuple[bool, str | None]:
        """
        Updates an existing user's information in the database.
        args:
            user_id (int): The ID of the user to update.
            username (str): The new username.
            full_name (str): The new full name.
            user_role (str): The new user role.
            is_active (bool): The new active status.
        Returns:
            tuple[bool, str | None]: (success, error_message)
                - success: True if user was updated successfully
                - error_message: None if successful, generic error message if failed
        """
        
        try:
            result = QueryHelper.execute(
                """
                UPDATE users
                SET username = :username,
                    full_name = :full_name,
                    user_role = :user_role,
                    is_active = :is_active
                WHERE user_id = :user_id
                """,
                {
                    "user_id": user_id,
                    "username": username,
                    "full_name": full_name,
                    "user_role": user_role,
                    "is_active": is_active,
                },
            )
           
            if result.get("rows_affected", 0) != 1:
                logger.warning(f"User not found for update: ID {user_id}")
                return False, ErrorMessages.NOT_FOUND
            return True, None
        
        except DatabaseError as e:
            return False, ErrorMessages.log_and_mask_error(
                error=e,
                context=f"updating user ID {user_id}",
                user_message=ErrorMessages.DATABASE_ERROR
            )
        except Exception as e:
            return False, ErrorMessages.log_and_mask_error(
                error=e,
                context=f"updating user ID {user_id}",
                user_message=ErrorMessages.GENERIC_ERROR
            )

    @staticmethod
    def get_all_users(include_inactive: bool = True) -> tuple[list[tuple], str | None]:
        """
        Retrieves all users from the database.
        
        Returns:
            tuple[list[tuple], str | None]: (users, error_message)
                - users: List of user tuples if successful, empty list if error
                - error_message: None if successful, generic error message if failed
        """
        try:
            sql = """
                SELECT user_id, username, full_name, user_role, is_active
                FROM users
            """

            params = None
            if not include_inactive:
                sql += " WHERE is_active = TRUE"

            sql += " ORDER BY user_id ASC"

            rows = QueryHelper.fetch_all(sql, params)

            users = [
                (
                    row["user_id"],
                    row["username"],
                    row["full_name"],
                    row["user_role"],
                    row["is_active"],
                )
                for row in rows
            ]
            return users, None

        except DatabaseError as e:
            error_msg = ErrorMessages.log_and_mask_error(
                error=e,
                context="retrieving all users",
                user_message=ErrorMessages.DATABASE_ERROR
            )
            return [], error_msg
        except Exception as e:
            error_msg = ErrorMessages.log_and_mask_error(
                error=e,
                context="retrieving all users",
                user_message=ErrorMessages.GENERIC_ERROR
            )
            return [], error_msg

    @staticmethod
    def get_user_by_id(user_id: int) -> list[tuple]:
        """
        Retrieves a user's information by their ID.
        Args:
            user_id (int): The ID of the user to retrieve.
        Returns:
            list[tuple]: A list containing the user tuple if found, empty list otherwise.
        """

        try:
            users = QueryHelper.fetch_all(
                """
                SELECT user_id, username, full_name, user_role, is_active
                FROM users
                WHERE user_id = :user_id
                """,
                {"user_id": user_id},
            )

            if not users:
                return []
            
            return [
                (
                    user["user_id"],
                    user["username"],
                    user["full_name"],
                    user["user_role"],
                    user["is_active"],
                )
                for user in users
            ]
        except DatabaseError as e:
            ErrorMessages.log_and_mask_error(
                error=e,
                context=f"retrieving user by ID {user_id}",
                user_message=ErrorMessages.DATABASE_ERROR
            )
            return []
        except Exception as e:
            ErrorMessages.log_and_mask_error(
                error=e,
                context=f"retrieving user by ID {user_id}",
                user_message=ErrorMessages.GENERIC_ERROR
            )
            return []
        
    @staticmethod
    def get_user_by_name(username: str) -> list[tuple]:
        """
        Retrieves a user's information by their username.
        Args:
            username (str): The username of the user to retrieve.
        Returns:
            list[tuple]: A list containing the user tuple if found, empty list otherwise.
        """

        try:
            users = QueryHelper.fetch_all(
                """
                SELECT user_id, username, full_name, user_role, is_active
                FROM users
                WHERE username ILIKE :username
                """,
                {"username": f"%{username}%"},
            )

            if not users:
                return []
            
            return [
                (
                    user["user_id"],
                    user["username"],
                    user["full_name"],
                    user["user_role"],
                    user["is_active"]
                )
                for user in users
            ]
        
        except DatabaseError as e:
            ErrorMessages.log_and_mask_error(
                error=e,
                context=f"retrieving user by username '{username}'",
                user_message=ErrorMessages.DATABASE_ERROR
            )
            return []
        except Exception as e:
            ErrorMessages.log_and_mask_error(
                error=e,
                context=f"retrieving user by username '{username}'",
                user_message=ErrorMessages.GENERIC_ERROR
            )
            return []

    @staticmethod
    def change_user_password(user_id: int, new_password: str) -> tuple[bool, str | None]:
        """
        Changes the password for a given user.
        
        Returns:
            tuple[bool, str | None]: (success, error_message)
                - success: True if password was changed successfully
                - error_message: None if successful, generic error message if failed
        """
        if not isinstance(new_password, str) or not new_password.strip():
            return False, ErrorMessages.VALIDATION_ERROR

        try:
            password_hash = bcrypt.hashpw(
                new_password.encode("utf-8"),
                bcrypt.gensalt(),
            ).decode("utf-8")

            result = QueryHelper.execute(
                """
                UPDATE users
                SET password_hash = :password_hash
                WHERE user_id = :user_id
                """,
                {
                    "user_id": user_id,
                    "password_hash": password_hash,
                },
            )

            if result.get("rows_affected", 0) != 1:
                logger.warning(f"User not found for password change: ID {user_id}")
                return False, ErrorMessages.NOT_FOUND

            return True, None

        except DatabaseError as e:
            return False, ErrorMessages.log_and_mask_error(
                error=e,
                context=f"changing password for user ID {user_id}",
                user_message=ErrorMessages.DATABASE_ERROR
            )
        except Exception as e:
            return False, ErrorMessages.log_and_mask_error(
                error=e,
                context=f"changing password for user ID {user_id}",
                user_message=ErrorMessages.GENERIC_ERROR
            )
