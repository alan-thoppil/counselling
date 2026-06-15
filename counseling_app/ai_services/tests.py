from django.test import TestCase, Client
from django.urls import reverse
from accounts.models import User
from ai_services.models import CrisisLog
import json

class CrisisLogsAPITestCase(TestCase):
    def setUp(self):
        self.client = Client()
        
        # Create user accounts
        self.patient = User.objects.create_user(
            username='test_patient',
            password='Password123!',
            role='patient'
        )
        self.therapist = User.objects.create_user(
            username='test_therapist',
            password='Password123!',
            role='therapist'
        )
        self.superuser = User.objects.create_superuser(
            username='test_admin',
            email='admin@aura.com',
            password='Password123!'
        )
        
        # Create sample crisis logs
        self.log_unreviewed = CrisisLog.objects.create(
            user=self.patient,
            text_snippet="I feel like I want to hurt myself today.",
            detected_keyword="hurt myself",
            reviewed=False
        )
        self.log_reviewed = CrisisLog.objects.create(
            user=self.patient,
            text_snippet="No reason to live anymore.",
            detected_keyword="no reason to live",
            reviewed=True
        )
        
        self.url = reverse('api_crisis_logs')

    def test_unauthenticated_access_redirects(self):
        """Test that unauthenticated access redirects to login page"""
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 302)
        self.assertIn('/accounts/login/', response.url)

    def test_patient_access_forbidden(self):
        """Test that patients are forbidden from viewing or modifying crisis logs"""
        self.client.login(username='test_patient', password='Password123!')
        
        # GET request
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 403)
        self.assertEqual(response.json(), {'error': 'Unauthorized'})
        
        # POST request
        response = self.client.post(
            self.url,
            data=json.dumps({'log_id': self.log_unreviewed.id}),
            content_type='application/json'
        )
        self.assertEqual(response.status_code, 403)
        self.assertEqual(response.json(), {'error': 'Unauthorized'})

    def test_therapist_access_granted(self):
        """Test that therapists can successfully retrieve the list of crisis logs"""
        self.client.login(username='test_therapist', password='Password123!')
        
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)
        
        data = response.json()
        self.assertIn('crisis_logs', data)
        self.assertEqual(len(data['crisis_logs']), 2)
        
        # Verify the content details
        log_ids = [item['id'] for item in data['crisis_logs']]
        self.assertIn(self.log_unreviewed.id, log_ids)
        self.assertIn(self.log_reviewed.id, log_ids)
        
        # Check specific log fields
        unreviewed_item = next(item for item in data['crisis_logs'] if item['id'] == self.log_unreviewed.id)
        self.assertEqual(unreviewed_item['username'], 'test_patient')
        self.assertEqual(unreviewed_item['detected_keyword'], 'hurt myself')
        self.assertEqual(unreviewed_item['text_snippet'], 'I feel like I want to hurt myself today.')
        self.assertFalse(unreviewed_item['reviewed'])

    def test_mark_as_reviewed_success(self):
        """Test that a therapist can mark a crisis log as reviewed"""
        self.client.login(username='test_therapist', password='Password123!')
        
        response = self.client.post(
            self.url,
            data=json.dumps({'log_id': self.log_unreviewed.id}),
            content_type='application/json'
        )
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json(), {'success': True})
        
        # Re-fetch and check database state
        self.log_unreviewed.refresh_from_db()
        self.assertTrue(self.log_unreviewed.reviewed)

    def test_mark_as_reviewed_invalid_log_id(self):
        """Test that posting an invalid log ID returns 404"""
        self.client.login(username='test_therapist', password='Password123!')
        
        response = self.client.post(
            self.url,
            data=json.dumps({'log_id': 99999}),
            content_type='application/json'
        )
        self.assertEqual(response.status_code, 404)
        self.assertEqual(response.json(), {'error': 'Crisis log not found.'})

    def test_mark_as_reviewed_missing_log_id(self):
        """Test that posting missing log ID returns 400"""
        self.client.login(username='test_therapist', password='Password123!')
        
        response = self.client.post(
            self.url,
            data=json.dumps({}),
            content_type='application/json'
        )
        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.json(), {'error': 'Log ID is required.'})
