from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .api_views import AppointmentViewSet, SessionNoteViewSet
from . import views

router = DefaultRouter()
router.register('appointments', AppointmentViewSet, basename='appointment-api')
router.register('notes', SessionNoteViewSet, basename='note-api')

urlpatterns = [
    # REST API endpoints
    path('api/', include(router.urls)),

    # Existing template views
    path('', views.list_appointments, name='list_appointments'),
    path('book/', views.book_appointment, name='book_appointment'),
    path('cancel/<int:appointment_id>/', views.cancel_appointment, name='cancel_appointment'),
    path('confirm/<int:appointment_id>/', views.confirm_appointment, name='confirm_appointment'),
    path('complete/<int:appointment_id>/', views.complete_appointment, name='complete_appointment'),
    path('notes/<int:appointment_id>/', views.session_notes, name='session_notes'),
]