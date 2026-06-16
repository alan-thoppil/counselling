import os
# pyrefly: ignore [missing-import]
import django
import datetime
from django.utils import timezone

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'counseling_app.settings')
django.setup()

from accounts.models import User, PatientProfile, TherapistProfile
from content.models import Category, Article
from mood.models import MoodLog

print("Seeding database...")

# Create admin
admin, created = User.objects.get_or_create(
    username='admin1',
    defaults={
        'email': 'admin@aura.com',
        'role': 'admin',
        'is_superuser': True,
        'is_staff': True,
    }
)
if created:
    admin.set_password('admin123')
    admin.save()
    print("Admin user created: admin1 / admin123")
else:
    admin.role = 'admin'
    admin.is_superuser = True
    admin.is_staff = True
    admin.set_password('admin123')
    admin.save()
    print("Admin user updated: admin1 / admin123")

# Create therapist
therapist, created = User.objects.get_or_create(
    username='therapist1',
    defaults={
        'email': 'therapist@aura.com',
        'role': 'therapist',
    }
)
if created:
    therapist.set_password('therapist123')
    therapist.save()
    print("Therapist user created: therapist1 / therapist123")
else:
    therapist.role = 'therapist'
    therapist.set_password('therapist123')
    therapist.save()
    print("Therapist user updated: therapist1 / therapist123")

therapist_profile, created = TherapistProfile.objects.get_or_create(
    user=therapist,
    defaults={
        'specialisation': 'CBT & Mindfulness',
        'bio': 'Licensed clinical psychologist with 5 years experience.',
        'years_of_experience': 5,
        'consultation_fee': 120.00
    }
)

# Create patient
patient, created = User.objects.get_or_create(
    username='patient1',
    defaults={
        'email': 'patient@aura.com',
        'role': 'patient',
    }
)
if created:
    patient.set_password('patient123')
    patient.save()
    print("Patient user created: patient1 / patient123")
else:
    patient.role = 'patient'
    patient.set_password('patient123')
    patient.save()
    print("Patient user updated: patient1 / patient123")

patient_profile, created = PatientProfile.objects.get_or_create(
    user=patient,
    defaults={
        'age': 28,
        'emergency_contact': 'John Doe (123-456-7890)'
    }
)

# Create categories
cat_anxiety, _ = Category.objects.get_or_create(name='Anxiety & Stress', defaults={'description': 'Resources for managing anxiety, panic, and stress.'})
cat_depression, _ = Category.objects.get_or_create(name='Depression', defaults={'description': 'Resources for managing depression and low mood.'})
cat_cbt, _ = Category.objects.get_or_create(name='CBT Techniques', defaults={'description': 'Cognitive Behavioral Therapy exercises.'})

# Create articles
Article.objects.get_or_create(
    title='Understanding CBT (Cognitive Behavioral Therapy)',
    defaults={
        'category': cat_cbt,
        'content_type': 'article',
        'body': 'Cognitive Behavioral Therapy (CBT) is a structured, goal-oriented type of psychotherapy...',
        'author': therapist,
        'is_published': True
    }
)
Article.objects.get_or_create(
    title='5-Minute Guided Breathing Exercise',
    defaults={
        'category': cat_anxiety,
        'content_type': 'exercise',
        'body': 'This simple 5-minute breathing exercise helps deactivate your nervous system...',
        'author': therapist,
        'is_published': True
    }
)

# Create some historical mood logs for patient1 to populate the chart
now = timezone.now()
mood_scores = [3, 2, 4, 3, 5]
notes = ['Feeling a bit neutral today.', 'Stressed with work.', 'Had a good session with therapist.', 'Tired but okay.', 'Feeling amazing!']

# Delete existing mood logs for clean demo
MoodLog.objects.filter(user=patient).delete()

for i, score in enumerate(mood_scores):
    logged_time = now - datetime.timedelta(days=(len(mood_scores) - 1 - i))
    log = MoodLog.objects.create(
        user=patient,
        mood_score=score,
        note=notes[i],
    )
    # Update logged_at directly since auto_now_add won't let us set it in create()
    MoodLog.objects.filter(pk=log.pk).update(logged_at=logged_time)

print("Database seeded successfully!")
