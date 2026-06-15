from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from accounts.views import index

# Root URL configuration for counseling_app project
urlpatterns = [
    # Root redirect
    path('', index, name='index'),

    # Django Admin site
    path('admin/', admin.site.urls),
    
    # Accounts, appointments, and mood apps
    path('accounts/', include('accounts.urls')),
    path('appointments/', include('appointments.urls')),
    path('mood/', include('mood.urls')),
    
    # Articles (/content/) and Assessments (/assessment/)
    path('', include('content.urls')),
    
    # AI Services APIs (/api/chat/, /api/sentiment/, etc.)
    path('api/', include('ai_services.urls')),
]

# Serve media files in development environment
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)