# from django import forms
# from django.contrib import admin
# from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
# from django.contrib.auth.forms import UserChangeForm, UserCreationForm

# from accounts.models import User


# class CustomUserCreationForm(UserCreationForm):
#     class Meta(UserCreationForm.Meta):
#         model = User
#         fields = ('username', 'email', 'role')


# class CustomUserChangeForm(UserChangeForm):
#     class Meta(UserChangeForm.Meta):
#         model = User


# @admin.register(User)
# class UserAdmin(BaseUserAdmin):
#     add_form = CustomUserCreationForm
#     form = CustomUserChangeForm
#     list_display = ['username', 'email', 'full_name', 'role', 'department', 'is_active', 'date_joined']
#     list_filter = ['role', 'is_active', 'department']
#     search_fields = ['username', 'email', 'first_name', 'last_name']
#     fieldsets = BaseUserAdmin.fieldsets + (
#         ('Profile', {'fields': ('role', 'department', 'manager', 'phone_number', 'avatar', 'date_joined_company')}),
#     )
#     add_fieldsets = BaseUserAdmin.add_fieldsets + (
#         ('Profile', {'fields': ('role', 'department', 'manager', 'email')}),
#     )

#     def full_name(self, obj):
#         return obj.full_name
#     full_name.short_description = 'Name'
from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.contrib.auth.forms import UserCreationForm, UserChangeForm

from .models import User


class CustomUserCreationForm(UserCreationForm):
    class Meta:
        model = User
        fields = (
            "username",
            "email",
            "role",
            "department",
            "manager",
        )


class CustomUserChangeForm(UserChangeForm):
    class Meta:
        model = User
        fields = (
            "username",
            "email",
            "role",
            "department",
            "manager",
            "is_active",
            "is_staff",
        )


@admin.register(User)
class UserAdmin(BaseUserAdmin):
    add_form = CustomUserCreationForm
    form = CustomUserChangeForm

    list_display = (
        "username",
        "email",
        "role",
        "department",
        "manager",
        "is_active",
        "is_staff",
    )

    list_filter = (
        "role",
        "department",
        "is_active",
        "is_staff",
    )

    search_fields = (
        "username",
        "email",
    )

    ordering = ("username",)

    fieldsets = (
        (
            None,
            {
                "fields": (
                    "username",
                    "password",
                )
            },
        ),
        (
            "Profile",
            {
                "fields": (
                    "role",
                    "department",
                    "manager",
                    "email",
                )
            },
        ),
        (
            "Permissions",
            {
                "fields": (
                    "is_active",
                    "is_staff",
                    "is_superuser",
                    "groups",
                    "user_permissions",
                )
            },
        ),
    )

    add_fieldsets = (
        (
            None,
            {
                "classes": ("wide",),
                "fields": (
                    "username",
                    "password1",
                    "password2",
                    "email",
                    "role",
                    "department",
                    "manager",
                ),
            },
        ),
    )