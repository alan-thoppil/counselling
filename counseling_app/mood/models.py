from django.db import models
from accounts.models import User


class MoodLog(models.Model):
    MOOD_CHOICES = (
        (1, '😞 Very Bad'),
        (2, '😟 Bad'),
        (3, '😐 Neutral'),
        (4, '😊 Good'),
        (5, '😄 Very Good'),
    )

    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='mood_logs'
    )
    mood_score = models.PositiveSmallIntegerField(choices=MOOD_CHOICES)
    note = models.CharField(max_length=300, blank=True)
    logged_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-logged_at']

    def __str__(self):
        return f"{self.user.username} — {self.mood_score} on {self.logged_at.date()}"


class JournalEntry(models.Model):
    SENTIMENT_CHOICES = (
        ('positive', 'Positive'),
        ('negative', 'Negative'),
        ('neutral', 'Neutral'),
        ('pending', 'Pending'),
    )

    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='journal_entries'
    )
    title = models.CharField(max_length=200, blank=True)
    content = models.TextField()
    sentiment = models.CharField(
        max_length=20,
        choices=SENTIMENT_CHOICES,
        default='pending'
    )
    sentiment_score = models.FloatField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.user.username} — {self.title or 'Untitled'} ({self.sentiment})"

    def save(self, *args, **kwargs):
        # Analyze sentiment if the journal entry is new or the sentiment is still pending
        is_new = self.pk is None
        if is_new or self.sentiment == 'pending':
            from ai_services.sentiment import analyze_sentiment
            res = analyze_sentiment(self.content)
            sentiment_val = res.get('sentiment', 'NEUTRAL')
            self.sentiment = str(sentiment_val).lower()
            
            score_val = res.get('score', 0.5)
            self.sentiment_score = float(score_val) if score_val is not None else 0.5
        super().save(*args, **kwargs)