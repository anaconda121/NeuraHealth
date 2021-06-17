from django.contrib import admin
from django.contrib.auth import get_user_model
from django.contrib.auth.admin import UserAdmin

from .forms import SignUpForm
from .models import CustomUser

class CustomUserAdmin(UserAdmin):
    add_form = SignUpForm
    model = CustomUser
    list_display = ['first_name', 'last_name', 'username', 'email', 'Phone', 'AssignedPatients', 'date_joined', 'last_login', 'is_staff', 'is_active']

admin.site.register(CustomUser, CustomUserAdmin)