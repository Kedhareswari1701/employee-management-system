"""Shared, lightweight mixins used across the API."""

from rest_framework.permissions import BasePermission


class IsAdminUser(BasePermission):
    """Allow only administrators (role == admin)."""

    def has_permission(self, request, view):
        return bool(request.user and request.user.is_authenticated and request.user.is_admin)


class IsManager(BasePermission):
    """Allow only managers (role == manager)."""

    def has_permission(self, request, view):
        return bool(request.user and request.user.is_authenticated and request.user.is_manager)


class IsStaffMember(BasePermission):
    """Allow admin or manager."""

    def has_permission(self, request, view):
        return bool(
            request.user
            and request.user.is_authenticated
            and (request.user.is_admin or request.user.is_manager)
        )


class IsAdminOrManager(BasePermission):
    """Allow admin or manager."""

    def has_permission(self, request, view):
        return bool(
            request.user
            and request.user.is_authenticated
            and (request.user.is_admin or request.user.is_manager)
        )
