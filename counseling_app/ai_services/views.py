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


@login_required
def mood_recommendation_view(request):
    try:
        from mood.models import MoodLog
        from django.conf import settings
        from anthropic import Anthropic

        # Fetch user's latest mood logs
        logs = MoodLog.objects.filter(user=request.user).order_by('-logged_at')[:3]
        if not logs.exists():
            return JsonResponse({
                'recommendation': "Start logging your daily mood, and MindWell will provide tailored recommendations to support you!"
            })
            
        latest_log = logs[0]
        score = latest_log.mood_score
        note = latest_log.note
        
        api_key = getattr(settings, 'ANTHROPIC_API_KEY', None)
        model = getattr(settings, 'ANTHROPIC_MODEL', 'claude-sonnet-4-6')
        
        if not api_key or api_key == 'your-key-here':
            # Fallback recommendations based on score
            if score == 1:
                rec = (
                    "<b>Breathing Exercise (4-7-8 Technique)</b>: Inhale for 4 seconds, hold for 7, and exhale slowly for 8. Repeat this 4 times to calm your nervous system.<br><br>"
                    "<b>Change Your Environment</b>: Step away from screens. Take a gentle 10-minute walk or simply look out a window.<br><br>"
                    "<b>Expressive Writing</b>: Spend 5 minutes writing down what is on your mind without worrying about spelling or grammar, then discard it."
                )
            elif score == 2:
                rec = (
                    "<b>Gentle Stretching</b>: Release physical tension in your neck, shoulders, and back.<br><br>"
                    "<b>Mindful Grounding</b>: Name 5 things you can see, 4 you can touch, 3 you can hear, 2 you can smell, and 1 you can taste.<br><br>"
                    "<b>Hydration Break</b>: Drink a glass of cold water mindfully, paying attention to the temperature and sensation."
                )
            elif score == 3:
                rec = (
                    "<b>Listen to Music</b>: Put on a track that elevates your focus or brings comfort.<br><br>"
                    "<b>Progress Check</b>: List one small thing you completed today and celebrate it.<br><br>"
                    "<b>Social Check-in</b>: Send a quick text or check in on a close friend or family member."
                )
            elif score == 4:
                rec = (
                    "<b>Gratitude Focus</b>: Write down two things you are grateful for today.<br><br>"
                    "<b>Active Movement</b>: Maintain your energy by doing a workout, run, or dancing to your favorite song.<br><br>"
                    "<b>Creative Time</b>: Dedicate 15 minutes to a hobby you enjoy, like drawing, reading, or crafting."
                )
            else: # score == 5
                rec = (
                    "<b>Capture the Moment</b>: Write down what made today so wonderful so you can look back on it on tougher days.<br><br>"
                    "<b>Spread Positive Energy</b>: Complement someone, or share your high spirits with a loved one.<br><br>"
                    "<b>Set a Goal</b>: Channel your positive energy to outline one creative goal for the rest of the week."
                )
            return JsonResponse({'recommendation': rec})

        # Anthropic integration
        client = Anthropic(api_key=api_key)
        
        # Construct message payload
        mood_str = dict(MoodLog.MOOD_CHOICES).get(score, str(score))
        user_context = f"Latest mood rating: {mood_str}. User note: '{note or 'none'}'.\n"
        if len(logs) > 1:
            user_context += "Previous logs:\n"
            for log in logs[1:]:
                prev_mood = dict(MoodLog.MOOD_CHOICES).get(log.mood_score, str(log.mood_score))
                user_context += f"- {prev_mood} with note: '{log.note or 'none'}' on {log.logged_at.date()}\n"

        prompt = (
            f"The user has logged their mood in a mental health app. Here is their context:\n{user_context}\n"
            "Provide 3 short, gentle, and highly actionable self-care or coping recommendations. "
            "Address them directly and empathetically. Keep the recommendations formatting clean using html tags like <b>, <ul>, <li>, etc. for rendering. "
            "Do not include introductory or concluding conversational fluff. Start directly with the recommendations."
        )

        response = client.messages.create(
            model=model,
            max_tokens=500,
            messages=[{
                'role': 'user',
                'content': prompt
            }]
        )

        recommendation_text = ""
        if response.content:
            recommendation_text = response.content[0].text
        else:
            recommendation_text = "Take a moment to rest, stay hydrated, and practice deep breathing."

        return JsonResponse({'recommendation': recommendation_text})

    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)
