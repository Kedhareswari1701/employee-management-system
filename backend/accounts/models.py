from django.contrib.auth.models import AbstractUser
from django.db import models

from departments.models import Department


class User(AbstractUser):
    """Custom user model with role-based access control.

    Roles:
        - admin:   full system control, manages everything
        - manager: manages their department's employees, attendance and leave
        - employee: regular staff (reports to a manager)
    """

    class Role(models.TextChoices):
        ADMIN = 'admin', 'Administrator'
        MANAGER = 'manager', 'Manager'
        EMPLOYEE = 'employee', 'Employee'

    role = models.CharField(
        max_length=20,
        choices=Role.choices,
        default=Role.EMPLOYEE,
    )
    department = models.ForeignKey(
        Department,
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name='employees',
        help_text='Department the user belongs to.',
    )
    manager = models.ForeignKey(
        'self',
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name='team_members',
        help_text='Direct reporting manager (for employees).',
    )
    phone_number = models.CharField(max_length=20, blank=True)
    avatar = models.ImageField(upload_to='avatars/', blank=True, null=True)
    date_joined_company = models.DateField(null=True, blank=True)

    @property
    def is_admin(self):
        return self.role == self.Role.ADMIN

    @property
    def is_manager(self):
        return self.role == self.Role.MANAGER

    @property
    def is_employee(self):
        return self.role == self.Role.EMPLOYEE

    @property
    def full_name(self):
        return self.get_full_name() or self.username

    def __str__(self):
        return f'{self.full_name} ({self.get_role_display()})'
