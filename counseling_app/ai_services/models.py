from django.db import models
from django.conf import settings

# CrisisLog model to store instances where crisis keywords are flagged
class CrisisLog(models.Model):
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='crisis_logs',
        null=True,
        blank=True
    )
    text_snippet = models.TextField()
    detected_keyword = models.CharField(max_length=100)
    timestamp = models.DateTimeField(auto_now_add=True)
    reviewed = models.BooleanField(default=False)

    class Meta:
        ordering = ['-timestamp']

    def __str__(self):
        username = self.user.username if self.user else "Anonymous"
        return f"Crisis Alert: {username} on {self.timestamp.date()} (Keyword: {self.detected_keyword})"
