import bcrypt
import logging
from dataclasses import dataclass
from database.query_helper import QueryHelper, DatabaseError

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
    """

    @staticmethod
    def authenticate_user(username: str, password: str):
        """Authenticates a user with the given username and password."""
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
            return None, str(e)

        if not row:
            return None, "User not found or inactive."

        stored_hash = row["password_hash"]
        stored_hash_bytes = stored_hash.encode("utf-8") if isinstance(stored_hash, str) else bytes(stored_hash)

        if not bcrypt.checkpw(password.encode("utf-8"), stored_hash_bytes):
            return None, "Invalid password."

        return AuthenticatedUser(
            user_id=row["user_id"],
            username=row["username"],
            user_role=row["user_role"],
        ), None

    @staticmethod
    def create_user(username: str, password: str, full_name: str, user_role: str, is_active: bool = True):
        """Creates a new user in the database."""

        if not username or not password or not full_name or not user_role:
            return False, "All fields are required."
        
        try:
            existing = QueryHelper.fetch_one(
                "SELECT 1 FROM users WHERE username = :username",
                {"username": username},
            )
            if existing:
                return False, "Username already exists."
            
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
        
        except Exception as e:
            QueryHelper.rollback()
            return False, str(e)

    @staticmethod
    def update_user_info(user_id: int, username: str, full_name: str, user_role: str, is_active: bool):
        """
        Updates an existing user's information in the database.
        args:
            user_id (int): The ID of the user to update.
            username (str): The new username.
            full_name (str): The new full name.
            user_role (str): The new user role.
            is_active (bool): The new active status.
        Returns:
            bool: True if the user was updated successfully, False otherwise.
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
                return False, "User not found."
            return True
        
        except DatabaseError as e:
            logger.error(f"Error updating user {user_id}: {e}")
            return False, str(e)

    @staticmethod
    def get_all_users(include_inactive: bool = True):
        """
        Retrieves all users from the database.
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

        except Exception as e:
            return [], str(e)

    @staticmethod
    def change_user_password(user_id: int, new_password: str):
        """
        Changes the password for a given user.
        """
        if not isinstance(new_password, str) or not new_password.strip():
            return False, "New password is required."

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
                return False, "User not found."

            return True, None

        except DatabaseError as e:
            logger.exception("Error changing password for user %s: %s", user_id, e)
            return False, str(e)
        except Exception as e:
            logger.exception("Unexpected error changing password for user %s: %s", user_id, e)
            return False, str(e)
