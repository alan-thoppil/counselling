from django.contrib import admin
from .models import MoodLog, JournalEntry


@admin.register(MoodLog)
class MoodLogAdmin(admin.ModelAdmin):
    list_display = ['user', 'mood_score', 'note', 'logged_at']
    list_filter = ['mood_score', 'logged_at']
    search_fields = ['user__username']


@admin.register(JournalEntry)
class JournalEntryAdmin(admin.ModelAdmin):
    list_display = ['user', 'title', 'sentiment', 'created_at']
    list_filter = ['sentiment', 'created_at']
    search_fields = ['user__username', 'title', 'content']