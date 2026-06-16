from django.test import TestCase, Client
from django.urls import reverse
from .models import User, PatientProfile, TherapistProfile


class UserRoleTestCase(TestCase):
    def setUp(self):
        self.patient = User.objects.create_user(
            username='patient1', 
            password='password123', 
            role='patient'
        )
        self.therapist = User.objects.create_user(
            username='therapist1', 
            password='password123', 
            role='therapist'
        )

    def test_user_roles(self):
        """Test User model role check functions"""
        self.assertTrue(self.patient.is_patient())
        self.assertFalse(self.patient.is_therapist())
        self.assertTrue(self.therapist.is_therapist())
        self.assertFalse(self.therapist.is_patient())


class RegistrationViewsTestCase(TestCase):
    def setUp(self):
        self.client = Client()

    def test_register_patient_view_get(self):
        """Test patient registration page renders successfully"""
        url = reverse('register_patient')
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'accounts/register_patient.html')

    def test_register_choice_anonymous(self):
        """Test registration choice page renders successfully for unauthenticated users"""
        url = reverse('register_choice')
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'accounts/register_choice.html')

    def test_register_choice_authenticated_patient(self):
        """Test registration choice page redirects authenticated patient to patient dashboard"""
        User.objects.create_user(username='testpatient', password='password123', role='patient')
        self.client.login(username='testpatient', password='password123')
        url = reverse('register_choice')
        response = self.client.get(url)
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, reverse('patient_dashboard'))

    def test_register_choice_authenticated_therapist(self):
        """Test registration choice page redirects authenticated therapist to therapist dashboard"""
        User.objects.create_user(username='testtherapist', password='password123', role='therapist')
        self.client.login(username='testtherapist', password='password123')
        url = reverse('register_choice')
        response = self.client.get(url)
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, reverse('therapist_dashboard'))

    def test_register_patient_view_post_success(self):
        """Test patient registration is successful and redirects to patient dashboard"""
        url = reverse('register_patient')
        data = {
            'username': 'newpatient',
            'email': 'patient@aura.com',
            'phone': '1234567890',
            'password1': 'SecurePass123!',
            'password2': 'SecurePass123!'
        }
        response = self.client.post(url, data)
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, reverse('patient_dashboard'))
        
        # Verify user and profile exist
        user = User.objects.get(username='newpatient')
        self.assertEqual(user.role, 'patient')
        self.assertEqual(user.phone, '1234567890')
        self.assertTrue(PatientProfile.objects.filter(user=user).exists())

    def test_register_therapist_view_get(self):
        """Test therapist registration page renders successfully"""
        url = reverse('register_therapist')
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'accounts/register_therapist.html')

    def test_register_therapist_view_post_success(self):
        """Test therapist registration is successful and redirects to therapist dashboard"""
        url = reverse('register_therapist')
        data = {
            'username': 'newtherapist',
            'email': 'therapist@aura.com',
            'phone': '0987654321',
            'specialisation': 'CBT & Mindfulness',
            'bio': 'Licensed clinical psychologist with 5 years experience.',
            'password1': 'SecurePass123!',
            'password2': 'SecurePass123!'
        }
        response = self.client.post(url, data)
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, reverse('therapist_dashboard'))
        
        # Verify user and profile exist
        user = User.objects.get(username='newtherapist')
        self.assertEqual(user.role, 'therapist')
        self.assertEqual(user.phone, '0987654321')
        
        profile = TherapistProfile.objects.get(user=user)
        self.assertEqual(profile.specialisation, 'CBT & Mindfulness')
        self.assertEqual(profile.bio, 'Licensed clinical psychologist with 5 years experience.')


class AuthViewsTestCase(TestCase):
    def setUp(self):
        self.client = Client()
        self.patient = User.objects.create_user(
            username='patient_user', 
            password='Password123!', 
            role='patient'
        )
        self.therapist = User.objects.create_user(
            username='therapist_user', 
            password='Password123!', 
            role='therapist'
        )

    def test_login_view_get(self):
        """Test login page renders successfully"""
        url = reverse('login')
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'accounts/login.html')

    def test_login_patient_redirect(self):
        """Test patient login redirects to patient dashboard"""
        url = reverse('login')
        data = {
            'username': 'patient_user',
            'password': 'Password123!'
        }
        response = self.client.post(url, data)
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, reverse('patient_dashboard'))

    def test_login_therapist_redirect(self):
        """Test therapist login redirects to therapist dashboard"""
        url = reverse('login')
        data = {
            'username': 'therapist_user',
            'password': 'Password123!'
        }
        response = self.client.post(url, data)
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, reverse('therapist_dashboard'))

    def test_logout_view(self):
        """Test user logout redirects back to login page"""
        self.client.login(username='patient_user', password='Password123!')
        url = reverse('logout')
        response = self.client.post(url)
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, reverse('login'))


class AdminEnrolledUsersTestCase(TestCase):
    def setUp(self):
        self.client = Client()
        self.admin = User.objects.create_superuser(
            username='admin_user',
            password='Password123!',
            email='admin@example.com'
        )
        self.admin.role = 'admin'
        self.admin.save()

        self.patient = User.objects.create_user(
            username='patient_test',
            password='Password123!',
            role='patient'
        )
        self.therapist = User.objects.create_user(
            username='therapist_test',
            password='Password123!',
            role='therapist'
        )
        # Create therapist profile
        TherapistProfile.objects.create(
            user=self.therapist,
            specialisation='Psychotherapy'
        )

        # Create an appointment
        from appointments.models import Appointment
        from datetime import date, time
        self.appt = Appointment.objects.create(
            patient=self.patient,
            therapist=self.therapist,
            date=date(2026, 6, 20),
            time=time(14, 0),
            status='confirmed',
            reason='Anxiety consultation'
        )

    def test_get_enrolled_users_unauthorized(self):
        """Test non-admin cannot access the enrolled users endpoint"""
        self.client.login(username='patient_test', password='Password123!')
        url = reverse('get_enrolled_users', args=[self.therapist.id])
        response = self.client.get(url)
        self.assertEqual(response.status_code, 403)

    def test_get_enrolled_users_therapist_success(self):
        """Test admin can view patients enrolled with a therapist"""
        self.client.login(username='admin_user', password='Password123!')
        url = reverse('get_enrolled_users', args=[self.therapist.id])
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        data = response.json()
        
        self.assertEqual(data['target_user']['username'], 'therapist_test')
        self.assertEqual(data['target_user']['role'], 'therapist')
        self.assertEqual(len(data['enrolled']), 1)
        self.assertEqual(data['enrolled'][0]['username'], 'patient_test')
        self.assertEqual(data['enrolled'][0]['booking_count'], 1)
        self.assertIn('confirmed', data['enrolled'][0]['statuses'])

    def test_get_enrolled_users_patient_success(self):
        """Test admin can view therapists enrolled with a patient"""
        self.client.login(username='admin_user', password='Password123!')
        url = reverse('get_enrolled_users', args=[self.patient.id])
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        data = response.json()
        
        self.assertEqual(data['target_user']['username'], 'patient_test')
        self.assertEqual(data['target_user']['role'], 'patient')
        self.assertEqual(len(data['enrolled']), 1)
        self.assertEqual(data['enrolled'][0]['username'], 'therapist_test')
        self.assertEqual(data['enrolled'][0]['specialisation'], 'Psychotherapy')
        self.assertEqual(data['enrolled'][0]['booking_count'], 1)

