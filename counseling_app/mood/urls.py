from django.urls import path
from . import views

urlpatterns = [
    path('log/', views.log_mood, name='log_mood'),
    path('chart/', views.mood_chart_data, name='mood_chart'),
    path('journal/', views.journal, name='journal'),
    path('journal/<int:entry_id>/', views.journal_detail, name='journal_detail'),
]