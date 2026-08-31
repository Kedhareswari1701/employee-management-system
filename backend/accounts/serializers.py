from django.contrib.auth import get_user_model
from django.db import transaction

from rest_framework import serializers

from accounts.models import User
from departments.serializers import DepartmentSerializer

User = get_user_model()


class UserSerializer(serializers.ModelSerializer):
    department_detail = DepartmentSerializer(source='department', read_only=True)
    full_name = serializers.CharField(read_only=True)

    class Meta:
        model = User
        fields = [
            'id', 'username', 'email', 'first_name', 'last_name', 'full_name',
            'role', 'department', 'department_detail', 'manager', 'manager_name',
            'phone_number', 'avatar', 'date_joined_company', 'date_joined',
            'is_active',
        ]
        read_only_fields = ['date_joined', 'is_active']

    manager_name = serializers.SerializerMethodField()

    def get_manager_name(self, obj):
        if obj.manager:
            return obj.manager.full_name
        return None

    def validate_username(self, value):
        if self.instance and self.instance.username == value:
            return value
        if User.objects.filter(username=value).exists():
            raise serializers.ValidationError('This username is already taken.')
        return value


class RegisterSerializer(serializers.ModelSerializer):
    """
    Public registration. By default a new user registers as an EMPLOYEE.
    Admin promotion is handled by admins via the user management endpoint.
    """
    password = serializers.CharField(write_only=True, min_length=8, style={'input_type': 'password'})
    password2 = serializers.CharField(write_only=True, min_length=8, style={'input_type': 'password'})

    class Meta:
        model = User
        fields = [
            'username', 'email', 'password', 'password2',
            'first_name', 'last_name', 'phone_number', 'department',
        ]

    def validate(self, attrs):
        if attrs['password'] != attrs['password2']:
            raise serializers.ValidationError({'password2': 'Passwords do not match.'})
        return attrs

    def create(self, validated_data):
        validated_data.pop('password2')
        password = validated_data.pop('password')
        user = User(**validated_data)
        user.role = User.Role.EMPLOYEE
        user.set_password(password)
        user.save()
        return user


class ChangePasswordSerializer(serializers.Serializer):
    old_password = serializers.CharField(write_only=True, style={'input_type': 'password'})
    new_password = serializers.CharField(write_only=True, min_length=8, style={'input_type': 'password'})

    def validate_old_password(self, value):
        user = self.context['request'].user
        if not user.check_password(value):
            raise serializers.ValidationError('Current password is incorrect.')
        return value


class UserCreateSerializer(serializers.ModelSerializer):
    """Admin-only: create users (including managers)."""
    password = serializers.CharField(write_only=True, min_length=8)
    department_detail = DepartmentSerializer(source='department', read_only=True)

    class Meta:
        model = User
        fields = [
            'username', 'email', 'password', 'first_name', 'last_name',
            'role', 'department', 'department_detail', 'manager',
            'phone_number', 'avatar', 'date_joined_company', 'is_active',
        ]

    def create(self, validated_data):
        password = validated_data.pop('password')
        user = User(**validated_data)
        user.set_password(password)
        user.save()
        return user
