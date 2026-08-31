from django.contrib import admin

from leaves.models import LeaveBalance, LeaveRequest, LeaveType


@admin.register(LeaveType)
class LeaveTypeAdmin(admin.ModelAdmin):
    list_display = ['name', 'code', 'default_days', 'is_paid', 'is_active']
    search_fields = ['name', 'code']


@admin.register(LeaveRequest)
class LeaveRequestAdmin(admin.ModelAdmin):
    list_display = ['employee', 'leave_type', 'start_date', 'end_date', 'duration_days', 'status', 'reviewed_by']
    list_filter = ['status', 'leave_type']
    search_fields = ['employee__first_name', 'employee__last_name', 'reason']
    date_hierarchy = 'created_at'


@admin.register(LeaveBalance)
class LeaveBalanceAdmin(admin.ModelAdmin):
    list_display = ['employee', 'leave_type', 'allocated_days', 'used_days']
    list_filter = ['leave_type']
