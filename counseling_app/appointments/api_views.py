from rest_framework import viewsets, permissions, exceptions
from .models import Appointment, SessionNote
from .serializers import AppointmentSerializer, SessionNoteSerializer


class AppointmentViewSet(viewsets.ModelViewSet):
    """
    Django REST Framework ViewSet for Appointment model.
    Enforces role-based query filtering:
    - Patients see their own appointments.
    - Therapists see their assigned appointments.
    - Admins/Staff see all appointments.
    """
    serializer_class = AppointmentSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        user = self.request.user
        if getattr(user, 'is_staff', False) or getattr(user, 'role', '') == 'admin':
            return Appointment.objects.all()
        elif getattr(user, 'role', '') == 'therapist':
            return Appointment.objects.filter(therapist=user)
        else:
            return Appointment.objects.filter(patient=user)

    def perform_create(self, serializer):
        # Default the booking patient to current user if role is patient
        user = self.request.user
        if getattr(user, 'role', '') == 'patient':
            serializer.save(patient=user)
        else:
            serializer.save()


class SessionNoteViewSet(viewsets.ModelViewSet):
    """
    Django REST Framework ViewSet for SessionNote model.
    Restricts CRUD modifications entirely to therapist roles or staff.
    """
    serializer_class = SessionNoteSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        user = self.request.user
        if getattr(user, 'is_staff', False) or getattr(user, 'role', '') == 'admin':
            return SessionNote.objects.all()
        elif getattr(user, 'role', '') == 'therapist':
            return SessionNote.objects.filter(therapist=user)
        else:
            # Patients cannot access session notes directly
            return SessionNote.objects.none()

    def check_permissions(self, request):
        super().check_permissions(request)
        # Block non-therapists and non-staff from performing any modifications
        if request.method not in permissions.SAFE_METHODS:
            user = request.user
            if getattr(user, 'role', '') != 'therapist' and not getattr(user, 'is_staff', False):
                raise exceptions.PermissionDenied("Only therapists are authorized to edit session notes.")

    def perform_create(self, serializer):
        serializer.save(therapist=self.request.user)
