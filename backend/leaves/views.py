from datetime import datetime

from django.db import transaction
from django.db.models import Count, Q, Sum
from django.shortcuts import get_object_or_404

from rest_framework import status, viewsets
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from accounts.models import User
from leaves.models import LeaveBalance, LeaveRequest, LeaveType
from leaves.serializers import (
    LeaveBalanceSerializer,
    LeaveRequestCreateSerializer,
    LeaveRequestSerializer,
    LeaveTypeSerializer,
    ReviewSerializer,
)
from core.permissions import IsAdminOrManager


class LeaveTypeViewSet(viewsets.ModelViewSet):
    queryset = LeaveType.objects.all()
    serializer_class = LeaveTypeSerializer
    filterset_fields = ['is_active', 'is_paid']
    search_fields = ['name', 'code']

    def get_permissions(self):
        if self.action in ('list', 'retrieve'):
            return [IsAuthenticated()]
        return [IsAdminOrManager()]


class LeaveRequestViewSet(viewsets.ModelViewSet):
    """
    Leave request lifecycle.

    - Employee: create own requests, cancel pending ones.
    - Manager/Admin: list scoped requests, review (approve/reject).
    """
    queryset = LeaveRequest.objects.select_related('employee', 'leave_type', 'reviewed_by').all()
    serializer_class = LeaveRequestSerializer
    filterset_fields = ['employee', 'status', 'leave_type']
    search_fields = ['employee__first_name', 'employee__last_name', 'reason']
    ordering_fields = ['created_at', 'start_date']
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        user = self.request.user
        qs = super().get_queryset()
        if user.is_admin:
            return qs
        if user.is_manager:
            return qs.filter(
                Q(employee=user)
                | Q(employee__manager=user)
                | Q(employee__department=user.department)
            )
        return qs.filter(employee=user)

    def get_serializer_class(self):
        if self.action == 'create':
            return LeaveRequestCreateSerializer
        return LeaveRequestSerializer

    def create(self, request, *args, **kwargs):
        serializer = LeaveRequestCreateSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        data = serializer.validated_data

        try:
            balance = LeaveBalance.objects.get(
                employee=request.user, leave_type=data['leave_type']
            )
        except LeaveBalance.DoesNotExist:
            balance = None

        requested_days = data['duration_days']
        if balance and requested_days > balance.remaining_days:
            return Response(
                {'detail': f'Insufficient balance. '
                           f'You have {balance.remaining_days} day(s) for '
                           f'{data["leave_type"].name} leave.'},
                status=status.HTTP_400_BAD_REQUEST,
            )

        leave_request = LeaveRequest.objects.create(
            employee=request.user,
            leave_type=data['leave_type'],
            start_date=data['start_date'],
            end_date=data['end_date'],
            duration_days=data['duration_days'],
            reason=data.get('reason', ''),
        )
        return Response(
            LeaveRequestSerializer(leave_request).data,
            status=status.HTTP_201_CREATED,
        )

    @action(detail=True, methods=['post'], permission_classes=[IsAdminOrManager])
    def review(self, request, pk=None):
        leave_request = self.get_object()
        if leave_request.status != LeaveRequest.Status.PENDING:
            return Response(
                {'detail': f'This request has already been {leave_request.status}.'},
                status=status.HTTP_400_BAD_REQUEST,
            )
        serializer = ReviewSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        new_status = serializer.validated_data['status']

        with transaction.atomic():
            leave_request.status = new_status
            leave_request.reviewed_by = request.user
            leave_request.review_note = serializer.validated_data.get('review_note', '')
            leave_request.reviewed_at = datetime.now()
            leave_request.save()

            if new_status == LeaveRequest.Status.APPROVED:
                balance, _ = LeaveBalance.objects.get_or_create(
                    employee=leave_request.employee,
                    leave_type=leave_request.leave_type,
                    defaults={'allocated_days': 0},
                )
                balance.used_days += leave_request.duration_days
                balance.save()

        return Response(LeaveRequestSerializer(leave_request).data)

    @action(detail=True, methods=['post'])
    def cancel(self, request, pk=None):
        leave_request = self.get_object()
        if leave_request.employee != request.user and not request.user.is_admin:
            return Response({'detail': 'You can only cancel your own requests.'},
                            status=status.HTTP_403_FORBIDDEN)
        if leave_request.status != LeaveRequest.Status.PENDING:
            return Response(
                {'detail': 'Only pending requests can be cancelled.'},
                status=status.HTTP_400_BAD_REQUEST,
            )
        leave_request.status = LeaveRequest.Status.CANCELLED
        leave_request.save()
        return Response(LeaveRequestSerializer(leave_request).data)


class LeaveBalanceViewSet(viewsets.ModelViewSet):
    """Leave balances. Read most; write for admins."""

    queryset = LeaveBalance.objects.select_related('employee', 'leave_type').all()
    serializer_class = LeaveBalanceSerializer
    filterset_fields = ['employee', 'leave_type']
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        user = self.request.user
        qs = super().get_queryset()
        if user.is_admin:
            return qs
        if user.is_manager:
            return qs.filter(
                Q(employee=user)
                | Q(employee__manager=user)
                | Q(employee__department=user.department)
            )
        return qs.filter(employee=user)

    def get_permissions(self):
        if self.action in ('create', 'update', 'partial_update', 'destroy'):
            return [IsAdminOrManager()]
        return [IsAuthenticated()]
