from django import forms
from django.contrib.auth.forms import UserCreationForm, UserChangeForm
from .models import User

class StudentRegistrationForm(UserCreationForm):
    """
    Form for students to sign up. 
    It includes the custom Thai ID and Phone Number fields.
    """
    class Meta(UserCreationForm.Meta):
        model = User
        # These are the fields that will appear on your registration page
        fields = (
            "username", 
            "first_name", 
            "last_name", 
            "email", 
            "id_number", 
            "phone_number"
        )

    def clean_id_number(self):
        """
        Ensures the ID number is stored as a clean string of digits.
        """
        id_num = self.cleaned_data.get('id_number')
        return id_num.strip()

    def clean_phone_number(self):
        """
        Removes any accidental dashes or spaces from the phone number.
        """
        phone = self.cleaned_data.get('phone_number')
        # Remove dashes or spaces if the user typed '081-234-5678'
        clean_phone = phone.replace("-", "").replace(" ", "")
        return clean_phone

class CustomUserChangeForm(UserChangeForm):
    """
    Used for the Django Admin panel to edit users.
    """
    class Meta:
        model = User
        fields = ("username", "email", "id_number", "phone_number", "is_teacher", "is_student")

RegisterForm = StudentRegistrationForm