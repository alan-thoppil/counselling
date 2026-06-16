from django.urls import path
from . import views

urlpatterns = [
    path('register/', views.register_choice, name='register_choice'),
    path('register/patient/', views.register_patient, name='register_patient'),
    path('register/therapist/', views.register_therapist, name='register_therapist'),
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
    path('dashboard/patient/', views.patient_dashboard, name='patient_dashboard'),
    path('dashboard/therapist/', views.therapist_dashboard, name='therapist_dashboard'),
    path('dashboard/admin/', views.admin_dashboard, name='admin_dashboard'),
    path('users/', views.list_users, name='list_users'),
    path('users/toggle/<int:user_id>/', views.toggle_user_active, name='toggle_user_active'),
    path('users/<int:user_id>/enrolled/', views.get_enrolled_users, name='get_enrolled_users'),
]