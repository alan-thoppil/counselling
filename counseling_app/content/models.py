from django.db import models
from accounts.models import User


class Category(models.Model):
    name = models.CharField(max_length=100, unique=True)
    description = models.TextField(blank=True)

    class Meta:
        verbose_name_plural = 'Categories'

    def __str__(self):
        return self.name


class Article(models.Model):
    CONTENT_TYPE_CHOICES = (
        ('article', 'Article'),
        ('video', 'Video'),
        ('exercise', 'Exercise'),
    )

    title = models.CharField(max_length=200)
    category = models.ForeignKey(
        Category,
        on_delete=models.SET_NULL,
        null=True,
        related_name='articles'
    )
    content_type = models.CharField(
        max_length=20,
        choices=CONTENT_TYPE_CHOICES,
        default='article'
    )
    body = models.TextField(blank=True)
    video_url = models.URLField(blank=True)
    author = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='authored_articles'
    )
    is_published = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return self.title
class Assessment(models.Model):
    ASSESSMENT_TYPE_CHOICES = (
        ('phq9', 'PHQ-9 (Depression)'),
        ('gad7', 'GAD-7 (Anxiety)'),
    )

    SEVERITY_CHOICES = (
        ('minimal', 'Minimal'),
        ('mild', 'Mild'),
        ('moderate', 'Moderate'),
        ('moderately_severe', 'Moderately Severe'),
        ('severe', 'Severe'),
    )

    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='assessments'
    )
    assessment_type = models.CharField(
        max_length=10,
        choices=ASSESSMENT_TYPE_CHOICES
    )
    answers = models.JSONField()  # stores list of scores per question
    total_score = models.PositiveSmallIntegerField()
    severity = models.CharField(max_length=20, choices=SEVERITY_CHOICES)
    recommendation = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.user.username} — {self.assessment_type.upper()} ({self.total_score})"

    @staticmethod
    def calculate_severity(assessment_type, total_score):
        """Returns severity level and recommendation based on score"""
        if assessment_type == 'phq9':
            if total_score <= 4:
                return 'minimal', 'Your responses suggest minimal depression symptoms. Keep up healthy habits like sleep, exercise, and journaling.'
            elif total_score <= 9:
                return 'mild', 'Your responses suggest mild depression symptoms. Consider self-help resources and monitoring your mood.'
            elif total_score <= 14:
                return 'moderate', 'Your responses suggest moderate depression symptoms. We recommend booking a session with a therapist.'
            elif total_score <= 19:
                return 'moderately_severe', 'Your responses suggest moderately severe symptoms. Please consider speaking with a therapist soon.'
            else:
                return 'severe', 'Your responses suggest severe symptoms. We strongly recommend speaking with a therapist as soon as possible.'

        elif assessment_type == 'gad7':
            if total_score <= 4:
                return 'minimal', 'Your responses suggest minimal anxiety symptoms.'
            elif total_score <= 9:
                return 'mild', 'Your responses suggest mild anxiety symptoms. Self-help techniques may help.'
            elif total_score <= 14:
                return 'moderate', 'Your responses suggest moderate anxiety symptoms. Consider booking a therapist session.'
            else:
                return 'severe', 'Your responses suggest severe anxiety symptoms. We recommend speaking with a therapist soon.'

        return 'minimal', ''