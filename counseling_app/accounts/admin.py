# Custom admin configuration for accounts app.
from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import User, PatientProfile, TherapistProfile


@admin.register(User)
class CustomUserAdmin(UserAdmin):
    list_display = ('username', 'email', 'role', 'is_active')
    list_filter = ('role', 'is_active')
    fieldsets = list(UserAdmin.fieldsets or []) + [
        ('Role & Contact', {'fields': ('role', 'phone', 'profile_photo')}),
    ]



@admin.register(PatientProfile)
class PatientProfileAdmin(admin.ModelAdmin):
    list_display = ('user', 'age', 'created_at')


@admin.register(TherapistProfile)
class TherapistProfileAdmin(admin.ModelAdmin):
    list_display = ('user', 'specialisation', 'is_available', 'years_of_experience')