from django.db import models
from django.conf import settings

# Category model to group articles
class Category(models.Model):
    name = models.CharField(max_length=100)
    slug = models.SlugField(max_length=120, unique=True)
    description = models.TextField(blank=True)

    class Meta:
        verbose_name_plural = "Categories"

    def __str__(self):
        return self.name


# Article model for psychological resources/education
class Article(models.Model):
    title = models.CharField(max_length=200)
    slug = models.SlugField(max_length=220, unique=True)
    body = models.TextField()
    category = models.ForeignKey(
        Category, 
        on_delete=models.CASCADE, 
        related_name='articles'
    )
    author = models.ForeignKey(
        settings.AUTH_USER_MODEL, 
        on_delete=models.CASCADE, 
        related_name='articles'
    )
    is_published = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return self.title


# Assessment model for PHQ-9 or GAD-7 assessment logs
class Assessment(models.Model):
    TYPE_CHOICES = (
        ('phq9', 'PHQ-9 (Patient Health Questionnaire-9)'),
        ('gad7', 'GAD-7 (Generalized Anxiety Disorder-7)'),
    )

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL, 
        on_delete=models.CASCADE, 
        related_name='assessments'
    )
    type = models.CharField(max_length=10, choices=TYPE_CHOICES)
    answers = models.JSONField()
    score = models.IntegerField()
    interpretation = models.CharField(max_length=100)
    taken_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-taken_at']

    def __str__(self):
        return f"{self.user.username} - {self.get_type_display()} ({self.score})"
