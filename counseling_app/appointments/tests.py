from django.test import TestCase, Client
from django.urls import reverse
from accounts.models import User
from appointments.models import Appointment

class AppointmentFilteringTests(TestCase):
    def setUp(self):
        # Create users
        self.patient1 = User.objects.create_user(username='patient1', password='password', role='patient')
        self.patient2 = User.objects.create_user(username='patient2', password='password', role='patient')
        
        self.therapist1 = User.objects.create_user(username='therapist1', password='password', role='therapist')
        self.therapist2 = User.objects.create_user(username='therapist2', password='password', role='therapist')
        
        self.admin = User.objects.create_user(username='admin_user', password='password', role='admin')
        self.superuser_patient = User.objects.create_superuser(username='superuser_patient', password='password', role='patient')

        # Create appointments
        self.app1 = Appointment.objects.create(
            patient=self.patient1,
            therapist=self.therapist1,
            date='2026-06-18',
            time='10:00:00'
        )
        self.app2 = Appointment.objects.create(
            patient=self.patient2,
            therapist=self.therapist2,
            date='2026-06-18',
            time='11:00:00'
        )

    def test_admin_gets_all_appointments(self):
        client = Client()
        client.login(username='admin_user', password='password')
        response = client.get(reverse('list_appointments'))
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertEqual(len(data['appointments']), 2)

    def test_superuser_gets_all_appointments_regardless_of_role(self):
        client = Client()
        client.login(username='superuser_patient', password='password')
        response = client.get(reverse('list_appointments'))
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertEqual(len(data['appointments']), 2)

    def test_patient_gets_only_their_own_appointments(self):
        client = Client()
        client.login(username='patient1', password='password')
        response = client.get(reverse('list_appointments'))
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertEqual(len(data['appointments']), 1)
        self.assertEqual(data['appointments'][0]['id'], self.app1.id)

    def test_therapist_gets_only_their_own_appointments(self):
        client = Client()
        client.login(username='therapist2', password='password')
        response = client.get(reverse('list_appointments'))
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertEqual(len(data['appointments']), 1)
        self.assertEqual(data['appointments'][0]['id'], self.app2.id)
