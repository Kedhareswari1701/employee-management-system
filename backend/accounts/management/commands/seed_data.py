"""Seed the database with demo departments, users, leave types and balances.

Usage:
    python manage.py seed_data
"""

import random
from datetime import date, timedelta

from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from django.db import transaction

from attendance.models import Attendance
from departments.models import Department
from leaves.models import LeaveBalance, LeaveRequest, LeaveType

User = get_user_model()


class Command(BaseCommand):
    help = 'Populate the database with demo data for development.'

    def handle(self, *args, **options):
        with transaction.atomic():
            self._seed_departments()
            self._seed_leave_types()
            self._seed_users()
            self._seed_attendance()
        self.stdout.write(self.style.SUCCESS('Demo data seeded successfully.'))

    def _seed_departments(self):
        departments = [
            ('Engineering', 'ENG'),
            ('Human Resources', 'HR'),
            ('Sales', 'SALES'),
            ('Finance', 'FIN'),
        ]
        for name, code in departments:
            Department.objects.get_or_create(name=name, defaults={'code': code})
        self.stdout.write('Departments created.')

    def _seed_leave_types(self):
        types = [
            ('Annual Leave', 'ANNUAL', 20, True),
            ('Sick Leave', 'SICK', 12, True),
            ('Casual Leave', 'CASUAL', 8, True),
            ('Unpaid Leave', 'UNPAID', 0, False),
        ]
        for name, code, days, paid in types:
            LeaveType.objects.get_or_create(
                code=code,
                defaults={'name': name, 'default_days': days, 'is_paid': paid},
            )
        self.stdout.write('Leave types created.')

    @transaction.atomic
    def _seed_users(self):
        dept_eng = Department.objects.get(code='ENG')
        dept_hr = Department.objects.get(code='HR')

        if not User.objects.filter(username='admin').exists():
            User.objects.create_superuser(
                username='admin',
                email='admin@company.com',
                password='admin12345',
                first_name='System',
                last_name='Admin',
                role=User.Role.ADMIN,
                department=dept_eng,
            )

        if not User.objects.filter(username='manager').exists():
            manager = User.objects.create_user(
                username='manager',
                email='manager@company.com',
                password='manager12345',
                first_name='Jane',
                last_name='Doe',
                role=User.Role.MANAGER,
                department=dept_eng,
            )
            manager.save()

        employees = [
            ('john', 'John', 'Smith', 'john@company.com'),
            ('sara', 'Sara', 'Lee', 'sara@company.com'),
            ('mike', 'Mike', 'Brown', 'mike@company.com'),
        ]

        manager = User.objects.get(username='manager')
        for username, first, last, email in employees:
            if not User.objects.filter(username=username).exists():
                emp = User.objects.create_user(
                    username=username,
                    email=email,
                    password='employee12345',
                    first_name=first,
                    last_name=last,
                    role=User.Role.EMPLOYEE,
                    department=dept_eng,
                    manager=manager,
                )
                emp.save()
        self.stdout.write('Users created.')

    def _seed_attendance(self):
        manager = User.objects.get(username='manager')
        employees = User.objects.filter(role=User.Role.EMPLOYEE)
        today = date.today()
        for employee in employees:
            for days_ago in range(1, 6):
                day = today - timedelta(days=days_ago)
                if day.weekday() >= 5:
                    continue
                status_choice = random.choices(
                    [Attendance.Status.PRESENT, Attendance.Status.LATE, Attendance.Status.ABSENT],
                    weights=[7, 2, 1],
                )[0]
                check_in = '09:00' if status_choice == Attendance.Status.PRESENT else '10:15'
                Attendance.objects.get_or_create(
                    employee=employee,
                    date=day,
                    defaults={
                        'check_in': check_in,
                        'check_out': '18:00',
                        'status': status_choice,
                        'worked_hours': 8.0,
                    },
                )
        self.stdout.write('Attendance seeded.')
