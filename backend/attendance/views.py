from datetime import date, datetime, time

from django.db.models import Count, Q, Sum
from django.shortcuts import get_object_or_404

from rest_framework import status, viewsets
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from accounts.models import User
from attendance.models import Attendance
from attendance.serializers import (
    AttendanceSerializer,
    CheckInSerializer,
    CheckOutSerializer,
    SummarySerializer,
)


class AttendanceViewSet(viewsets.ModelViewSet):
    """
    Attendance CRUD.

    - Employees: check-in/check-out (self) and view own records.
    - Managers/Admins: view and manage records in scope.
    """
    queryset = Attendance.objects.select_related('employee').all()
    serializer_class = AttendanceSerializer
    filterset_fields = ['employee', 'status', 'date']
    search_fields = ['employee__first_name', 'employee__last_name', 'notes']
    ordering_fields = ['date', 'check_in']
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

    @action(detail=False, methods=['post'])
    def check_in(self, request):
        serializer = CheckInSerializer(data=request.data, context={'request': request})
        serializer.is_valid(raise_exception=True)
        check_in = serializer.validated_data['check_in']
        today = date.today()
        status_val = Attendance.Status.PRESENT
        if check_in > time(9, 15):
            status_val = Attendance.Status.LATE
        record, created = Attendance.objects.get_or_create(
            employee=request.user,
            date=today,
            defaults={'check_in': check_in, 'status': status_val},
        )
        return Response(AttendanceSerializer(record).data, status=status.HTTP_201_CREATED)

    @action(detail=False, methods=['post'])
    def check_out(self, request):
        serializer = CheckOutSerializer(data=request.data, context={'request': request})
        serializer.is_valid(raise_exception=True)
        today = date.today()
        record = Attendance.objects.get(employee=request.user, date=today)
        check_out = serializer.validated_data['check_out']
        record.check_out = check_out
        hours = (
            datetime.combine(date.min, check_out) - datetime.combine(date.min, record.check_in)
        ).total_seconds() / 3600
        record.worked_hours = round(max(hours, 0), 2)
        record.save()
        return Response(AttendanceSerializer(record).data)

    @action(detail=False, methods=['get'])
    def summary(self, request):
        user_param = request.query_params.get('employee')
        if user_param and request.user.is_admin:
            target = get_object_or_404(User, id=user_param)
        elif user_param and request.user.is_manager:
            scope = self.get_queryset().filter(employee_id=user_param)
            if not scope.exists():
                return Response(
                    {'detail': 'This employee is outside your department scope.'},
                    status=status.HTTP_403_FORBIDDEN,
                )
            target = get_object_or_404(User, id=user_param)
        else:
            target = request.user

        year = request.query_params.get('year') or str(date.today().year)
        month = request.query_params.get('month')

        qs = Attendance.objects.filter(employee=target, date__year=year)
        if month:
            qs = qs.filter(date__month=month)

        agg = qs.aggregate(
            present_days=Count('id', filter=Q(status=Attendance.Status.PRESENT)),
            absent_days=Count('id', filter=Q(status=Attendance.Status.ABSENT)),
            late_days=Count('id', filter=Q(status=Attendance.Status.LATE)),
            half_days=Count('id', filter=Q(status=Attendance.Status.HALF_DAY)),
            leave_days=Count('id', filter=Q(status=Attendance.Status.ON_LEAVE)),
            total_worked_hours=Sum('worked_hours'),
        )
        agg['total_days'] = qs.count()
        agg['total_worked_hours'] = float(agg['total_worked_hours'] or 0)

        data = SummarySerializer(agg).data
        present = agg['present_days'] + agg['late_days'] + agg['half_days']
        data['attendance_rate'] = round(present / agg['total_days'] * 100, 2) if agg['total_days'] else 0
        return Response(data)

    @action(detail=False, methods=['get'])
    def today(self, request):
        record = Attendance.objects.filter(employee=request.user, date=date.today()).first()
        if record:
            return Response(AttendanceSerializer(record).data)
        return Response({'checked_in': False, 'message': 'Not checked in yet today.'})
