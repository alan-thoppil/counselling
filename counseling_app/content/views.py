import json
from django.http import JsonResponse
from django.contrib.auth.decorators import login_required
from django.views.decorators.http import require_http_methods
from .models import Article, Assessment

# View to list all published articles
@login_required
@require_http_methods(["GET"])
def article_list(request):
    articles = Article.objects.filter(is_published=True)
    data = []
    for a in articles:
        data.append({
            'id': a.id,
            'title': a.title,
            'slug': a.slug,
            'category': {
                'id': a.category.id,
                'name': a.category.name,
                'slug': a.category.slug
            },
            'author': a.author.username,
            'created_at': a.created_at.isoformat(),
            'updated_at': a.updated_at.isoformat()
        })
    return JsonResponse(data, safe=False)


# View to retrieve a single published article by slug
@login_required
@require_http_methods(["GET"])
def article_detail(request, slug):
    try:
        a = Article.objects.get(slug=slug, is_published=True)
        return JsonResponse({
            'id': a.id,
            'title': a.title,
            'slug': a.slug,
            'body': a.body,
            'category': {
                'id': a.category.id,
                'name': a.category.name,
                'slug': a.category.slug
            },
            'author': a.author.username,
            'created_at': a.created_at.isoformat(),
            'updated_at': a.updated_at.isoformat()
        })
    except Article.DoesNotExist:
        return JsonResponse({'error': 'Article not found'}, status=404)


# View to get assessment schemas (GET) or submit and score assessments (POST)
@login_required
@require_http_methods(["GET", "POST"])
def assessment_view(request):
    if request.method == 'GET':
        # Return assessment structure for PHQ-9 and GAD-7
        return JsonResponse({
            'phq9': {
                'title': 'PHQ-9 (Patient Health Questionnaire-9)',
                'choices': [
                    {'value': 0, 'label': 'Not at all'},
                    {'value': 1, 'label': 'Several days'},
                    {'value': 2, 'label': 'More than half the days'},
                    {'value': 3, 'label': 'Nearly every day'}
                ],
                'questions': [
                    'Little interest or pleasure in doing things',
                    'Feeling down, depressed, or hopeless',
                    'Trouble falling or staying asleep, or sleeping too much',
                    'Feeling tired or having little energy',
                    'Poor appetite or overeating',
                    'Feeling bad about yourself — or that you are a failure or have let yourself or your family down',
                    'Trouble concentrating on things, such as reading the newspaper or watching television',
                    'Moving or speaking so slowly that other people could have noticed? Or the opposite — being so fidgety or restless that you have been moving around a lot more than usual',
                    'Thoughts that you would be better off dead or of hurting yourself in some way'
                ]
            },
            'gad7': {
                'title': 'GAD-7 (Generalized Anxiety Disorder-7)',
                'choices': [
                    {'value': 0, 'label': 'Not at all'},
                    {'value': 1, 'label': 'Several days'},
                    {'value': 2, 'label': 'More than half the days'},
                    {'value': 3, 'label': 'Nearly every day'}
                ],
                'questions': [
                    'Feeling nervous, anxious or on edge',
                    'Not being able to stop or control worrying',
                    'Worrying too much about different things',
                    'Trouble relaxing',
                    'Being so restless that it is hard to sit still',
                    'Becoming easily annoyed or irritable',
                    'Feeling afraid as if something awful might happen'
                ]
            }
        })

    elif request.method == 'POST':
        try:
            data = json.loads(request.body)
            assessment_type = data.get('type')
            answers = data.get('answers')

            if not assessment_type or not isinstance(answers, list):
                return JsonResponse({
                    'error': 'Invalid payload. "type" and "answers" list are required.'
                }, status=400)

            if not all(isinstance(x, int) for x in answers):
                return JsonResponse({'error': 'Answers must be a list of integers.'}, status=400)

            score = sum(answers)

            if assessment_type == 'phq9':
                if len(answers) != 9:
                    return JsonResponse({'error': 'PHQ-9 requires exactly 9 answers.'}, status=400)
                # PHQ-9 scoring ranges
                if score <= 4:
                    interpretation = "Minimal depression"
                elif score <= 9:
                    interpretation = "Mild depression"
                elif score <= 14:
                    interpretation = "Moderate depression"
                elif score <= 19:
                    interpretation = "Moderately severe depression"
                else:
                    interpretation = "Severe depression"

            elif assessment_type == 'gad7':
                if len(answers) != 7:
                    return JsonResponse({'error': 'GAD-7 requires exactly 7 answers.'}, status=400)
                # GAD-7 scoring ranges
                if score <= 4:
                    interpretation = "Minimal anxiety"
                elif score <= 9:
                    interpretation = "Mild anxiety"
                elif score <= 14:
                    interpretation = "Moderate anxiety"
                else:
                    interpretation = "Severe anxiety"
            else:
                return JsonResponse({
                    'error': f'Unsupported assessment type: {assessment_type}'
                }, status=400)

            # Create and save assessment log in DB
            assessment = Assessment.objects.create(
                user=request.user,
                type=assessment_type,
                answers=answers,
                score=score,
                interpretation=interpretation
            )

            return JsonResponse({
                'id': assessment.id,
                'user': assessment.user.username,
                'type': assessment.type,
                'score': assessment.score,
                'interpretation': assessment.interpretation,
                'taken_at': assessment.taken_at.isoformat()
            }, status=201)

        except json.JSONDecodeError:
            return JsonResponse({'error': 'Invalid JSON body'}, status=400)
