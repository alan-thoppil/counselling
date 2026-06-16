from django.urls import path
from . import views

# Routing patterns for ai_services API
urlpatterns = [
    path('chat/', views.chat_view, name='api_chat'),
    path('sentiment/', views.sentiment_view, name='api_sentiment'),
    path('crisis/', views.crisis_view, name='api_crisis'),
    path('match/', views.match_view, name='api_match'),
    path('summarise/', views.summarise_view, name='api_summarise'),
    path('crisis-logs/', views.crisis_logs_view, name='api_crisis_logs'),
    path('mood-recommendation/', views.mood_recommendation_view, name='api_mood_recommendation'),
]
