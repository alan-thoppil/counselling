from django.db import models
from accounts.models import User


class Appointment(models.Model):
    STATUS_CHOICES = (
        ('pending', 'Pending'),
        ('confirmed', 'Confirmed'),
        ('cancelled', 'Cancelled'),
        ('completed', 'Completed'),
    )

    patient = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='patient_appointments'
    )
    therapist = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='therapist_appointments'
    )
    date = models.DateField()
    time = models.TimeField()
    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default='pending'
    )
    reason = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    session_note: 'SessionNote'

    class Meta:
        ordering = ['-date', '-time']

    def __str__(self):
        return f"{self.patient.username} → {self.therapist.username} on {self.date} at {self.time}"

    def is_pending(self):
        return self.status == 'pending'

    def is_confirmed(self):
        return self.status == 'confirmed'

    def cancel(self):
        self.status = 'cancelled'
        self.save()

    def confirm(self):
        self.status = 'confirmed'
        self.save()

    def complete(self):
        self.status = 'completed'
        self.save()


class SessionNote(models.Model):
    appointment = models.OneToOneField(
        Appointment,
        on_delete=models.CASCADE,
        related_name='session_note'
    )
    therapist = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='session_notes'
    )
    private_note = models.TextField()
    shared_summary = models.TextField(blank=True)
    ai_summary = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Note for appointment {self.appointment.id}"