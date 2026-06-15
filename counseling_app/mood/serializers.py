from rest_framework import serializers
from .models import MoodLog, JournalEntry

# Django REST Framework Serializer for MoodLog model
class MoodLogSerializer(serializers.ModelSerializer):
    class Meta:
        model = MoodLog
        fields = ['id', 'user', 'mood_score', 'note', 'logged_at']
        read_only_fields = ['id', 'logged_at']


# Django REST Framework Serializer for JournalEntry model
class JournalEntrySerializer(serializers.ModelSerializer):
    class Meta:
        model = JournalEntry
        fields = [
            'id', 
            'user', 
            'title', 
            'content', 
            'sentiment', 
            'sentiment_score', 
            'created_at', 
            'updated_at'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']
