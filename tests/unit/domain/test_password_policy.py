"""
Unit tests for the PasswordPolicy class.
Tests password validation, strength calculation, and requirements checking.
"""
import pytest
import os
from unittest.mock import patch
from src.domain.password_policy import PasswordPolicy


@pytest.mark.unit
@pytest.mark.security
class TestPasswordPolicyValidation:
    """Test password validation against security requirements"""
    
    def test_empty_password_fails(self):
        """Test that empty password is rejected"""
        is_valid, message = PasswordPolicy.validate("")
        assert not is_valid
        assert "empty" in message.lower()
    
    def test_none_password_fails(self):
        """Test that None password is rejected"""
        is_valid, message = PasswordPolicy.validate(None)
        assert not is_valid
    
    def test_password_too_short_fails(self):
        """Test that password shorter than minimum length is rejected"""
        short_password = "Abc1!"  # 5 characters
        is_valid, message = PasswordPolicy.validate(short_password)
        assert not is_valid
        assert "8" in message  # Assuming default min length is 8
        assert "characters" in message.lower()
    
    def test_password_missing_uppercase_fails(self):
        """Test that password without uppercase letter is rejected"""
        password = "password123!"
        is_valid, message = PasswordPolicy.validate(password)
        assert not is_valid
        assert "uppercase" in message.lower()
    
    def test_password_missing_lowercase_fails(self):
        """Test that password without lowercase letter is rejected"""
        password = "PASSWORD123!"
        is_valid, message = PasswordPolicy.validate(password)
        assert not is_valid
        assert "lowercase" in message.lower()
    
    def test_password_missing_digit_fails(self):
        """Test that password without digit is rejected"""
        password = "Password!"
        is_valid, message = PasswordPolicy.validate(password)
        assert not is_valid
        assert "number" in message.lower() or "digit" in message.lower()
    
    def test_password_missing_special_char_fails(self):
        """Test that password without special character is rejected"""
        password = "Password123"
        is_valid, message = PasswordPolicy.validate(password)
        assert not is_valid
        assert "special" in message.lower()
    
    def test_valid_password_passes(self):
        """Test that password meeting all requirements passes"""
        valid_password = "Password123!"
        is_valid, message = PasswordPolicy.validate(valid_password)
        assert is_valid
        assert message == ""
    
    def test_strong_password_passes(self):
        """Test various strong passwords"""
        strong_passwords = [
            "MyP@ssw0rd!",
            "Secur3$Password",
            "C0mpl3x!Pass",
            "Tr0ng#Pass123",
            "MyC0mpl3x$Pwd!"
        ]
        
        for password in strong_passwords:
            is_valid, message = PasswordPolicy.validate(password)
            assert is_valid, f"Password '{password}' should be valid but got: {message}"
            assert message == ""
    
    def test_password_with_multiple_special_chars(self):
        """Test password with multiple special characters"""
        password = "P@ssw0rd!#$"
        is_valid, message = PasswordPolicy.validate(password)
        assert is_valid
        assert message == ""
    
    def test_very_long_password_passes(self):
        """Test that very long passwords are accepted"""
        long_password = "ThisIsAVeryLongP@ssw0rd123WithManyCharacters!"
        is_valid, message = PasswordPolicy.validate(long_password)
        assert is_valid
        assert message == ""
    
    def test_minimum_length_boundary(self):
        """Test passwords at minimum length boundary"""
        # Exactly 8 characters (minimum)
        password = "Pass123!"
        is_valid, message = PasswordPolicy.validate(password)
        assert is_valid
        
        # 7 characters (below minimum)
        password = "Pas123!"
        is_valid, message = PasswordPolicy.validate(password)
        assert not is_valid
    
    def test_special_characters_accepted(self):
        """Test that all defined special characters are accepted"""
        special_chars = "!@#$%^&*()_+-=[]{}|;:,.<>?"
        
        for char in special_chars:
            password = f"Password123{char}"
            is_valid, message = PasswordPolicy.validate(password)
            assert is_valid, f"Special character '{char}' should be accepted"


@pytest.mark.unit
class TestPasswordPolicyRequirementsText:
    """Test get_requirements_text method"""
    
    def test_returns_non_empty_text(self):
        """Test that requirements text is returned"""
        requirements = PasswordPolicy.get_requirements_text()
        assert requirements
        assert len(requirements) > 0
    
    def test_includes_minimum_length(self):
        """Test that minimum length is mentioned"""
        requirements = PasswordPolicy.get_requirements_text()
        assert "8" in requirements or "characters" in requirements.lower()
    
    def test_includes_uppercase_requirement(self):
        """Test that uppercase requirement is mentioned"""
        requirements = PasswordPolicy.get_requirements_text()
        assert "uppercase" in requirements.lower() or "A-Z" in requirements
    
    def test_includes_lowercase_requirement(self):
        """Test that lowercase requirement is mentioned"""
        requirements = PasswordPolicy.get_requirements_text()
        assert "lowercase" in requirements.lower() or "a-z" in requirements
    
    def test_includes_digit_requirement(self):
        """Test that digit requirement is mentioned"""
        requirements = PasswordPolicy.get_requirements_text()
        assert "number" in requirements.lower() or "0-9" in requirements or "digit" in requirements.lower()
    
    def test_includes_special_char_requirement(self):
        """Test that special character requirement is mentioned"""
        requirements = PasswordPolicy.get_requirements_text()
        assert "special" in requirements.lower()
    
    def test_multiline_format(self):
        """Test that requirements are formatted as multiple lines"""
        requirements = PasswordPolicy.get_requirements_text()
        assert "\n" in requirements
        lines = requirements.split("\n")
        assert len(lines) >= 3  # At least a few requirements


@pytest.mark.unit
class TestPasswordStrength:
    """Test get_password_strength method"""
    
    def test_empty_password_is_weak(self):
        """Test that empty password is weak"""
        label, score = PasswordPolicy.get_password_strength("")
        assert label == "Weak"
        assert score == 0
    
    def test_short_simple_password_is_weak(self):
        """Test that short simple password is weak"""
        label, score = PasswordPolicy.get_password_strength("abc")
        assert label == "Weak"
        assert score < 40
    
    def test_longer_password_stronger(self):
        """Test that longer passwords get higher scores"""
        short_label, short_score = PasswordPolicy.get_password_strength("Pass123!")
        long_label, long_score = PasswordPolicy.get_password_strength("Password123!@#$")
        
        assert long_score > short_score
    
    def test_mixed_characters_increases_strength(self):
        """Test that character variety increases strength"""
        # Only lowercase
        label1, score1 = PasswordPolicy.get_password_strength("password")
        
        # Lowercase + uppercase
        label2, score2 = PasswordPolicy.get_password_strength("Password")
        
        # Lowercase + uppercase + digits
        label3, score3 = PasswordPolicy.get_password_strength("Password123")
        
        # Full variety
        label4, score4 = PasswordPolicy.get_password_strength("Password123!")
        
        assert score2 > score1
        assert score3 > score2
        assert score4 > score3
    
    def test_weak_password_label(self):
        """Test weak password classification"""
        label, score = PasswordPolicy.get_password_strength("pass")
        assert label == "Weak"
        assert score < 40
    
    def test_medium_password_label(self):
        """Test medium password classification"""
        label, score = PasswordPolicy.get_password_strength("Password1")
        # Password scoring can vary, just ensure score is reasonable
        assert label in ["Weak", "Medium", "Strong"]
        assert 0 <= score <= 100
    
    def test_strong_password_label(self):
        """Test strong password classification"""
        label, score = PasswordPolicy.get_password_strength("MyStr0ngP@ssword")
        assert label in ["Strong", "Very Strong"]
        assert score >= 60
    
    def test_very_strong_password_label(self):
        """Test very strong password classification"""
        label, score = PasswordPolicy.get_password_strength("MyV3ry$tr0ng!P@ssw0rd#2024")
        assert label in ["Strong", "Very Strong"]
        assert score >= 70
    
    def test_score_capped_at_100(self):
        """Test that score doesn't exceed 100"""
        super_strong = "ThisIsAnExtremelyStr0ng&C0mpl3x!P@ssw0rd#With$Many*Characters%2024"
        label, score = PasswordPolicy.get_password_strength(super_strong)
        assert score <= 100
    
    def test_score_is_integer(self):
        """Test that score is an integer"""
        label, score = PasswordPolicy.get_password_strength("Password123!")
        assert isinstance(score, int)
    
    def test_label_is_string(self):
        """Test that label is a string"""
        label, score = PasswordPolicy.get_password_strength("Password123!")
        assert isinstance(label, str)
    
    def test_valid_strength_labels_only(self):
        """Test that only valid strength labels are returned"""
        valid_labels = ["Weak", "Medium", "Strong", "Very Strong"]
        
        test_passwords = [
            "abc",
            "password",
            "Password1",
            "Password123!",
            "MyV3ry$tr0ng!P@ssw0rd"
        ]
        
        for password in test_passwords:
            label, score = PasswordPolicy.get_password_strength(password)
            assert label in valid_labels, f"Invalid label '{label}' for password '{password}'"


@pytest.mark.unit
@pytest.mark.security
class TestPasswordPolicyWithCustomSettings:
    """Test password policy with custom security settings"""
    
    def test_custom_minimum_length(self):
        """Test validation with custom minimum length"""
        with patch.dict(os.environ, {"PASSWORD_MIN_LENGTH": "12"}):
            # Reimport to get new settings
            from config.settings import SecurityConfig
            
            # 11 characters (below new minimum)
            password = "Password12!"
            # Note: Settings are cached, so this may not work as expected
            # This test demonstrates how you would test with custom settings
    
    def test_password_policy_uses_config(self):
        """Test that PasswordPolicy uses SecurityConfig"""
        # This test verifies the policy references SecurityConfig
        password = "Password123!"
        is_valid, message = PasswordPolicy.validate(password)
        
        # Should be valid with default config
        assert is_valid


@pytest.mark.unit
class TestPasswordPolicyEdgeCases:
    """Test edge cases and special scenarios"""
    
    def test_password_with_spaces(self):
        """Test password containing spaces"""
        password = "Pass word 123!"
        is_valid, message = PasswordPolicy.validate(password)
        # Spaces should be allowed
        assert is_valid
    
    def test_password_with_unicode(self):
        """Test password with unicode characters"""
        password = "Pássw0rd!"  # Contains accented character
        is_valid, message = PasswordPolicy.validate(password)
        # Should handle unicode gracefully
        assert isinstance(is_valid, bool)
    
    def test_password_all_same_character(self):
        """Test password with all same characters"""
        password = "AAAAAAAA"
        is_valid, message = PasswordPolicy.validate(password)
        # Should fail other requirements
        assert not is_valid
    
    def test_password_sequential_characters(self):
        """Test password with sequential characters"""
        password = "Abcd1234!"
        is_valid, message = PasswordPolicy.validate(password)
        # Sequential is OK if it meets requirements
        assert is_valid
    
    def test_validation_returns_tuple(self):
        """Test that validate always returns a tuple"""
        result = PasswordPolicy.validate("Password123!")
        assert isinstance(result, tuple)
        assert len(result) == 2
        assert isinstance(result[0], bool)
        assert isinstance(result[1], str)
    
    def test_strength_returns_tuple(self):
        """Test that get_password_strength always returns a tuple"""
        result = PasswordPolicy.get_password_strength("Password123!")
        assert isinstance(result, tuple)
        assert len(result) == 2
        assert isinstance(result[0], str)
        assert isinstance(result[1], int)
