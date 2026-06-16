from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login, logout, authenticate
from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth.decorators import login_required
from django.views.decorators.http import require_POST
from django.http import JsonResponse
from django.contrib import messages
from .forms import PatientRegistrationForm, TherapistRegistrationForm
from .models import User, PatientProfile, TherapistProfile


def register_patient(request):
    if request.method == 'POST':
        form = PatientRegistrationForm(request.POST)
        if form.is_valid():
            user = form.save()
            PatientProfile.objects.create(user=user)
            login(request, user)
            messages.success(request, 'Account created successfully!')
            return redirect('patient_dashboard')
    else:
        form = PatientRegistrationForm()
    return render(request, 'accounts/register_patient.html', {'form': form})


def register_therapist(request):
    if request.method == 'POST':
        form = TherapistRegistrationForm(request.POST)
        if form.is_valid():
            user = form.save()
            TherapistProfile.objects.create(
                user=user,
                specialisation=form.cleaned_data.get('specialisation', ''),
                bio=form.cleaned_data.get('bio', '')
            )
            login(request, user)
            messages.success(request, 'Therapist account created!')
            return redirect('therapist_dashboard')
    else:
        form = TherapistRegistrationForm()
    return render(request, 'accounts/register_therapist.html', {'form': form})


def register_choice(request):
    if request.user.is_authenticated:
        if request.user.role == 'admin' or request.user.is_superuser:
            return redirect('admin_dashboard')
        elif request.user.is_patient():
            return redirect('patient_dashboard')
        elif request.user.is_therapist():
            return redirect('therapist_dashboard')
        return redirect('index')
    return render(request, 'accounts/register_choice.html')



def login_view(request):
    if request.method == 'POST':
        form = AuthenticationForm(data=request.POST)
        if form.is_valid():
            user = form.get_user()
            login(request, user)
            if isinstance(user, User):
                messages.success(request, f'Welcome back, {user.username}!')
                if user.role == 'admin' or user.is_superuser:
                    return redirect('admin_dashboard')
                elif user.is_patient():
                    return redirect('patient_dashboard')
                elif user.is_therapist():
                    return redirect('therapist_dashboard')
                else:
                    return redirect('/admin/')
            else:
                messages.success(request, 'Welcome back!')
                return redirect('/admin/')
    else:
        form = AuthenticationForm()
    return render(request, 'accounts/login.html', {'form': form})


def logout_view(request):
    logout(request)
    messages.info(request, 'You have been logged out.')
    return redirect('login')


@login_required
def patient_dashboard(request):
    therapists = User.objects.filter(role='therapist')
    return render(request, 'accounts/patient_dashboard.html', {'therapists': therapists})


@login_required
def therapist_dashboard(request):
    return render(request, 'accounts/therapist_dashboard.html')


@login_required
def admin_dashboard(request):
    if not (request.user.is_superuser or getattr(request.user, 'role', '') == 'admin'):
        return redirect('index')
    
    # Calculate stats
    from appointments.models import Appointment
    from content.models import Article
    
    total_patients = User.objects.filter(role='patient').count()
    total_therapists = User.objects.filter(role='therapist').count()
    total_bookings = Appointment.objects.count()
    total_articles = Article.objects.count()
    
    context = {
        'total_patients': total_patients,
        'total_therapists': total_therapists,
        'total_bookings': total_bookings,
        'total_articles': total_articles
    }
    return render(request, 'accounts/admin_dashboard.html', context)


@login_required
def list_users(request):
    if not (request.user.is_superuser or getattr(request.user, 'role', '') == 'admin'):
        return JsonResponse({'error': 'Unauthorized'}, status=403)
    users = User.objects.all().order_by('username')
    data = [{
        'id': u.id,
        'username': u.username,
        'email': u.email,
        'role': u.role,
        'phone': u.phone,
        'is_active': u.is_active
    } for u in users]
    return JsonResponse({'users': data})


@login_required
@require_POST
def toggle_user_active(request, user_id):
    if not (request.user.is_superuser or getattr(request.user, 'role', '') == 'admin'):
        return JsonResponse({'error': 'Unauthorized'}, status=403)
    user = get_object_or_404(User, id=user_id)
    if user == request.user:
        return JsonResponse({'error': 'Cannot deactivate yourself.'}, status=400)
    user.is_active = not user.is_active
    user.save()
    return JsonResponse({'success': True, 'is_active': user.is_active})


@login_required
def get_enrolled_users(request, user_id):
    if not (request.user.is_superuser or getattr(request.user, 'role', '') == 'admin'):
        return JsonResponse({'error': 'Unauthorized'}, status=403)
    
    from appointments.models import Appointment
    
    target_user = get_object_or_404(User, id=user_id)
    enrolled_data = []
    
    if target_user.role == 'therapist':
        # Get unique patients enrolled with this therapist through appointments
        appointments = Appointment.objects.filter(therapist=target_user).select_related('patient')
        patient_map = {}
        for appt in appointments:
            p = appt.patient
            if p.id not in patient_map:
                patient_map[p.id] = {
                    'id': p.id,
                    'username': p.username,
                    'email': p.email,
                    'phone': p.phone or '—',
                    'is_active': p.is_active,
                    'booking_count': 0,
                    'statuses': set()
                }
            patient_map[p.id]['booking_count'] += 1
            patient_map[p.id]['statuses'].add(appt.status)
        
        for pid in patient_map:
            patient_map[pid]['statuses'] = list(patient_map[pid]['statuses'])
            
        enrolled_data = list(patient_map.values())
        
    elif target_user.role == 'patient':
        # Get unique therapists enrolled with this patient through appointments
        appointments = Appointment.objects.filter(patient=target_user).select_related('therapist')
        therapist_map = {}
        for appt in appointments:
            t = appt.therapist
            if t.id not in therapist_map:
                specialisation = '—'
                if hasattr(t, 'therapist_profile'):
                    specialisation = t.therapist_profile.specialisation or 'General'
                therapist_map[t.id] = {
                    'id': t.id,
                    'username': t.username,
                    'email': t.email,
                    'specialisation': specialisation,
                    'phone': t.phone or '—',
                    'is_active': t.is_active,
                    'booking_count': 0,
                    'statuses': set()
                }
            therapist_map[t.id]['booking_count'] += 1
            therapist_map[t.id]['statuses'].add(appt.status)
            
        for tid in therapist_map:
            therapist_map[tid]['statuses'] = list(therapist_map[tid]['statuses'])
            
        enrolled_data = list(therapist_map.values())
        
    return JsonResponse({
        'target_user': {
            'username': target_user.username,
            'role': target_user.role
        },
        'enrolled': enrolled_data
    })




def index(request):
    if request.user.is_authenticated:
        if hasattr(request.user, 'role'):
            if request.user.role == 'admin' or request.user.is_superuser:
                return redirect('admin_dashboard')
            elif request.user.is_patient():
                return redirect('patient_dashboard')
            elif request.user.is_therapist():
                return redirect('therapist_dashboard')
        return redirect('/admin/')
    return render(request, 'accounts/index.html')