import json
from django.http import JsonResponse
from django.contrib.auth.decorators import login_required
from django.views.decorators.http import require_POST

from .models import CrisisLog
from .chatbot import get_chatbot_response
from .sentiment import analyze_sentiment
from .crisis import check_crisis
from .matching import match_therapist
from .summariser import summarise_session_note

# POST /api/chat/ -> Chat triage view
@login_required
@require_POST
def chat_view(request):
    try:
        data = json.loads(request.body)
        message = data.get('message')
        history = data.get('history', [])

        if not message:
            return JsonResponse({'error': 'Message is required.'}, status=400)

        response_text = get_chatbot_response(message, history)
        return JsonResponse({'response': response_text})

    except json.JSONDecodeError:
        return JsonResponse({'error': 'Invalid JSON body.'}, status=400)


# POST /api/sentiment/ -> Analyze journal/text sentiment
@login_required
@require_POST
def sentiment_view(request):
    try:
        data = json.loads(request.body)
        text = data.get('text')

        if text is None:
            return JsonResponse({'error': 'Text is required.'}, status=400)

        result = analyze_sentiment(text)
        return JsonResponse(result)

    except json.JSONDecodeError:
        return JsonResponse({'error': 'Invalid JSON body.'}, status=400)


# POST /api/crisis/ -> Verify suicidal/self-harm risk
@login_required
@require_POST
def crisis_view(request):
    try:
        data = json.loads(request.body)
        text = data.get('text')

        if text is None:
            return JsonResponse({'error': 'Text is required.'}, status=400)

        result = check_crisis(text)
        return JsonResponse(result)

    except json.JSONDecodeError:
        return JsonResponse({'error': 'Invalid JSON body.'}, status=400)


# POST /api/match/ -> Find matching specialities from onboarding answers
@login_required
@require_POST
def match_view(request):
    try:
        data = json.loads(request.body)
        answers = data.get('answers')

        if not isinstance(answers, list) or len(answers) != 5:
            return JsonResponse({
                'error': 'Answers list containing exactly 5 elements is required.'
            }, status=400)

        specialisations = match_therapist(answers)
        return JsonResponse({'specialisations': specialisations})

    except json.JSONDecodeError:
        return JsonResponse({'error': 'Invalid JSON body.'}, status=400)


# POST /api/summarise/ -> Summarise therapist session notes
@login_required
@require_POST
def summarise_view(request):
    try:
        data = json.loads(request.body)
        note_text = data.get('note_text')

        if not note_text:
            return JsonResponse({'error': 'Note text is required.'}, status=400)

        summary = summarise_session_note(note_text)
        return JsonResponse({'summary': summary})

    except json.JSONDecodeError:
        return JsonResponse({'error': 'Invalid JSON body.'}, status=400)


# GET/POST /api/crisis-logs/ -> View and review crisis detection alerts
@login_required
def crisis_logs_view(request):
    # Restrict to therapists and admins
    if not (request.user.is_superuser or getattr(request.user, 'role', '') == 'therapist'):
        return JsonResponse({'error': 'Unauthorized'}, status=403)

    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            log_id = data.get('log_id')
            if not log_id:
                return JsonResponse({'error': 'Log ID is required.'}, status=400)
            
            try:
                log = CrisisLog.objects.get(id=log_id)
                log.reviewed = True
                log.save()
                return JsonResponse({'success': True})
            except CrisisLog.DoesNotExist:
                return JsonResponse({'error': 'Crisis log not found.'}, status=404)
        except json.JSONDecodeError:
            return JsonResponse({'error': 'Invalid JSON body.'}, status=400)

    # GET request: list all crisis logs
    logs = CrisisLog.objects.all().select_related('user')
    data = [{
        'id': l.id,
        'username': l.user.username if l.user else 'Anonymous',
        'text_snippet': l.text_snippet,
        'detected_keyword': l.detected_keyword,
        'timestamp': l.timestamp.isoformat(),
        'reviewed': l.reviewed
    } for l in logs]

    return JsonResponse({'crisis_logs': data})
