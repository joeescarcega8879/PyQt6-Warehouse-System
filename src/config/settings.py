"""
Configuration management using environment variables.
Loads settings from .env file for secure credential management.
"""
import os
import sys
from pathlib import Path
from typing import Optional

try:
    from dotenv import load_dotenv
except ImportError:
    print("ERROR: python-dotenv not installed. Run: pip install python-dotenv")
    sys.exit(1)

# Load .env file from project root (src/config/ -> src/ -> project root)
BASE_DIR = Path(__file__).resolve().parent.parent.parent
ENV_FILE = BASE_DIR / ".env"

if not ENV_FILE.exists():
    print("WARNING: .env file not found")
    print(f"Expected location: {ENV_FILE}")
    print("Copy .env.example to .env and configure your credentials")
    print("The application will try to use default values where possible")


load_dotenv(ENV_FILE)


class DatabaseConfig:
    """Database connection settings loaded from environment variables"""
    
    HOST: str = os.getenv("DB_HOST", "localhost")
    PORT: int = int(os.getenv("DB_PORT", "5432"))
    NAME: Optional[str] = os.getenv("DB_NAME")
    USER: Optional[str] = os.getenv("DB_USER")
    PASSWORD: Optional[str] = os.getenv("DB_PASSWORD")
    SSL_MODE: str = os.getenv("DB_SSL_MODE", "prefer")
    
    @classmethod
    def validate(cls) -> tuple[bool, str]:
        """
        Validate that all required database settings are present.
        
        Returns:
            tuple[bool, str]: (is_valid, message)
        """
        required_fields = {
            "DB_NAME": cls.NAME,
            "DB_USER": cls.USER,
            "DB_PASSWORD": cls.PASSWORD
        }
        
        missing = [key for key, value in required_fields.items() if not value]
        
        if missing:
            return False, f"Missing required configuration: {', '.join(missing)}"
        
        return True, "Database configuration valid"
    
    @classmethod
    def get_connection_string(cls) -> str:
        """
        Get connection options string for QSqlDatabase.
        
        Returns:
            str: Connection options string
        """
        return f"sslmode={cls.SSL_MODE}"


class AppConfig:
    """Application settings"""
    
    ENV: str = os.getenv("APP_ENV", "production")
    DEBUG: bool = os.getenv("APP_DEBUG", "false").lower() == "true"
    LOG_LEVEL: str = os.getenv("LOG_LEVEL", "INFO")
    SECRET_KEY: Optional[str] = os.getenv("SECRET_KEY")
    
    @classmethod
    def is_development(cls) -> bool:
        """Check if running in development environment"""
        return cls.ENV == "development"
    
    @classmethod
    def is_production(cls) -> bool:
        """Check if running in production environment"""
        return cls.ENV == "production"


class SecurityConfig:
    """Security settings for authentication and session management"""
    
    # Session timeout in minutes
    SESSION_TIMEOUT_MINUTES: int = int(os.getenv("SESSION_TIMEOUT_MINUTES", "30"))
    
    # Login rate limiting
    MAX_LOGIN_ATTEMPTS: int = int(os.getenv("MAX_LOGIN_ATTEMPTS", "5"))
    LOGIN_LOCKOUT_MINUTES: int = int(os.getenv("LOGIN_LOCKOUT_MINUTES", "30"))
    
    # Password policy
    PASSWORD_MIN_LENGTH: int = int(os.getenv("PASSWORD_MIN_LENGTH", "8"))
    PASSWORD_REQUIRE_UPPERCASE: bool = os.getenv("PASSWORD_REQUIRE_UPPERCASE", "true").lower() == "true"
    PASSWORD_REQUIRE_LOWERCASE: bool = os.getenv("PASSWORD_REQUIRE_LOWERCASE", "true").lower() == "true"
    PASSWORD_REQUIRE_DIGIT: bool = os.getenv("PASSWORD_REQUIRE_DIGIT", "true").lower() == "true"
    PASSWORD_REQUIRE_SPECIAL: bool = os.getenv("PASSWORD_REQUIRE_SPECIAL", "true").lower() == "true"
    
    # Special characters allowed in passwords
    SPECIAL_CHARS: str = "!@#$%^&*()_+-=[]{}|;:,.<>?"


# Validate configuration on import if not in test mode
if not os.getenv("TESTING"):
    is_valid, message = DatabaseConfig.validate()
    if not is_valid and not ENV_FILE.exists():
        print(f"Configuration error: {message}")
        print("Please create a .env file with required database credentials")

    # Display configuration info in development mode
    if AppConfig.is_development() and is_valid:
        print("Configuration loaded successfully:")
        print(f"  - Environment: {AppConfig.ENV}")
        print(f"  - DB Host: {DatabaseConfig.HOST}:{DatabaseConfig.PORT}")
        print(f"  - DB Name: {DatabaseConfig.NAME}")
        print(f"  - SSL Mode: {DatabaseConfig.SSL_MODE}")
