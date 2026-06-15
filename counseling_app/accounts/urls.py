from django.urls import path
from . import views

urlpatterns = [
    path('register/patient/', views.register_patient, name='register_patient'),
    path('register/therapist/', views.register_therapist, name='register_therapist'),
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
    path('dashboard/patient/', views.patient_dashboard, name='patient_dashboard'),
    path('dashboard/therapist/', views.therapist_dashboard, name='therapist_dashboard'),
]