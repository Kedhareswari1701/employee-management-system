from datetime import date, time, timedelta

from rest_framework import serializers

from attendance.models import Attendance


class AttendanceSerializer(serializers.ModelSerializer):
    employee_name = serializers.SerializerMethodField()

    class Meta:
        model = Attendance
        fields = [
            'id', 'employee', 'employee_name', 'date', 'check_in', 'check_out',
            'status', 'worked_hours', 'notes', 'created_at', 'updated_at',
        ]
        read_only_fields = ['id', 'employee_name', 'created_at', 'updated_at']

    def get_employee_name(self, obj):
        return obj.employee.full_name

    def validate_date(self, value):
        if value > date.today():
            raise serializers.ValidationError('Cannot record attendance for a future date.')
        return value


class CheckInSerializer(serializers.Serializer):
    check_in = serializers.TimeField()

    def validate_check_in(self, value):
        now = date.today()
        if Attendance.objects.filter(employee=self.context['request'].user, date=now).exists():
            raise serializers.ValidationError('Attendance already recorded for today.')
        return value


class CheckOutSerializer(serializers.Serializer):
    check_out = serializers.TimeField()

    def validate_check_out(self, value):
        user = self.context['request'].user
        today = date.today()
        try:
            record = Attendance.objects.get(employee=user, date=today)
        except Attendance.DoesNotExist:
            raise serializers.ValidationError('You have not checked in today.')
        if record.check_out:
            raise serializers.ValidationError('You have already checked out today.')
        if record.check_in and value <= record.check_in:
            raise serializers.ValidationError('Check-out time must be after check-in time.')
        return value


class SummarySerializer(serializers.Serializer):
    total_days = serializers.IntegerField()
    present_days = serializers.IntegerField()
    absent_days = serializers.IntegerField()
    late_days = serializers.IntegerField()
    half_days = serializers.IntegerField()
    leave_days = serializers.IntegerField()
    total_worked_hours = serializers.FloatField()
