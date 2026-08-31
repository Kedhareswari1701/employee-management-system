from datetime import date

from django.conf import settings
from django.db import models


class LeaveType(models.Model):
    """A category of leave an employee can request (e.g. Annual, Sick)."""

    name = models.CharField(max_length=80, unique=True)
    code = models.CharField(max_length=20, unique=True)
    default_days = models.PositiveIntegerField(default=0, help_text='Default number of days granted per year.')
    description = models.TextField(blank=True)
    is_paid = models.BooleanField(default=True)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['name']

    def __str__(self):
        return self.name


class LeaveRequest(models.Model):
    """An employee's request for leave, which a manager/admin approves."""

    class Status(models.TextChoices):
        PENDING = 'pending', 'Pending'
        APPROVED = 'approved', 'Approved'
        REJECTED = 'rejected', 'Rejected'
        CANCELLED = 'cancelled', 'Cancelled'

    employee = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='leave_requests',
    )
    leave_type = models.ForeignKey(LeaveType, on_delete=models.PROTECT, related_name='requests')
    start_date = models.DateField()
    end_date = models.DateField()
    duration_days = models.PositiveIntegerField(default=1, help_text='Number of working days requested.')
    reason = models.TextField()
    status = models.CharField(max_length=20, choices=Status.choices, default=Status.PENDING)
    reviewed_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name='reviewed_leave_requests',
    )
    review_note = models.TextField(blank=True)
    reviewed_at = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created_at']

    def clean(self):
        if self.start_date and self.end_date and self.start_date > self.end_date:
            from django.core.exceptions import ValidationError
            raise ValidationError('Start date cannot be after end date.')
        if self.start_date and self.start_date < date.today():
            from django.core.exceptions import ValidationError
            raise ValidationError('Leave start date cannot be in the past.')

    def __str__(self):
        return f'{self.employee} - {self.leave_type} ({self.start_date} to {self.end_date})'


class LeaveBalance(models.Model):
    """The number of days an employee has available for a given leave type."""

    employee = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='leave_balances',
    )
    leave_type = models.ForeignKey(LeaveType, on_delete=models.CASCADE, related_name='balances')
    allocated_days = models.PositiveIntegerField(default=0)
    used_days = models.PositiveIntegerField(default=0)

    class Meta:
        unique_together = ('employee', 'leave_type')

    @property
    def remaining_days(self):
        return max(self.allocated_days - self.used_days, 0)

    def __str__(self):
        return f'{self.employee} - {self.leave_type}: {self.remaining_days} remaining'
