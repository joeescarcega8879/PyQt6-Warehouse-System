"""
Unit tests for UserModel class.
Tests user authentication, CRUD operations, and error handling with mocked database.
"""

import pytest
import bcrypt
from unittest.mock import patch, MagicMock
from models.user_model import UserModel, AuthenticatedUser
from database.query_helper import DatabaseError
from common.error_messages import ErrorMessages


class TestAuthenticateUser:
    """Tests for authenticate_user method."""
    
    @pytest.mark.unit
    def test_successful_authentication(self):
        """Test successful user authentication with valid credentials."""
        # Arrange
        password = "SecurePassword123!"
        password_hash = bcrypt.hashpw(password.encode("utf-8"), bcrypt.gensalt()).decode("utf-8")
        
        mock_row = {
            "user_id": 1,
            "username": "john_doe",
            "password_hash": password_hash,
            "user_role": "admin"
        }
        
        with patch('models.user_model.QueryHelper.fetch_one', return_value=mock_row):
            # Act
            user, error = UserModel.authenticate_user("john_doe", password)
            
            # Assert
            assert user is not None
            assert error is None
            assert isinstance(user, AuthenticatedUser)
            assert user.user_id == 1
            assert user.username == "john_doe"
            assert user.user_role == "admin"
    
    @pytest.mark.unit
    def test_authentication_user_not_found(self):
        """Test authentication fails when user does not exist."""
        # Arrange
        with patch('models.user_model.QueryHelper.fetch_one', return_value=None):
            # Act
            user, error = UserModel.authenticate_user("nonexistent", "password")
            
            # Assert
            assert user is None
            assert error == ErrorMessages.LOGIN_FAILED
    
    @pytest.mark.unit
    def test_authentication_wrong_password(self):
        """Test authentication fails with incorrect password."""
        # Arrange
        correct_password = "CorrectPassword123!"
        password_hash = bcrypt.hashpw(correct_password.encode("utf-8"), bcrypt.gensalt()).decode("utf-8")
        
        mock_row = {
            "user_id": 1,
            "username": "john_doe",
            "password_hash": password_hash,
            "user_role": "admin"
        }
        
        with patch('models.user_model.QueryHelper.fetch_one', return_value=mock_row):
            # Act
            user, error = UserModel.authenticate_user("john_doe", "WrongPassword123!")
            
            # Assert
            assert user is None
            assert error == ErrorMessages.LOGIN_FAILED
    
    @pytest.mark.unit
    def test_authentication_password_hash_as_bytes(self):
        """Test authentication works when password_hash is returned as bytes."""
        # Arrange
        password = "SecurePassword123!"
        password_hash_bytes = bcrypt.hashpw(password.encode("utf-8"), bcrypt.gensalt())
        
        mock_row = {
            "user_id": 1,
            "username": "john_doe",
            "password_hash": password_hash_bytes,  # bytes instead of string
            "user_role": "admin"
        }
        
        with patch('models.user_model.QueryHelper.fetch_one', return_value=mock_row):
            # Act
            user, error = UserModel.authenticate_user("john_doe", password)
            
            # Assert
            assert user is not None
            assert error is None
    
    @pytest.mark.unit
    @pytest.mark.security
    def test_authentication_database_error(self):
        """Test authentication handles database errors gracefully."""
        # Arrange
        with patch('models.user_model.QueryHelper.fetch_one', side_effect=DatabaseError("Connection failed")):
            with patch('models.user_model.ErrorMessages.log_and_mask_error', 
                      return_value=ErrorMessages.AUTHENTICATION_ERROR):
                # Act
                user, error = UserModel.authenticate_user("john_doe", "password")
                
                # Assert
                assert user is None
                assert error == ErrorMessages.AUTHENTICATION_ERROR
    
    @pytest.mark.unit
    @pytest.mark.security
    def test_authentication_generic_exception(self):
        """Test authentication handles unexpected exceptions."""
        # Arrange
        with patch('models.user_model.QueryHelper.fetch_one', side_effect=Exception("Unexpected error")):
            with patch('models.user_model.ErrorMessages.log_and_mask_error', 
                      return_value=ErrorMessages.AUTHENTICATION_ERROR):
                # Act
                user, error = UserModel.authenticate_user("john_doe", "password")
                
                # Assert
                assert user is None
                assert error == ErrorMessages.AUTHENTICATION_ERROR
    
    @pytest.mark.unit
    @pytest.mark.security
    def test_authentication_inactive_user_not_returned(self):
        """Test that SQL query checks for is_active = TRUE."""
        # Arrange
        with patch('models.user_model.QueryHelper.fetch_one', return_value=None) as mock_fetch:
            # Act
            UserModel.authenticate_user("inactive_user", "password")
            
            # Assert - verify SQL query includes is_active check
            call_args = mock_fetch.call_args
            sql_query = call_args[0][0]
            assert "is_active = TRUE" in sql_query or "is_active=TRUE" in sql_query.replace(" ", "")


class TestCreateUser:
    """Tests for create_user method."""
    
    @pytest.mark.unit
    def test_successful_user_creation(self):
        """Test successful creation of a new user."""
        # Arrange
        with patch('models.user_model.QueryHelper.fetch_one', return_value=None):
            with patch('models.user_model.QueryHelper.execute', return_value={"success": True}):
                with patch('models.user_model.QueryHelper.begin_transaction'):
                    with patch('models.user_model.QueryHelper.commit'):
                        # Act
                        success, error = UserModel.create_user(
                            username="new_user",
                            password="Password123!",
                            full_name="New User",
                            user_role="employee"
                        )
                        
                        # Assert
                        assert success is True
                        assert error is None
    
    @pytest.mark.unit
    def test_create_user_with_custom_is_active(self):
        """Test creating user with custom is_active flag."""
        # Arrange
        with patch('models.user_model.QueryHelper.fetch_one', return_value=None):
            with patch('models.user_model.QueryHelper.execute', return_value={"success": True}) as mock_execute:
                with patch('models.user_model.QueryHelper.begin_transaction'):
                    with patch('models.user_model.QueryHelper.commit'):
                        # Act
                        success, error = UserModel.create_user(
                            username="new_user",
                            password="Password123!",
                            full_name="New User",
                            user_role="employee",
                            is_active=False
                        )
                        
                        # Assert
                        assert success is True
                        params = mock_execute.call_args[0][1]
                        assert params["is_active"] is False
    
    @pytest.mark.unit
    def test_create_user_duplicate_username(self):
        """Test creating user with duplicate username fails."""
        # Arrange - simulate existing user
        with patch('models.user_model.QueryHelper.fetch_one', return_value={"username": "existing_user"}):
            # Act
            success, error = UserModel.create_user(
                username="existing_user",
                password="Password123!",
                full_name="Duplicate User",
                user_role="employee"
            )
            
            # Assert
            assert success is False
            assert error == ErrorMessages.DUPLICATE_ERROR
    
    @pytest.mark.unit
    def test_create_user_empty_username(self):
        """Test creating user with empty username fails validation."""
        # Act
        success, error = UserModel.create_user(
            username="",
            password="Password123!",
            full_name="User",
            user_role="employee"
        )
        
        # Assert
        assert success is False
        assert error == ErrorMessages.VALIDATION_ERROR
    
    @pytest.mark.unit
    def test_create_user_empty_password(self):
        """Test creating user with empty password fails validation."""
        # Act
        success, error = UserModel.create_user(
            username="new_user",
            password="",
            full_name="User",
            user_role="employee"
        )
        
        # Assert
        assert success is False
        assert error == ErrorMessages.VALIDATION_ERROR
    
    @pytest.mark.unit
    def test_create_user_empty_full_name(self):
        """Test creating user with empty full name fails validation."""
        # Act
        success, error = UserModel.create_user(
            username="new_user",
            password="Password123!",
            full_name="",
            user_role="employee"
        )
        
        # Assert
        assert success is False
        assert error == ErrorMessages.VALIDATION_ERROR
    
    @pytest.mark.unit
    def test_create_user_empty_user_role(self):
        """Test creating user with empty user role fails validation."""
        # Act
        success, error = UserModel.create_user(
            username="new_user",
            password="Password123!",
            full_name="User",
            user_role=""
        )
        
        # Assert
        assert success is False
        assert error == ErrorMessages.VALIDATION_ERROR
    
    @pytest.mark.unit
    def test_create_user_none_values(self):
        """Test creating user with None values fails validation."""
        # Act
        success, error = UserModel.create_user(
            username=None,
            password="Password123!",
            full_name="User",
            user_role="employee"
        )
        
        # Assert
        assert success is False
        assert error == ErrorMessages.VALIDATION_ERROR
    
    @pytest.mark.unit
    def test_create_user_password_hashing(self):
        """Test that password is properly hashed before storage."""
        # Arrange
        plain_password = "Password123!"
        
        with patch('models.user_model.QueryHelper.fetch_one', return_value=None):
            with patch('models.user_model.QueryHelper.execute') as mock_execute:
                with patch('models.user_model.QueryHelper.begin_transaction'):
                    with patch('models.user_model.QueryHelper.commit'):
                        # Act
                        UserModel.create_user(
                            username="new_user",
                            password=plain_password,
                            full_name="User",
                            user_role="employee"
                        )
                        
                        # Assert
                        params = mock_execute.call_args[0][1]
                        stored_hash = params["password_hash"]
                        
                        # Verify it's a valid bcrypt hash
                        assert stored_hash != plain_password
                        assert stored_hash.startswith("$2b$")
                        
                        # Verify the hash can validate the original password
                        assert bcrypt.checkpw(plain_password.encode("utf-8"), stored_hash.encode("utf-8"))
    
    @pytest.mark.unit
    def test_create_user_database_error_with_rollback(self):
        """Test that database errors trigger rollback."""
        # Arrange
        with patch('models.user_model.QueryHelper.fetch_one', return_value=None):
            with patch('models.user_model.QueryHelper.execute', side_effect=DatabaseError("Insert failed")):
                with patch('models.user_model.QueryHelper.begin_transaction'):
                    with patch('models.user_model.QueryHelper.rollback') as mock_rollback:
                        with patch('models.user_model.ErrorMessages.log_and_mask_error', 
                                  return_value=ErrorMessages.DATABASE_ERROR):
                            # Act
                            success, error = UserModel.create_user(
                                username="new_user",
                                password="Password123!",
                                full_name="User",
                                user_role="employee"
                            )
                            
                            # Assert
                            assert success is False
                            assert error == ErrorMessages.DATABASE_ERROR
                            mock_rollback.assert_called_once()
    
    @pytest.mark.unit
    def test_create_user_generic_exception_with_rollback(self):
        """Test that generic exceptions trigger rollback."""
        # Arrange
        with patch('models.user_model.QueryHelper.fetch_one', return_value=None):
            with patch('models.user_model.QueryHelper.execute', side_effect=Exception("Unexpected error")):
                with patch('models.user_model.QueryHelper.begin_transaction'):
                    with patch('models.user_model.QueryHelper.rollback') as mock_rollback:
                        with patch('models.user_model.ErrorMessages.log_and_mask_error', 
                                  return_value=ErrorMessages.GENERIC_ERROR):
                            # Act
                            success, error = UserModel.create_user(
                                username="new_user",
                                password="Password123!",
                                full_name="User",
                                user_role="employee"
                            )
                            
                            # Assert
                            assert success is False
                            assert error == ErrorMessages.GENERIC_ERROR
                            mock_rollback.assert_called_once()


class TestUpdateUserInfo:
    """Tests for update_user_info method."""
    
    @pytest.mark.unit
    def test_successful_user_update(self):
        """Test successful update of user information."""
        # Arrange
        with patch('models.user_model.QueryHelper.execute', 
                  return_value={"rows_affected": 1}):
            # Act
            success, error = UserModel.update_user_info(
                user_id=1,
                username="updated_user",
                full_name="Updated Name",
                user_role="admin",
                is_active=True
            )
            
            # Assert
            assert success is True
            assert error is None
    
    @pytest.mark.unit
    def test_update_user_not_found(self):
        """Test updating non-existent user returns NOT_FOUND error."""
        # Arrange
        with patch('models.user_model.QueryHelper.execute', 
                  return_value={"rows_affected": 0}):
            # Act
            success, error = UserModel.update_user_info(
                user_id=999,
                username="user",
                full_name="Name",
                user_role="employee",
                is_active=True
            )
            
            # Assert
            assert success is False
            assert error == ErrorMessages.NOT_FOUND
    
    @pytest.mark.unit
    def test_update_user_database_error(self):
        """Test update handles database errors gracefully."""
        # Arrange
        with patch('models.user_model.QueryHelper.execute', 
                  side_effect=DatabaseError("Update failed")):
            with patch('models.user_model.ErrorMessages.log_and_mask_error', 
                      return_value=ErrorMessages.DATABASE_ERROR):
                # Act
                success, error = UserModel.update_user_info(
                    user_id=1,
                    username="user",
                    full_name="Name",
                    user_role="employee",
                    is_active=True
                )
                
                # Assert
                assert success is False
                assert error == ErrorMessages.DATABASE_ERROR
    
    @pytest.mark.unit
    def test_update_user_generic_exception(self):
        """Test update handles generic exceptions gracefully."""
        # Arrange
        with patch('models.user_model.QueryHelper.execute', 
                  side_effect=Exception("Unexpected error")):
            with patch('models.user_model.ErrorMessages.log_and_mask_error', 
                      return_value=ErrorMessages.GENERIC_ERROR):
                # Act
                success, error = UserModel.update_user_info(
                    user_id=1,
                    username="user",
                    full_name="Name",
                    user_role="employee",
                    is_active=True
                )
                
                # Assert
                assert success is False
                assert error == ErrorMessages.GENERIC_ERROR
    
    @pytest.mark.unit
    def test_update_user_deactivation(self):
        """Test updating user to deactivate them."""
        # Arrange
        with patch('models.user_model.QueryHelper.execute', 
                  return_value={"rows_affected": 1}) as mock_execute:
            # Act
            success, error = UserModel.update_user_info(
                user_id=1,
                username="user",
                full_name="Name",
                user_role="employee",
                is_active=False  # Deactivating user
            )
            
            # Assert
            assert success is True
            params = mock_execute.call_args[0][1]
            assert params["is_active"] is False


class TestGetAllUsers:
    """Tests for get_all_users method."""
    
    @pytest.mark.unit
    def test_get_all_users_success(self):
        """Test retrieving all users successfully."""
        # Arrange
        mock_rows = [
            {"user_id": 1, "username": "user1", "full_name": "User One", "user_role": "admin", "is_active": True},
            {"user_id": 2, "username": "user2", "full_name": "User Two", "user_role": "employee", "is_active": False}
        ]
        
        with patch('models.user_model.QueryHelper.fetch_all', return_value=mock_rows):
            # Act
            users, error = UserModel.get_all_users()
            
            # Assert
            assert error is None
            assert len(users) == 2
            assert users[0] == (1, "user1", "User One", "admin", True)
            assert users[1] == (2, "user2", "User Two", "employee", False)
    
    @pytest.mark.unit
    def test_get_all_users_empty_result(self):
        """Test get all users when no users exist."""
        # Arrange
        with patch('models.user_model.QueryHelper.fetch_all', return_value=[]):
            # Act
            users, error = UserModel.get_all_users()
            
            # Assert
            assert error is None
            assert users == []
    
    @pytest.mark.unit
    def test_get_all_users_include_inactive_true(self):
        """Test get all users with include_inactive=True."""
        # Arrange
        with patch('models.user_model.QueryHelper.fetch_all', return_value=[]) as mock_fetch:
            # Act
            UserModel.get_all_users(include_inactive=True)
            
            # Assert
            sql_query = mock_fetch.call_args[0][0]
            assert "WHERE is_active = TRUE" not in sql_query
    
    @pytest.mark.unit
    def test_get_all_users_include_inactive_false(self):
        """Test get all users with include_inactive=False filters inactive users."""
        # Arrange
        with patch('models.user_model.QueryHelper.fetch_all', return_value=[]) as mock_fetch:
            # Act
            UserModel.get_all_users(include_inactive=False)
            
            # Assert
            sql_query = mock_fetch.call_args[0][0]
            assert "WHERE is_active = TRUE" in sql_query or "WHERE is_active=TRUE" in sql_query.replace(" ", "")
    
    @pytest.mark.unit
    def test_get_all_users_ordered_by_id(self):
        """Test that results are ordered by user_id ASC."""
        # Arrange
        with patch('models.user_model.QueryHelper.fetch_all', return_value=[]) as mock_fetch:
            # Act
            UserModel.get_all_users()
            
            # Assert
            sql_query = mock_fetch.call_args[0][0]
            assert "ORDER BY user_id ASC" in sql_query
    
    @pytest.mark.unit
    def test_get_all_users_database_error(self):
        """Test get all users handles database errors gracefully."""
        # Arrange
        with patch('models.user_model.QueryHelper.fetch_all', 
                  side_effect=DatabaseError("Query failed")):
            with patch('models.user_model.ErrorMessages.log_and_mask_error', 
                      return_value=ErrorMessages.DATABASE_ERROR):
                # Act
                users, error = UserModel.get_all_users()
                
                # Assert
                assert users == []
                assert error == ErrorMessages.DATABASE_ERROR
    
    @pytest.mark.unit
    def test_get_all_users_generic_exception(self):
        """Test get all users handles generic exceptions gracefully."""
        # Arrange
        with patch('models.user_model.QueryHelper.fetch_all', 
                  side_effect=Exception("Unexpected error")):
            with patch('models.user_model.ErrorMessages.log_and_mask_error', 
                      return_value=ErrorMessages.GENERIC_ERROR):
                # Act
                users, error = UserModel.get_all_users()
                
                # Assert
                assert users == []
                assert error == ErrorMessages.GENERIC_ERROR


class TestGetUserById:
    """Tests for get_user_by_id method."""
    
    @pytest.mark.unit
    def test_get_user_by_id_success(self):
        """Test retrieving user by ID successfully."""
        # Arrange
        mock_rows = [
            {"user_id": 1, "username": "user1", "full_name": "User One", "user_role": "admin", "is_active": True}
        ]
        
        with patch('models.user_model.QueryHelper.fetch_all', return_value=mock_rows):
            # Act
            result = UserModel.get_user_by_id(1)
            
            # Assert
            assert len(result) == 1
            assert result[0] == (1, "user1", "User One", "admin", True)
    
    @pytest.mark.unit
    def test_get_user_by_id_not_found(self):
        """Test get user by ID when user does not exist."""
        # Arrange
        with patch('models.user_model.QueryHelper.fetch_all', return_value=[]):
            # Act
            result = UserModel.get_user_by_id(999)
            
            # Assert
            assert result == []
    
    @pytest.mark.unit
    def test_get_user_by_id_database_error(self):
        """Test get user by ID handles database errors gracefully."""
        # Arrange
        with patch('models.user_model.QueryHelper.fetch_all', 
                  side_effect=DatabaseError("Query failed")):
            with patch('models.user_model.ErrorMessages.log_and_mask_error', 
                      return_value=ErrorMessages.DATABASE_ERROR):
                # Act
                result = UserModel.get_user_by_id(1)
                
                # Assert
                assert result == []
    
    @pytest.mark.unit
    def test_get_user_by_id_generic_exception(self):
        """Test get user by ID handles generic exceptions gracefully."""
        # Arrange
        with patch('models.user_model.QueryHelper.fetch_all', 
                  side_effect=Exception("Unexpected error")):
            with patch('models.user_model.ErrorMessages.log_and_mask_error', 
                      return_value=ErrorMessages.GENERIC_ERROR):
                # Act
                result = UserModel.get_user_by_id(1)
                
                # Assert
                assert result == []


class TestGetUserByName:
    """Tests for get_user_by_name method."""
    
    @pytest.mark.unit
    def test_get_user_by_name_success(self):
        """Test retrieving user by username successfully."""
        # Arrange
        mock_rows = [
            {"user_id": 1, "username": "john_doe", "full_name": "John Doe", "user_role": "admin", "is_active": True}
        ]
        
        with patch('models.user_model.QueryHelper.fetch_all', return_value=mock_rows):
            # Act
            result = UserModel.get_user_by_name("john")
            
            # Assert
            assert len(result) == 1
            assert result[0] == (1, "john_doe", "John Doe", "admin", True)
    
    @pytest.mark.unit
    def test_get_user_by_name_partial_match(self):
        """Test that username search uses ILIKE with wildcards."""
        # Arrange
        with patch('models.user_model.QueryHelper.fetch_all', return_value=[]) as mock_fetch:
            # Act
            UserModel.get_user_by_name("john")
            
            # Assert
            params = mock_fetch.call_args[0][1]
            assert params["username"] == "%john%"
    
    @pytest.mark.unit
    def test_get_user_by_name_case_insensitive(self):
        """Test that username search is case-insensitive (ILIKE)."""
        # Arrange
        with patch('models.user_model.QueryHelper.fetch_all', return_value=[]) as mock_fetch:
            # Act
            UserModel.get_user_by_name("JOHN")
            
            # Assert
            sql_query = mock_fetch.call_args[0][0]
            assert "ILIKE" in sql_query
    
    @pytest.mark.unit
    def test_get_user_by_name_multiple_results(self):
        """Test retrieving multiple users with similar names."""
        # Arrange
        mock_rows = [
            {"user_id": 1, "username": "john_doe", "full_name": "John Doe", "user_role": "admin", "is_active": True},
            {"user_id": 2, "username": "john_smith", "full_name": "John Smith", "user_role": "employee", "is_active": True}
        ]
        
        with patch('models.user_model.QueryHelper.fetch_all', return_value=mock_rows):
            # Act
            result = UserModel.get_user_by_name("john")
            
            # Assert
            assert len(result) == 2
            assert result[0][1] == "john_doe"
            assert result[1][1] == "john_smith"
    
    @pytest.mark.unit
    def test_get_user_by_name_not_found(self):
        """Test get user by name when no matches exist."""
        # Arrange
        with patch('models.user_model.QueryHelper.fetch_all', return_value=[]):
            # Act
            result = UserModel.get_user_by_name("nonexistent")
            
            # Assert
            assert result == []
    
    @pytest.mark.unit
    def test_get_user_by_name_database_error(self):
        """Test get user by name handles database errors gracefully."""
        # Arrange
        with patch('models.user_model.QueryHelper.fetch_all', 
                  side_effect=DatabaseError("Query failed")):
            with patch('models.user_model.ErrorMessages.log_and_mask_error', 
                      return_value=ErrorMessages.DATABASE_ERROR):
                # Act
                result = UserModel.get_user_by_name("john")
                
                # Assert
                assert result == []
    
    @pytest.mark.unit
    def test_get_user_by_name_generic_exception(self):
        """Test get user by name handles generic exceptions gracefully."""
        # Arrange
        with patch('models.user_model.QueryHelper.fetch_all', 
                  side_effect=Exception("Unexpected error")):
            with patch('models.user_model.ErrorMessages.log_and_mask_error', 
                      return_value=ErrorMessages.GENERIC_ERROR):
                # Act
                result = UserModel.get_user_by_name("john")
                
                # Assert
                assert result == []


class TestChangeUserPassword:
    """Tests for change_user_password method."""
    
    @pytest.mark.unit
    def test_change_password_success(self):
        """Test successful password change."""
        # Arrange
        with patch('models.user_model.QueryHelper.execute', 
                  return_value={"rows_affected": 1}):
            # Act
            success, error = UserModel.change_user_password(1, "NewPassword123!")
            
            # Assert
            assert success is True
            assert error is None
    
    @pytest.mark.unit
    def test_change_password_hashing(self):
        """Test that new password is properly hashed."""
        # Arrange
        new_password = "NewPassword123!"
        
        with patch('models.user_model.QueryHelper.execute', 
                  return_value={"rows_affected": 1}) as mock_execute:
            # Act
            UserModel.change_user_password(1, new_password)
            
            # Assert
            params = mock_execute.call_args[0][1]
            stored_hash = params["password_hash"]
            
            # Verify it's a valid bcrypt hash
            assert stored_hash != new_password
            assert stored_hash.startswith("$2b$")
            
            # Verify the hash can validate the original password
            assert bcrypt.checkpw(new_password.encode("utf-8"), stored_hash.encode("utf-8"))
    
    @pytest.mark.unit
    def test_change_password_empty_string(self):
        """Test changing password to empty string fails validation."""
        # Act
        success, error = UserModel.change_user_password(1, "")
        
        # Assert
        assert success is False
        assert error == ErrorMessages.VALIDATION_ERROR
    
    @pytest.mark.unit
    def test_change_password_whitespace_only(self):
        """Test changing password to whitespace-only string fails validation."""
        # Act
        success, error = UserModel.change_user_password(1, "   ")
        
        # Assert
        assert success is False
        assert error == ErrorMessages.VALIDATION_ERROR
    
    @pytest.mark.unit
    def test_change_password_none_value(self):
        """Test changing password to None fails validation."""
        # Act
        success, error = UserModel.change_user_password(1, None)
        
        # Assert
        assert success is False
        assert error == ErrorMessages.VALIDATION_ERROR
    
    @pytest.mark.unit
    def test_change_password_user_not_found(self):
        """Test changing password for non-existent user."""
        # Arrange
        with patch('models.user_model.QueryHelper.execute', 
                  return_value={"rows_affected": 0}):
            # Act
            success, error = UserModel.change_user_password(999, "NewPassword123!")
            
            # Assert
            assert success is False
            assert error == ErrorMessages.NOT_FOUND
    
    @pytest.mark.unit
    def test_change_password_database_error(self):
        """Test change password handles database errors gracefully."""
        # Arrange
        with patch('models.user_model.QueryHelper.execute', 
                  side_effect=DatabaseError("Update failed")):
            with patch('models.user_model.ErrorMessages.log_and_mask_error', 
                      return_value=ErrorMessages.DATABASE_ERROR):
                # Act
                success, error = UserModel.change_user_password(1, "NewPassword123!")
                
                # Assert
                assert success is False
                assert error == ErrorMessages.DATABASE_ERROR
    
    @pytest.mark.unit
    def test_change_password_generic_exception(self):
        """Test change password handles generic exceptions gracefully."""
        # Arrange
        with patch('models.user_model.QueryHelper.execute', 
                  side_effect=Exception("Unexpected error")):
            with patch('models.user_model.ErrorMessages.log_and_mask_error', 
                      return_value=ErrorMessages.GENERIC_ERROR):
                # Act
                success, error = UserModel.change_user_password(1, "NewPassword123!")
                
                # Assert
                assert success is False
                assert error == ErrorMessages.GENERIC_ERROR


class TestAuthenticatedUserDataClass:
    """Tests for AuthenticatedUser dataclass."""
    
    @pytest.mark.unit
    def test_authenticated_user_creation(self):
        """Test creating an AuthenticatedUser instance."""
        # Act
        user = AuthenticatedUser(
            user_id=1,
            username="john_doe",
            user_role="admin"
        )
        
        # Assert
        assert user.user_id == 1
        assert user.username == "john_doe"
        assert user.user_role == "admin"
    
    @pytest.mark.unit
    def test_authenticated_user_equality(self):
        """Test AuthenticatedUser equality comparison."""
        # Arrange
        user1 = AuthenticatedUser(user_id=1, username="john", user_role="admin")
        user2 = AuthenticatedUser(user_id=1, username="john", user_role="admin")
        user3 = AuthenticatedUser(user_id=2, username="jane", user_role="employee")
        
        # Assert
        assert user1 == user2
        assert user1 != user3


class TestUserModelEdgeCases:
    """Tests for edge cases and special scenarios."""
    
    @pytest.mark.unit
    def test_authenticate_with_unicode_password(self):
        """Test authentication with unicode characters in password."""
        # Arrange
        password = "Contraseña123!José"
        password_hash = bcrypt.hashpw(password.encode("utf-8"), bcrypt.gensalt()).decode("utf-8")
        
        mock_row = {
            "user_id": 1,
            "username": "user",
            "password_hash": password_hash,
            "user_role": "admin"
        }
        
        with patch('models.user_model.QueryHelper.fetch_one', return_value=mock_row):
            # Act
            user, error = UserModel.authenticate_user("user", password)
            
            # Assert
            assert user is not None
            assert error is None
    
    @pytest.mark.unit
    def test_create_user_with_unicode_characters(self):
        """Test creating user with unicode characters in fields."""
        # Arrange
        with patch('models.user_model.QueryHelper.fetch_one', return_value=None):
            with patch('models.user_model.QueryHelper.execute', return_value={"success": True}):
                with patch('models.user_model.QueryHelper.begin_transaction'):
                    with patch('models.user_model.QueryHelper.commit'):
                        # Act
                        success, error = UserModel.create_user(
                            username="josé",
                            password="Contraseña123!",
                            full_name="José García",
                            user_role="employee"
                        )
                        
                        # Assert
                        assert success is True
                        assert error is None
    
    @pytest.mark.unit
    def test_get_user_by_name_with_sql_special_characters(self):
        """Test search handles SQL wildcards in username."""
        # Arrange
        with patch('models.user_model.QueryHelper.fetch_all', return_value=[]) as mock_fetch:
            # Act - search with % character
            UserModel.get_user_by_name("test%user")
            
            # Assert - verify % is wrapped in additional wildcards
            params = mock_fetch.call_args[0][1]
            assert params["username"] == "%test%user%"
