from django.contrib import admin
from .models import Category, Article, Assessment

# Register Category in Django admin
@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ('name', 'slug', 'description')
    prepopulated_fields = {'slug': ('name',)}


# Register Article in Django admin
@admin.register(Article)
class ArticleAdmin(admin.ModelAdmin):
    list_display = ('title', 'slug', 'category', 'author', 'is_published', 'created_at', 'updated_at')
    list_filter = ('is_published', 'category', 'created_at')
    search_fields = ('title', 'body')
    prepopulated_fields = {'slug': ('title',)}


# Register Assessment in Django admin
@admin.register(Assessment)
class AssessmentAdmin(admin.ModelAdmin):
    list_display = ('user', 'type', 'score', 'interpretation', 'taken_at')
    list_filter = ('type', 'taken_at')
    search_fields = ('user__username', 'interpretation')
