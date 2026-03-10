"""
Password policy validation module.
Enforces password complexity requirements based on security configuration.
"""
import re
from typing import Tuple
from config.settings import SecurityConfig


class PasswordPolicy:
    """
    Validates passwords against security policy requirements.
    Configuration loaded from SecurityConfig (environment variables).
    """
    
    @staticmethod
    def validate(password: str) -> Tuple[bool, str]:
        """
        Validate password against all configured policy requirements.
        
        Args:
            password: The password string to validate
            
        Returns:
            Tuple[bool, str]: (is_valid, error_message)
                - is_valid: True if password meets all requirements
                - error_message: Empty string if valid, otherwise describes the first requirement that failed
        """
        if not password:
            return False, "Password cannot be empty"
        
        # Check minimum length
        if len(password) < SecurityConfig.PASSWORD_MIN_LENGTH:
            return False, f"Password must be at least {SecurityConfig.PASSWORD_MIN_LENGTH} characters long"
        
        # Check for uppercase letter
        if SecurityConfig.PASSWORD_REQUIRE_UPPERCASE:
            if not re.search(r'[A-Z]', password):
                return False, "Password must contain at least one uppercase letter"
        
        # Check for lowercase letter
        if SecurityConfig.PASSWORD_REQUIRE_LOWERCASE:
            if not re.search(r'[a-z]', password):
                return False, "Password must contain at least one lowercase letter"
        
        # Check for digit
        if SecurityConfig.PASSWORD_REQUIRE_DIGIT:
            if not re.search(r'\d', password):
                return False, "Password must contain at least one number"
        
        # Check for special character
        if SecurityConfig.PASSWORD_REQUIRE_SPECIAL:
            special_char_pattern = f"[{re.escape(SecurityConfig.SPECIAL_CHARS)}]"
            if not re.search(special_char_pattern, password):
                return False, f"Password must contain at least one special character ({SecurityConfig.SPECIAL_CHARS})"
        
        return True, ""
    
    @staticmethod
    def get_requirements_text() -> str:
        """
        Generate a human-readable description of password requirements.
        
        Returns:
            str: Multi-line string describing all password requirements
        """
        requirements = [f"- At least {SecurityConfig.PASSWORD_MIN_LENGTH} characters long"]
        
        if SecurityConfig.PASSWORD_REQUIRE_UPPERCASE:
            requirements.append("- At least one uppercase letter (A-Z)")
        
        if SecurityConfig.PASSWORD_REQUIRE_LOWERCASE:
            requirements.append("- At least one lowercase letter (a-z)")
        
        if SecurityConfig.PASSWORD_REQUIRE_DIGIT:
            requirements.append("- At least one number (0-9)")
        
        if SecurityConfig.PASSWORD_REQUIRE_SPECIAL:
            requirements.append(f"- At least one special character ({SecurityConfig.SPECIAL_CHARS})")
        
        return "\n".join(requirements)
    
    @staticmethod
    def get_password_strength(password: str) -> Tuple[str, int]:
        """
        Calculate password strength score and category.
        
        Args:
            password: The password to evaluate
            
        Returns:
            Tuple[str, int]: (strength_label, score)
                - strength_label: "Weak", "Medium", "Strong", or "Very Strong"
                - score: Integer from 0-100 representing password strength
        """
        if not password:
            return "Weak", 0
        
        score = 0
        
        # Length scoring
        length = len(password)
        if length >= 8:
            score += 20
        if length >= 12:
            score += 10
        if length >= 16:
            score += 10
        
        # Character variety scoring
        if re.search(r'[a-z]', password):
            score += 10
        if re.search(r'[A-Z]', password):
            score += 15
        if re.search(r'\d', password):
            score += 15
        if re.search(f"[{re.escape(SecurityConfig.SPECIAL_CHARS)}]", password):
            score += 20
        
        # Bonus for high variety
        unique_chars = len(set(password))
        if unique_chars > length * 0.7:
            score += 10
        
        # Determine strength label
        if score < 40:
            label = "Weak"
        elif score < 60:
            label = "Medium"
        elif score < 80:
            label = "Strong"
        else:
            label = "Very Strong"
        
        return label, min(score, 100)
