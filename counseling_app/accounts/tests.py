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
        """Test therapist registration is successful and redirects to login page as inactive"""
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
        self.assertRedirects(response, reverse('login'))
        
        # Verify user and profile exist and user is inactive (pending approval)
        user = User.objects.get(username='newtherapist')
        self.assertEqual(user.role, 'therapist')
        self.assertEqual(user.phone, '0987654321')
        self.assertFalse(user.is_active)
        
        profile = TherapistProfile.objects.get(user=user)
        self.assertEqual(profile.specialisation, 'CBT & Mindfulness')
        self.assertEqual(profile.bio, 'Licensed clinical psychologist with 5 years experience.')

    def test_login_inactive_therapist_fails(self):
        """Test that an inactive therapist cannot log in and gets a custom error message"""
        # Create an inactive therapist
        User.objects.create_user(
            username='inactive_therapist',
            password='Password123!',
            role='therapist',
            is_active=False
        )
        url = reverse('login')
        data = {
            'username': 'inactive_therapist',
            'password': 'Password123!'
        }
        response = self.client.post(url, data)
        self.assertEqual(response.status_code, 200)
        self.assertFormError(response.context['form'], None, "Your therapist account is pending administrator approval.")


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




class ChangePasswordViewsTestCase(TestCase):
    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(
            username='change_test_user',
            password='CurrentSecurePass123!',
            role='patient'
        )

    def test_change_password_anonymous_denied(self):
        """Test that unauthenticated user cannot access change password endpoint"""
        url = reverse('change_password')
        response = self.client.post(url, data={}, content_type='application/json')
        # Django login_required decorator redirects anonymous users to login page (302)
        self.assertEqual(response.status_code, 302)

    def test_change_password_get_not_allowed(self):
        """Test GET request to change password endpoint is rejected"""
        self.client.login(username='change_test_user', password='CurrentSecurePass123!')
        url = reverse('change_password')
        response = self.client.get(url)
        self.assertEqual(response.status_code, 405)

    def test_change_password_success(self):
        """Test user can successfully change password with valid current and new password"""
        self.client.login(username='change_test_user', password='CurrentSecurePass123!')
        url = reverse('change_password')
        data = {
            'old_password': 'CurrentSecurePass123!',
            'new_password1': 'NewSecurePass999!',
            'new_password2': 'NewSecurePass999!'
        }
        response = self.client.post(url, data=data, content_type='application/json')
        self.assertEqual(response.status_code, 200)
        res_data = response.json()
        self.assertTrue(res_data['success'])
        self.assertEqual(res_data['message'], 'Your password has been changed successfully!')
        
        # Verify the password actually changed
        self.client.logout()
        login_success = self.client.login(username='change_test_user', password='NewSecurePass999!')
        self.assertTrue(login_success)

    def test_change_password_incorrect_old_password(self):
        """Test password change fails if the current password is wrong"""
        self.client.login(username='change_test_user', password='CurrentSecurePass123!')
        url = reverse('change_password')
        data = {
            'old_password': 'WrongCurrentPass!',
            'new_password1': 'NewSecurePass999!',
            'new_password2': 'NewSecurePass999!'
        }
        response = self.client.post(url, data=data, content_type='application/json')
        self.assertEqual(response.status_code, 200)
        res_data = response.json()
        self.assertFalse(res_data['success'])
        self.assertIn('error', res_data)

    def test_change_password_mismatched_new_passwords(self):
        """Test password change fails if new passwords do not match"""
        self.client.login(username='change_test_user', password='CurrentSecurePass123!')
        url = reverse('change_password')
        data = {
            'old_password': 'CurrentSecurePass123!',
            'new_password1': 'NewSecurePass1!',
            'new_password2': 'NewSecurePass2!'
        }
        response = self.client.post(url, data=data, content_type='application/json')
        self.assertEqual(response.status_code, 200)
        res_data = response.json()
        self.assertFalse(res_data['success'])
