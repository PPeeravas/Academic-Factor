import re
from django.db import models
from django.contrib.auth.models import AbstractUser
from django.core.exceptions import ValidationError
from django.core.validators import RegexValidator

# --- 1. VALIDATION FUNCTIONS ---

def validate_thai_id(value):
    """
    Validates the Thai National ID using the Modulus 11 checksum algorithm.
    """
    if not re.match(r"^\d{13}$", value):
        raise ValidationError("Thai ID must be exactly 13 digits.")

    # Calculate checksum
    sum_val = 0
    for i in range(12):
        sum_val += int(value[i]) * (13 - i)
    
    check_digit = (11 - (sum_val % 11)) % 10
    
    if check_digit != int(value[12]):
        raise ValidationError("Invalid Thai National ID checksum.")

# Regex for Thai Mobile: Starts with 0 and then 6, 8, or 9, followed by 8 digits
thai_phone_regex = RegexValidator(
    regex=r'^0[689]\d{8}$',
    message="Phone number must be 10 digits starting with 06, 08, or 09."
)


# --- 2. THE USER MODEL ---

class User(AbstractUser):
    """
    Custom User Model for the Study Website.
    Includes roles, Thai ID, and Mobile Phone.
    """
    otp = models.CharField(max_length=6, null=True, blank=True)
    # User Roles
    is_teacher = models.BooleanField(
        default=False, 
        help_text="Designates whether this user can upload course content."
    )
    is_student = models.BooleanField(
        default=True, 
        help_text="Designates whether this user can enroll in courses."
    )

    # Identification
    id_number = models.CharField(
        max_length=13,
        unique=True,
        validators=[validate_thai_id],
        help_text="Thai National ID (13 digits)"
    )

    # Contact
    phone_number = models.CharField(
        max_length=10,
        unique=True,
        validators=[thai_phone_regex],
        help_text="Mobile phone number (e.g., 0812345678)"
    )

    # Standard fields like first_name, last_name, email are already included in AbstractUser

    def __str__(self):
        return f"{self.username} ({self.get_full_name()})"