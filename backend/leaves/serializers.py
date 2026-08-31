from datetime import date

from rest_framework import serializers

from leaves.models import LeaveBalance, LeaveRequest, LeaveType


class LeaveTypeSerializer(serializers.ModelSerializer):
    class Meta:
        model = LeaveType
        fields = ['id', 'name', 'code', 'default_days', 'description', 'is_paid', 'is_active', 'created_at']
        read_only_fields = ['id', 'created_at']


class LeaveBalanceSerializer(serializers.ModelSerializer):
    leave_type_name = serializers.CharField(source='leave_type.name', read_only=True)
    remaining_days = serializers.IntegerField(read_only=True)

    class Meta:
        model = LeaveBalance
        fields = ['id', 'employee', 'employee_name', 'leave_type', 'leave_type_name',
                  'allocated_days', 'used_days', 'remaining_days']
        read_only_fields = ['id', 'used_days']

    employee_name = serializers.SerializerMethodField()

    def get_employee_name(self, obj):
        return obj.employee.full_name


class LeaveRequestSerializer(serializers.ModelSerializer):
    employee_name = serializers.SerializerMethodField()
    leave_type_name = serializers.CharField(source='leave_type.name', read_only=True)
    reviewed_by_name = serializers.SerializerMethodField()

    class Meta:
        model = LeaveRequest
        fields = [
            'id', 'employee', 'employee_name', 'leave_type', 'leave_type_name',
            'start_date', 'end_date', 'duration_days', 'reason', 'status',
            'reviewed_by', 'reviewed_by_name', 'review_note', 'reviewed_at',
            'created_at', 'updated_at',
        ]
        read_only_fields = [
            'id', 'employee_name', 'reviewed_by', 'reviewed_by_name', 'review_note',
            'reviewed_at', 'created_at', 'updated_at', 'status', 'duration_days',
        ]

    def get_employee_name(self, obj):
        return obj.employee.full_name

    def get_reviewed_by_name(self, obj):
        return obj.reviewed_by.full_name if obj.reviewed_by else None


class LeaveRequestCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = LeaveRequest
        fields = ['leave_type', 'start_date', 'end_date', 'duration_days', 'reason']
        extra_kwargs = {'duration_days': {'required': False}}

    def validate(self, attrs):
        start = attrs.get('start_date')
        end = attrs.get('end_date')
        if start and end and start > end:
            raise serializers.ValidationError('Start date cannot be after end date.')
        if start and start < date.today():
            raise serializers.ValidationError('Leave start date cannot be in the past.')
        if 'duration_days' not in attrs or not attrs.get('duration_days'):
            attrs['duration_days'] = (end - start).days + 1 if start and end else 1
        return attrs


class ReviewSerializer(serializers.Serializer):
    status = serializers.ChoiceField(choices=['approved', 'rejected'])
    review_note = serializers.CharField(required=False, allow_blank=True)

    def validate_status(self, value):
        if value not in ('approved', 'rejected'):
            raise serializers.ValidationError('Status must be approved or rejected.')
        return value
