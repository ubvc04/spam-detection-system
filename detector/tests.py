from django.test import TestCase
from django.urls import reverse
from django.test import Client
import json

# Create your tests here.
class DetectorViewsTest(TestCase):
    def setUp(self):
        self.client = Client()
    
    def test_home_page(self):
        """Test that the home page loads correctly."""
        response = self.client.get(reverse('home'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'ML Security Detector')
    
    def test_email_prediction_endpoint(self):
        """Test the email prediction API endpoint."""
        data = {
            'email_text': 'Test email content'
        }
        response = self.client.post(
            reverse('predict_email'),
            data=json.dumps(data),
            content_type='application/json'
        )
        self.assertEqual(response.status_code, 200)
    
    def test_sms_prediction_endpoint(self):
        """Test the SMS prediction API endpoint."""
        data = {
            'sms_text': 'Test SMS content'
        }
        response = self.client.post(
            reverse('predict_sms'),
            data=json.dumps(data),
            content_type='application/json'
        )
        self.assertEqual(response.status_code, 200)
    
    def test_url_prediction_endpoint(self):
        """Test the URL prediction API endpoint."""
        data = {
            'url': 'https://example.com'
        }
        response = self.client.post(
            reverse('predict_url'),
            data=json.dumps(data),
            content_type='application/json'
        )
        self.assertEqual(response.status_code, 200)
