from django.contrib import admin
from .models import CrisisLog

# Register CrisisLog in Django admin
@admin.register(CrisisLog)
class CrisisLogAdmin(admin.ModelAdmin):
    list_display = ('user', 'detected_keyword', 'timestamp', 'reviewed')
    list_filter = ('reviewed', 'timestamp')
    search_fields = ('user__username', 'text_snippet', 'detected_keyword')
