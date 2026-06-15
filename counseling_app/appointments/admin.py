from django.contrib import admin
from .models import Appointment, SessionNote


@admin.register(Appointment)
class AppointmentAdmin(admin.ModelAdmin):
    list_display = ['patient', 'therapist', 'date', 'time', 'status']
    list_filter = ['status', 'date']
    search_fields = ['patient__username', 'therapist__username']


@admin.register(SessionNote)
class SessionNoteAdmin(admin.ModelAdmin):
    list_display = ['appointment', 'therapist', 'created_at']
    search_fields = ['therapist__username']