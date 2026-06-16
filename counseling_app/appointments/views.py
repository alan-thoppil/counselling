from django.shortcuts import get_object_or_404
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.views.decorators.http import require_http_methods
from django.views.decorators.csrf import csrf_exempt
import json
from .models import Appointment, SessionNote
from accounts.models import User
from .emails import send_appointment_email


@login_required
def book_appointment(request):
    if request.method == 'POST':
        if not isinstance(request.user, User):
            return JsonResponse({'error': 'Unauthorized'}, status=401)
        data = json.loads(request.body)
        
        # Update user's email if provided
        email = data.get('email', '').strip()
        if email:
            request.user.email = email
            request.user.save()

        therapist = get_object_or_404(User, id=data['therapist_id'], role='therapist')
        appointment = Appointment.objects.create(
            patient=request.user,
            therapist=therapist,
            date=data['date'],
            time=data['time'],
            reason=data.get('reason', '')
        )
        send_appointment_email(appointment, 'booked')
        return JsonResponse({
            'success': True,
            'appointment_id': appointment.id,
            'status': appointment.status
        })
    return JsonResponse({'error': 'POST required'}, status=400)


@login_required
def cancel_appointment(request, appointment_id):
    if not isinstance(request.user, User):
        return JsonResponse({'error': 'Unauthorized'}, status=401)
    
    from django.db.models import Q
    appointment = get_object_or_404(
        Appointment,
        Q(patient=request.user) | Q(therapist=request.user),
        id=appointment_id
    )
    appointment.cancel()
    send_appointment_email(appointment, 'cancelled')
    return JsonResponse({'success': True, 'status': appointment.status})


@login_required
def confirm_appointment(request, appointment_id):
    if not isinstance(request.user, User) or not request.user.is_therapist():
        return JsonResponse({'error': 'Only therapists are authorized to confirm appointments.'}, status=403)
    appointment = get_object_or_404(
        Appointment,
        id=appointment_id,
        therapist=request.user
    )
    appointment.confirm()
    send_appointment_email(appointment, 'confirmed')
    return JsonResponse({'success': True, 'status': appointment.status})


@login_required
def complete_appointment(request, appointment_id):
    if not isinstance(request.user, User) or not request.user.is_therapist():
        return JsonResponse({'error': 'Only therapists are authorized to complete appointments.'}, status=403)
    appointment = get_object_or_404(
        Appointment,
        id=appointment_id,
        therapist=request.user
    )
    appointment.complete()
    send_appointment_email(appointment, 'completed')
    return JsonResponse({'success': True, 'status': appointment.status})



@login_required
def list_appointments(request):
    user = request.user
    if not isinstance(user, User):
        return JsonResponse({'error': 'Unauthorized'}, status=401)
    
    if user.is_patient():
        appointments = Appointment.objects.filter(patient=user)
    elif user.is_therapist():
        appointments = Appointment.objects.filter(therapist=user)
    else:
        appointments = Appointment.objects.all()

    data = [{
        'id': a.id,
        'patient': a.patient.username,
        'therapist': a.therapist.username,
        'date': str(a.date),
        'time': str(a.time),
        'status': a.status,
        'reason': a.reason
    } for a in appointments]

    return JsonResponse({'appointments': data})


@login_required
def session_notes(request, appointment_id):
    appointment = get_object_or_404(Appointment, id=appointment_id)

    if request.method == 'GET':
        try:
            note = appointment.session_note
            return JsonResponse({
                'private_note': note.private_note,
                'shared_summary': note.shared_summary,
                'ai_summary': note.ai_summary
            })
        except SessionNote.DoesNotExist:
            return JsonResponse({'error': 'No note found'}, status=404)

    if request.method == 'POST':
        if not isinstance(request.user, User) or not request.user.is_therapist():
            return JsonResponse({'error': 'Therapists only'}, status=403)
        data = json.loads(request.body)
        note, created = SessionNote.objects.update_or_create(
            appointment=appointment,
            defaults={
                'therapist': request.user,
                'private_note': data.get('private_note', ''),
                'shared_summary': data.get('shared_summary', ''),
                'ai_summary': data.get('ai_summary', '')
            }
        )
        return JsonResponse({
            'success': True,
            'created': created,
            'note_id': note.id
        })

    return JsonResponse({'error': 'Method not allowed'}, status=405)