"""
Database connection management using Qt's SQL driver.
Credentials loaded from environment variables via config.settings for security.
"""
from PyQt6.QtSql import QSqlDatabase
from config.settings import DatabaseConfig, AppConfig
import logging

logger = logging.getLogger(__name__)

CONNECTION_NAME = "inventory_connection"


def connect_db() -> bool:
    """
    Establish connection to PostgreSQL database using credentials from environment.
    
    Returns:
        bool: True if connection successful, False otherwise
    """
    # Check if connection already exists
    if QSqlDatabase.contains(CONNECTION_NAME):
        logger.info("Using existing database connection")
        return True
    
    # Validate configuration before attempting connection
    is_valid, validation_message = DatabaseConfig.validate()
    if not is_valid:
        logger.error(f"Invalid database configuration: {validation_message}")
        return False
    
    # Create database connection
    db = QSqlDatabase.addDatabase("QPSQL", CONNECTION_NAME)
    db.setHostName(DatabaseConfig.HOST)
    db.setPort(DatabaseConfig.PORT)
    db.setDatabaseName(DatabaseConfig.NAME)
    db.setUserName(DatabaseConfig.USER)
    db.setPassword(DatabaseConfig.PASSWORD)
    
    # Set connection options (SSL configuration)
    connection_options = DatabaseConfig.get_connection_string()
    db.setConnectOptions(connection_options)
    
    # Attempt connection
    if not db.open():
        error = db.lastError().text()
        logger.error(f"Database connection error: {error}")
        
        # In development, show more details
        if AppConfig.is_development():
            print(f"Database connection failed:")
            print(f"  Host: {DatabaseConfig.HOST}:{DatabaseConfig.PORT}")
            print(f"  Database: {DatabaseConfig.NAME}")
            print(f"  Error: {error}")
        
        return False
    
    logger.info(f"Database connection successful: {DatabaseConfig.NAME}@{DatabaseConfig.HOST}")
    
    if AppConfig.is_development():
        print(f"Connected to database: {DatabaseConfig.NAME}")
    
    return True


def close_db() -> None:
    """Close database connection if it exists"""
    if QSqlDatabase.contains(CONNECTION_NAME):
        db = QSqlDatabase.database(CONNECTION_NAME)
        if db.isOpen():
            db.close()
            logger.info("Database connection closed")
        QSqlDatabase.removeDatabase(CONNECTION_NAME)


def get_db() -> QSqlDatabase:
    """
    Get the current database connection.
    
    Returns:
        QSqlDatabase: The active database connection
        
    Raises:
        RuntimeError: If no connection exists
    """
    if not QSqlDatabase.contains(CONNECTION_NAME):
        raise RuntimeError("No database connection exists. Call connect_db() first.")
    
    return QSqlDatabase.database(CONNECTION_NAME)
