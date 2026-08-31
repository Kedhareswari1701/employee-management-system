"""Signals that keep derived data consistent when users/leave-types change."""

from django.db.models.signals import post_save
from django.dispatch import receiver

from accounts.models import User
from leaves.models import LeaveBalance, LeaveType


@receiver(post_save, sender=User)
def ensure_leave_balances_on_user_creation(sender, instance, created, **kwargs):
    """When a new user (non-admin) is created, grant default leave balances."""
    if not created:
        return
    if instance.role == User.Role.ADMIN:
        return
    _sync_balances_for_user(instance)


def _sync_balances_for_user(user):
    for leave_type in LeaveType.objects.filter(is_active=True):
        LeaveBalance.objects.get_or_create(
            employee=user,
            leave_type=leave_type,
            defaults={'allocated_days': leave_type.default_days},
        )


@receiver(post_save, sender=LeaveType)
def create_balances_for_new_leave_type(sender, instance, created, **kwargs):
    """When a new leave type is created, create balances for existing users."""
    if not created or not instance.is_active:
        return
    for employee in User.objects.filter(is_active=True).exclude(role=User.Role.ADMIN):
        LeaveBalance.objects.get_or_create(
            employee=employee,
            leave_type=instance,
            defaults={'allocated_days': instance.default_days},
        )
