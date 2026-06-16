from django.urls import path
from . import views

urlpatterns = [
    path('articles/', views.list_articles, name='list_articles'),
    path('articles/<int:article_id>/', views.article_detail, name='article_detail'),
    path('categories/', views.list_categories, name='list_categories'),
    path('assessment/', views.assessment, name='assessment'),
    
    # Administrative endpoints
    path('categories/create/', views.create_category, name='create_category'),
    path('categories/delete/<int:category_id>/', views.delete_category, name='delete_category'),
    path('articles/create/', views.create_article, name='create_article'),
    path('articles/edit/<int:article_id>/', views.edit_article, name='edit_article'),
    path('articles/delete/<int:article_id>/', views.delete_article, name='delete_article'),
]