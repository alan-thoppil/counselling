from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.utils import timezone
from datetime import timedelta
import json
from .models import MoodLog, JournalEntry
from accounts.models import User


@login_required
def log_mood(request):
    if not isinstance(request.user, User):
        return JsonResponse({'error': 'Unauthorized'}, status=401)

    if request.method == 'POST':
        data = json.loads(request.body)
        mood_score = data.get('mood_score')

        if not mood_score or int(mood_score) not in range(1, 6):
            return JsonResponse({'error': 'mood_score must be 1-5'}, status=400)

        log = MoodLog.objects.create(
            user=request.user,
            mood_score=int(mood_score),
            note=data.get('note', '')
        )
        return JsonResponse({
            'success': True,
            'id': log.id,
            'mood_score': log.mood_score,
            'logged_at': str(log.logged_at)
        })

    # GET — list mood logs
    logs = MoodLog.objects.filter(user=request.user)
    data = [{
        'id': l.id,
        'mood_score': l.mood_score,
        'note': l.note,
        'logged_at': str(l.logged_at)
    } for l in logs]
    return JsonResponse({'mood_logs': data})


@login_required
def mood_chart_data(request):
    if not isinstance(request.user, User):
        return JsonResponse({'error': 'Unauthorized'}, status=401)

    days = int(request.GET.get('days', 7))
    since = timezone.now() - timedelta(days=days)
    logs = MoodLog.objects.filter(
        user=request.user,
        logged_at__gte=since
    ).order_by('logged_at')

    data = [{
        'date': str(l.logged_at.date()),
        'mood_score': l.mood_score
    } for l in logs]

    return JsonResponse({'chart_data': data, 'days': days})


@login_required
def journal(request):
    if not isinstance(request.user, User):
        return JsonResponse({'error': 'Unauthorized'}, status=401)

    if request.method == 'POST':
        data = json.loads(request.body)
        content = data.get('content', '').strip()

        if not content:
            return JsonResponse({'error': 'Content is required'}, status=400)

        entry = JournalEntry.objects.create(
            user=request.user,
            title=data.get('title', ''),
            content=content
        )
        return JsonResponse({
            'success': True,
            'id': entry.id,
            'sentiment': entry.sentiment,
            'created_at': str(entry.created_at)
        })

    # GET — list journal entries
    keyword = request.GET.get('search', '')
    entries = JournalEntry.objects.filter(user=request.user)

    if keyword:
        entries = entries.filter(content__icontains=keyword)

    data = [{
        'id': e.id,
        'title': e.title,
        'content': e.content,
        'sentiment': e.sentiment,
        'sentiment_score': e.sentiment_score,
        'created_at': str(e.created_at)
    } for e in entries]

    return JsonResponse({'journal_entries': data})


@login_required
def journal_detail(request, entry_id):
    if not isinstance(request.user, User):
        return JsonResponse({'error': 'Unauthorized'}, status=401)

    try:
        entry = JournalEntry.objects.get(id=entry_id, user=request.user)
    except JournalEntry.DoesNotExist:
        return JsonResponse({'error': 'Not found'}, status=404)

    if request.method == 'GET':
        return JsonResponse({
            'id': entry.id,
            'title': entry.title,
            'content': entry.content,
            'sentiment': entry.sentiment,
            'created_at': str(entry.created_at)
        })

    if request.method == 'DELETE':
        entry.delete()
        return JsonResponse({'success': True})

    return JsonResponse({'error': 'Method not allowed'}, status=405)