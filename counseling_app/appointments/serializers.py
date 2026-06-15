from rest_framework import serializers
from .models import Appointment, SessionNote

# Django REST Framework Serializer for SessionNote model
class SessionNoteSerializer(serializers.ModelSerializer):
    class Meta:
        model = SessionNote
        fields = [
            'id', 
            'appointment', 
            'therapist', 
            'private_note', 
            'shared_summary', 
            'ai_summary', 
            'created_at', 
            'updated_at'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']


# Django REST Framework Serializer for Appointment model
class AppointmentSerializer(serializers.ModelSerializer):
    # Retrieve nested session note if it exists
    session_note = SessionNoteSerializer(read_only=True)

    class Meta:
        model = Appointment
        fields = [
            'id', 
            'patient', 
            'therapist', 
            'date', 
            'time', 
            'status', 
            'reason', 
            'session_note', 
            'created_at', 
            'updated_at'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']
