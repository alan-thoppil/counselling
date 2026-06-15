from django.urls import path
from . import views

urlpatterns = [
    path('articles/', views.list_articles, name='list_articles'),
    path('articles/<int:article_id>/', views.article_detail, name='article_detail'),
    path('categories/', views.list_categories, name='list_categories'),
    path('assessment/', views.assessment, name='assessment'),
]