from django.urls import path
from . import views

urlpatterns = [
    # Article endpoints
    path('content/', views.article_list, name='article_list'),
    path('content/<slug:slug>/', views.article_detail, name='article_detail'),
    
    # Assessment endpoint
    path('assessment/', views.assessment_view, name='assessment'),
]
