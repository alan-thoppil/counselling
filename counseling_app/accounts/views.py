from django.shortcuts import render, redirect
from django.contrib.auth import login, logout, authenticate
from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth.decorators import login_required
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


def login_view(request):
    if request.method == 'POST':
        form = AuthenticationForm(data=request.POST)
        if form.is_valid():
            user = form.get_user()
            login(request, user)
            if isinstance(user, User):
                messages.success(request, f'Welcome back, {user.username}!')
                if user.is_patient():
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


def index(request):
    if request.user.is_authenticated:
        if hasattr(request.user, 'role'):
            if request.user.is_patient():
                return redirect('patient_dashboard')
            elif request.user.is_therapist():
                return redirect('therapist_dashboard')
        return redirect('/admin/')
    return render(request, 'accounts/index.html')