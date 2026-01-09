from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import User

# Register the User model with our Custom class
@admin.register(User)
class CustomUserAdmin(UserAdmin):
    # 1. Columns shown in the main list
    list_display = ('username', 'id_number', 'phone_number', 'is_teacher', 'is_student', 'is_staff')
    
    # 2. Layout when EDITING a user
    fieldsets = UserAdmin.fieldsets + (
        ('Study Site Roles & ID', {
            'fields': ('is_teacher', 'is_student', 'id_number', 'phone_number'),
        }),
    )

    # 3. Layout when initially ADDING a new user
    add_fieldsets = UserAdmin.add_fieldsets + (
        ('Initial Roles & ID', {
            'fields': ('is_teacher', 'is_student', 'id_number', 'phone_number'),
        }),
    )   