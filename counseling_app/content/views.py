from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404
from django.http import JsonResponse
import json
from .models import Article, Category, Assessment


def list_articles(request):
    category_id = request.GET.get('category')
    content_type = request.GET.get('type')

    articles = Article.objects.filter(is_published=True)

    if category_id:
        articles = articles.filter(category_id=category_id)
    if content_type:
        articles = articles.filter(content_type=content_type)

    data = [{
        'id': a.id,
        'title': a.title,
        'category': a.category.name if a.category else None,
        'content_type': a.content_type,
        'body': a.body[:200],  # preview
        'video_url': a.video_url,
        'created_at': str(a.created_at)
    } for a in articles]

    return JsonResponse({'articles': data})


def article_detail(request, article_id):
    article = get_object_or_404(Article, id=article_id, is_published=True)
    return JsonResponse({
        'id': article.id,
        'title': article.title,
        'category': article.category.name if article.category else None,
        'content_type': article.content_type,
        'body': article.body,
        'video_url': article.video_url,
        'created_at': str(article.created_at)
    })


def list_categories(request):
    categories = Category.objects.all()
    data = [{
        'id': c.id,
        'name': c.name,
        'description': c.description,
        'article_count': Article.objects.filter(category=c).count()
    } for c in categories]
    return JsonResponse({'categories': data})


# PHQ-9 questions
PHQ9_QUESTIONS = [
    "Little interest or pleasure in doing things",
    "Feeling down, depressed, or hopeless",
    "Trouble falling or staying asleep, or sleeping too much",
    "Feeling tired or having little energy",
    "Poor appetite or overeating",
    "Feeling bad about yourself",
    "Trouble concentrating on things",
    "Moving or speaking slowly, or being restless",
    "Thoughts that you would be better off dead or of hurting yourself"
]

# GAD-7 questions
GAD7_QUESTIONS = [
    "Feeling nervous, anxious, or on edge",
    "Not being able to stop or control worrying",
    "Worrying too much about different things",
    "Trouble relaxing",
    "Being so restless that it's hard to sit still",
    "Becoming easily annoyed or irritable",
    "Feeling afraid as if something awful might happen"
]


@login_required
def assessment(request):
    if request.method == 'GET':
        assessment_type = request.GET.get('type')

        if assessment_type == 'phq9':
            return JsonResponse({'type': 'phq9', 'questions': PHQ9_QUESTIONS})
        elif assessment_type == 'gad7':
            return JsonResponse({'type': 'gad7', 'questions': GAD7_QUESTIONS})

        # List user's past assessments
        assessments = Assessment.objects.filter(user=request.user)
        data = [{
            'id': a.id,
            'type': a.assessment_type,
            'total_score': a.total_score,
            'severity': a.severity,
            'created_at': str(a.created_at)
        } for a in assessments]
        return JsonResponse({'assessments': data})

    if request.method == 'POST':
        data = json.loads(request.body)
        assessment_type = data.get('assessment_type')
        answers = data.get('answers', [])

        if assessment_type not in ['phq9', 'gad7']:
            return JsonResponse({'error': 'Invalid assessment type'}, status=400)

        if not answers or not all(isinstance(a, int) and 0 <= a <= 3 for a in answers):
            return JsonResponse({'error': 'Answers must be a list of integers 0-3'}, status=400)

        total_score = sum(answers)
        severity, recommendation = Assessment.calculate_severity(assessment_type, total_score)

        # Crisis check for PHQ-9 question 9 (self-harm thoughts)
        crisis_flag = False
        if assessment_type == 'phq9' and len(answers) >= 9 and answers[8] > 0:
            crisis_flag = True

        record = Assessment.objects.create(
            user=request.user,
            assessment_type=assessment_type,
            answers=answers,
            total_score=total_score,
            severity=severity,
            recommendation=recommendation
        )

        return JsonResponse({
            'success': True,
            'id': record.id,
            'total_score': total_score,
            'severity': severity,
            'recommendation': recommendation,
            'crisis_flag': crisis_flag
        })

    return JsonResponse({'error': 'Method not allowed'}, status=405)
