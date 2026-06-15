from django.contrib import admin
from .models import Category, Article, Assessment


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ['name']


@admin.register(Article)
class ArticleAdmin(admin.ModelAdmin):
    list_display = ['title', 'category', 'content_type', 'is_published', 'created_at']
    list_filter = ['category', 'content_type', 'is_published']
    search_fields = ['title', 'body']


@admin.register(Assessment)
class AssessmentAdmin(admin.ModelAdmin):
    list_display = ['user', 'assessment_type', 'total_score', 'severity', 'created_at']
    list_filter = ['assessment_type', 'severity']
    search_fields = ['user__username']
