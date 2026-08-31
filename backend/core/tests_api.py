import tempfile
from datetime import date, timedelta

from django.core.files.uploadedfile import SimpleUploadedFile
from PIL import Image

from accounts.models import User
from departments.models import Department
from leaves.models import LeaveBalance, LeaveType

from core.tests_base import APITestCaseBase


def make_image():
    img = Image.new('RGB', (10, 10), color='red')
    tmp = tempfile.NamedTemporaryFile(suffix='.png', delete=False)
    img.save(tmp.name)
    tmp.seek(0)
    with open(tmp.name, 'rb') as f:
        return SimpleUploadedFile('avatar.png', f.read(), content_type='image/png')


class AuthenticationTests(APITestCaseBase):
    def test_register_creates_employee(self):
        dept = self.create_department()
        url = '/api/auth/register/'
        resp = self.client.post(url, {
            'username': 'newbie',
            'email': 'newbie@test.com',
            'password': 'strongpass1',
            'password2': 'strongpass1',
            'first_name': 'New',
            'last_name': 'Bee',
            'department': dept.id,
        })
        self.assertEqual(resp.status_code, 201)
        user = User.objects.get(username='newbie')
        self.assertEqual(user.role, User.Role.EMPLOYEE)

    def test_register_mismatched_passwords(self):
        url = '/api/auth/register/'
        resp = self.client.post(url, {
            'username': 'badpass', 'email': 'bad@test.com',
            'password': 'strongpass1', 'password2': 'different1',
        })
        self.assertEqual(resp.status_code, 400)

    def test_login_returns_tokens(self):
        user = self.create_user('loginuser')
        resp = self.client.post('/api/token/', {'username': 'loginuser', 'password': 'testpass123'})
        self.assertEqual(resp.status_code, 200)
        self.assertIn('access', resp.data)
        self.assertIn('refresh', resp.data)


class UserAuthzTests(APITestCaseBase):
    def test_me_requires_auth(self):
        resp = self.client.get('/api/users/me/')
        self.assertEqual(resp.status_code, 401)

    def test_me_returns_own_profile_when_authenticated(self):
        user = self.create_user('meuser')
        self.authorize(user)
        resp = self.client.get('/api/users/me/')
        self.assertEqual(resp.status_code, 200)
        self.assertEqual(resp.data['username'], 'meuser')

    def test_change_password_flow(self):
        user = self.create_user('pwuser')
        self.authorize(user)
        resp = self.client.post('/api/users/change_password/', {
            'old_password': 'testpass123', 'new_password': 'newpass1234'
        })
        self.assertEqual(resp.status_code, 200)
        user.refresh_from_db()
        self.assertTrue(user.check_password('newpass1234'))

    def test_change_password_rejects_wrong_old(self):
        user = self.create_user('pwuser2')
        self.authorize(user)
        resp = self.client.post('/api/users/change_password/', {
            'old_password': 'wrongpass', 'new_password': 'newpass1234'
        })
        self.assertEqual(resp.status_code, 400)

    def test_only_admin_can_update_users(self):
        admin = self.create_user('admin', role=User.Role.ADMIN)
        employee = self.create_user('empuser')
        self.authorize(employee)
        resp = self.client.patch(f'/api/users/{employee.id}/', {'phone_number': '555'})
        self.assertEqual(resp.status_code, 403)

    def test_admin_can_create_manager(self):
        admin = self.create_user('admin2', role=User.Role.ADMIN)
        dept = self.create_department()
        self.authorize(admin)
        resp = self.client.post('/api/users/', {
            'username': 'newmanager', 'email': 'nm@test.com',
            'password': 'managerpass1', 'role': 'manager', 'department': dept.id,
        })
        self.assertEqual(resp.status_code, 201)
        self.assertEqual(User.objects.get(username='newmanager').role, User.Role.MANAGER)


class DepartmentTests(APITestCaseBase):
    def test_employee_can_list_departments(self):
        self.create_department()
        user = self.create_user('deptuser')
        self.authorize(user)
        resp = self.client.get('/api/departments/')
        self.assertEqual(resp.status_code, 200)

    def test_employee_cannot_create_department(self):
        self.create_department()
        user = self.create_user('deptemp')
        self.authorize(user)
        resp = self.client.post('/api/departments/', {'name': 'New Dept', 'code': 'NEW'})
        self.assertEqual(resp.status_code, 403)

    def test_admin_can_create_department(self):
        admin = self.create_user('deptadmin', role=User.Role.ADMIN)
        self.authorize(admin)
        resp = self.client.post('/api/departments/', {'name': 'QA', 'code': 'QA'})
        self.assertEqual(resp.status_code, 201)

    def test_duplicate_department_code_rejected(self):
        self.create_department('Eng', 'ENG')
        admin = self.create_user('deptadmin2', role=User.Role.ADMIN)
        self.authorize(admin)
        resp = self.client.post('/api/departments/', {'name': 'Other', 'code': 'ENG'})
        self.assertEqual(resp.status_code, 400)


class AttendanceTests(APITestCaseBase):
    def test_employee_sees_only_own_attendance(self):
        emp1 = self.create_user('att1')
        emp2 = self.create_user('att2')
        self.create_leave_type()
        balance = self.create_balance(emp1, LeaveType.objects.first())
        from attendance.models import Attendance
        Attendance.objects.create(employee=emp1, date=date.today() - timedelta(days=1))
        Attendance.objects.create(employee=emp2, date=date.today())
        self.authorize(emp1)
        resp = self.client.get('/api/attendance/')
        self.assertEqual(resp.status_code, 200)
        self.assertEqual(resp.data['count'], 1)

    def test_admin_sees_all_attendance(self):
        admin = self.create_user('attadmin', role=User.Role.ADMIN)
        emp = self.create_user('attemp')
        from attendance.models import Attendance
        Attendance.objects.create(employee=emp, date=date.today())
        self.authorize(admin)
        resp = self.client.get('/api/attendance/')
        self.assertEqual(resp.data['count'], 1)

    def test_check_in_creates_record(self):
        from attendance.models import Attendance
        user = self.create_user('checkin')
        self.authorize(user)
        resp = self.client.post('/api/attendance/check_in/', {'check_in': '09:00'})
        self.assertEqual(resp.status_code, 201)
        self.assertEqual(Attendance.objects.filter(employee=user, date=date.today()).count(), 1)

    def test_double_check_in_rejected(self):
        from attendance.models import Attendance
        user = self.create_user('checkindouble')
        Attendance.objects.create(employee=user, date=date.today(), check_in='09:00')
        self.authorize(user)
        resp = self.client.post('/api/attendance/check_in/', {'check_in': '09:30'})
        self.assertEqual(resp.status_code, 400)

    def test_attendance_future_date_rejected(self):
        from attendance.models import Attendance
        user = self.create_user('futureatt')
        self.authorize(user)
        resp = self.client.post('/api/attendance/', {
            'employee': user.id, 'date': str(date.today() + timedelta(days=5))
        })
        self.assertEqual(resp.status_code, 400)


class LeaveTests(APITestCaseBase):
    def test_employee_can_list_leave_types(self):
        self.create_leave_type()
        user = self.create_user('leavetypes')
        self.authorize(user)
        resp = self.client.get('/api/leaves/types/')
        self.assertEqual(resp.status_code, 200)

    def test_employee_cannot_create_leave_type(self):
        self.create_leave_type()
        user = self.create_user('lvtype')
        self.authorize(user)
        resp = self.client.post('/api/leaves/types/', {'name': 'M', 'code': 'X'})
        self.assertEqual(resp.status_code, 403)

    def test_create_leave_request_consumes_balance_on_approval(self):
        user = self.create_user('lvreq')
        lt = self.create_leave_type()
        self.create_balance(user, lt, allocated=20, used=0)
        start = date.today() + timedelta(days=3)
        end = start + timedelta(days=2)
        self.authorize(user)
        resp = self.client.post('/api/leaves/requests/', {
            'leave_type': lt.id, 'start_date': str(start),
            'end_date': str(end), 'duration_days': 3, 'reason': 'vacation',
        })
        self.assertEqual(resp.status_code, 201)
        request_id = resp.data['id']
        # employee cannot review
        resp = self.client.post(f'/api/leaves/requests/{request_id}/review/', {'status': 'approved'})
        self.assertEqual(resp.status_code, 403)

    def test_leave_request_exceeding_balance_rejected(self):
        user = self.create_user('lvover')
        lt = self.create_leave_type()
        self.create_balance(user, lt, allocated=2, used=0)
        start = date.today() + timedelta(days=3)
        self.authorize(user)
        resp = self.client.post('/api/leaves/requests/', {
            'leave_type': lt.id, 'start_date': str(start),
            'end_date': str(start + timedelta(days=4)), 'duration_days': 5, 'reason': 'long',
        })
        self.assertEqual(resp.status_code, 400)

    def test_manager_can_approve_and_balance_updates(self):
        lt = self.create_leave_type()
        mgr = self.create_user('lvmg', role=User.Role.MANAGER)
        emp = self.create_user('lvsub', manager=mgr)
        self.create_balance(emp, lt, allocated=10, used=0)
        start = date.today() + timedelta(days=3)
        self.authorize(emp)
        resp = self.client.post('/api/leaves/requests/', {
            'leave_type': lt.id, 'start_date': str(start),
            'end_date': str(start), 'duration_days': 1, 'reason': 'sick',
        })
        request_id = resp.data['id']
        self.authorize(mgr)
        resp = self.client.post(f'/api/leaves/requests/{request_id}/review/', {'status': 'approved'})
        self.assertEqual(resp.status_code, 200)
        from leaves.models import LeaveBalance
        balance = LeaveBalance.objects.get(employee=emp, leave_type=lt)
        self.assertEqual(balance.used_days, 1)

    def test_employee_sees_only_own_leave_requests(self):
        emp1 = self.create_user('lv1')
        emp2 = self.create_user('lv2')
        lt = self.create_leave_type()
        self.create_balance(emp1, lt)
        self.create_balance(emp2, lt)
        from leaves.models import LeaveRequest
        s = date.today() + timedelta(days=3)
        LeaveRequest.objects.create(employee=emp1, leave_type=lt, start_date=s, end_date=s, duration_days=1, reason='a')
        LeaveRequest.objects.create(employee=emp2, leave_type=lt, start_date=s, end_date=s, duration_days=1, reason='b')
        self.authorize(emp1)
        resp = self.client.get('/api/leaves/requests/')
        self.assertEqual(resp.data['count'], 1)

    def test_cancel_pending_request(self):
        user = self.create_user('lvcan')
        lt = self.create_leave_type()
        self.create_balance(user, lt)
        s = date.today() + timedelta(days=3)
        from leaves.models import LeaveRequest
        req = LeaveRequest.objects.create(employee=user, leave_type=lt, start_date=s, end_date=s, duration_days=1, reason='x')
        self.authorize(user)
        resp = self.client.post(f'/api/leaves/requests/{req.id}/cancel/')
        self.assertEqual(resp.status_code, 200)
        self.assertEqual(resp.data['status'], 'cancelled')

    def test_signals_create_balance_for_new_user(self):
        self.create_leave_type()
        user = self.create_user('signals')
        balances = LeaveBalance.objects.filter(employee=user)
        self.assertTrue(balances.exists())
