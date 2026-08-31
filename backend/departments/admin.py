from django.contrib import admin

from departments.models import Department


@admin.register(Department)
class DepartmentAdmin(admin.ModelAdmin):
    list_display = ['name', 'code', 'is_active', 'employee_count', 'created_at']
    search_fields = ['name', 'code']
    list_filter = ['is_active']

    def employee_count(self, obj):
        return obj.employees.count()
    employee_count.short_description = 'Employees'
