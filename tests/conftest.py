"""
Pytest configuration and shared fixtures for all tests.
This file is automatically loaded by pytest before running tests.
"""
import os
import sys
from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest
from PyQt6.QtWidgets import QApplication
from PyQt6.QtSql import QSqlDatabase

# Add project root to Python path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

# Set testing mode before importing config
os.environ["TESTING"] = "1"
os.environ["APP_ENV"] = "testing"


@pytest.fixture(scope="session")
def qapp():
    """
    Create QApplication instance for the entire test session.
    Required for any tests that use Qt widgets or UI components.
    
    Yields:
        QApplication: The Qt application instance
    """
    app = QApplication.instance()
    if app is None:
        app = QApplication([])
    yield app
    # Cleanup happens automatically when session ends


@pytest.fixture
def mock_database():
    """
    Mock database connection for testing without real database.
    Useful for unit tests that should be isolated from database.
    
    Returns:
        MagicMock: Mocked QSqlDatabase instance
    """
    mock_db = MagicMock(spec=QSqlDatabase)
    mock_db.isOpen.return_value = True
    mock_db.transaction.return_value = True
    mock_db.commit.return_value = True
    mock_db.rollback.return_value = True
    return mock_db


@pytest.fixture
def mock_query_helper(mock_database):
    """
    Mock QueryHelper class methods for testing without database.
    This patches the QueryHelper class to return mock results.
    
    Usage in tests:
        def test_something(mock_query_helper):
            mock_query_helper.fetch_one.return_value = {"id": 1, "name": "test"}
            # Your test code here
    
    Returns:
        MagicMock: Mocked QueryHelper with common methods
    """
    with patch("database.query_helper.QueryHelper") as mock_helper:
        # Setup default return values
        mock_helper.fetch_one.return_value = None
        mock_helper.fetch_all.return_value = []
        mock_helper.execute.return_value = {"last_insert_id": 1, "rows_affected": 1}
        mock_helper.begin_transaction.return_value = None
        mock_helper.commit.return_value = None
        mock_helper.rollback.return_value = None
        
        yield mock_helper


@pytest.fixture
def sample_user_data():
    """
    Provide sample user data for testing.
    
    Returns:
        dict: User data with typical fields
    """
    return {
        "user_id": 1,
        "username": "testuser",
        "password": "Test123!@#",
        "password_hash": "$2b$12$abcdefghijklmnopqrstuvwxyz123456",
        "role": "admin",
        "is_active": True
    }


@pytest.fixture
def sample_material_data():
    """
    Provide sample material data for testing.
    
    Returns:
        dict: Material data with typical fields
    """
    return {
        "material_id": 1,
        "material_name": "Test Material",
        "description": "Test description",
        "unit": "kg",
        "stock_quantity": 100.0,
        "min_stock": 10.0,
        "is_active": True
    }


@pytest.fixture
def sample_production_line_data():
    """
    Provide sample production line data for testing.
    
    Returns:
        dict: Production line data with typical fields
    """
    return {
        "line_id": 1,
        "line_name": "Test Line",
        "description": "Test production line",
        "is_active": True
    }


@pytest.fixture
def sample_supplier_data():
    """
    Provide sample supplier data for testing.
    
    Returns:
        dict: Supplier data with typical fields
    """
    return {
        "supplier_id": 1,
        "supplier_name": "Test Supplier",
        "contact_person": "John Doe",
        "phone": "1234567890",
        "email": "test@supplier.com",
        "address": "123 Test St",
        "is_active": True
    }


@pytest.fixture(autouse=True)
def reset_environment():
    """
    Reset environment variables before each test.
    This ensures tests don't interfere with each other.
    """
    # Save original environment
    original_env = os.environ.copy()
    
    # Set test defaults
    os.environ["TESTING"] = "1"
    os.environ["APP_ENV"] = "testing"
    os.environ["SESSION_TIMEOUT_MINUTES"] = "30"
    os.environ["MAX_LOGIN_ATTEMPTS"] = "5"
    os.environ["LOGIN_LOCKOUT_MINUTES"] = "30"
    
    yield
    
    # Restore original environment
    os.environ.clear()
    os.environ.update(original_env)


@pytest.fixture
def temp_test_env_file(tmp_path):
    """
    Create a temporary .env file for testing configuration loading.
    
    Args:
        tmp_path: pytest fixture providing temporary directory
    
    Returns:
        Path: Path to temporary .env file
    """
    env_file = tmp_path / ".env"
    env_content = """
DB_HOST=localhost
DB_PORT=5432
DB_NAME=test_warehouse
DB_USER=test_user
DB_PASSWORD=test_password
DB_SSL_MODE=disable

APP_ENV=testing
APP_DEBUG=true
LOG_LEVEL=DEBUG

SESSION_TIMEOUT_MINUTES=30
MAX_LOGIN_ATTEMPTS=5
LOGIN_LOCKOUT_MINUTES=30
"""
    env_file.write_text(env_content)
    return env_file


@pytest.fixture
def mock_logger():
    """
    Mock logger to capture log messages in tests.
    
    Returns:
        MagicMock: Mocked logger instance
    """
    with patch("config.logger_config.logger") as mock_log:
        yield mock_log


# Custom markers for test organization
def pytest_configure(config):
    """Register custom markers"""
    config.addinivalue_line(
        "markers", "unit: Unit tests (fast, isolated)"
    )
    config.addinivalue_line(
        "markers", "integration: Integration tests (slower, require database)"
    )
    config.addinivalue_line(
        "markers", "ui: UI tests (require Qt environment)"
    )
    config.addinivalue_line(
        "markers", "slow: Slow tests that take significant time"
    )
    config.addinivalue_line(
        "markers", "security: Security-related tests"
    )
