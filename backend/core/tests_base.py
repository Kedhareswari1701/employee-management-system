from datetime import date, timedelta

from rest_framework.test import APITestCase

from accounts.models import User
from departments.models import Department
from leaves.models import LeaveBalance, LeaveType


class APITestCaseBase(APITestCase):
    """Shared helpers and fixtures for API tests."""

    def create_user(self, username='employee', role=User.Role.EMPLOYEE, **kwargs):
        defaults = {
            'username': username,
            'email': f'{username}@test.com',
            'manager': None,
            'department': None,
        }
        defaults.update(kwargs)
        user = User.objects.create_user(password='testpass123', **defaults)
        user.role = role
        user.save()
        return user

    def create_department(self, name='Engineering', code='ENG'):
        return Department.objects.get_or_create(name=name, defaults={'code': code})[0]

    def create_leave_type(self, name='Annual Leave', code='ANNUAL', default_days=20):
        return LeaveType.objects.get_or_create(
            name=name, defaults={'code': code, 'default_days': default_days}
        )[0]

    def create_balance(self, user, leave_type, allocated=20, used=0):
        balance, _ = LeaveBalance.objects.get_or_create(
            employee=user,
            leave_type=leave_type,
            defaults={'allocated_days': allocated, 'used_days': used},
        )
        balance.allocated_days = allocated
        balance.used_days = used
        balance.save()
        return balance

    def authorize(self, user):
        url = '/api/token/'
        response = self.client.post(url, {'username': user.username, 'password': 'testpass123'})
        token = response.data['access']
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {token}')
        return response
