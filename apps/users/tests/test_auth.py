import pytest
from django.urls import reverse
from rest_framework.test import APIClient
from rest_framework import status
from django.contrib.auth import get_user_model
from apps.users.models import EmailVerificationToken

User = get_user_model()

@pytest.mark.django_db
class TestAuth:
    def setup_method(self):
        self.client = APIClient()
        self.signup_url = reverse('signup')
        self.verify_url = reverse('verify_email')
        self.login_url = reverse('token_obtain_pair')

    def test_signup_creates_user_and_token(self):
        payload = {
            'email': 'test@example.com',
            'password': 'password123',
            'first_name': 'Test',
            'last_name': 'User'
        }
        response = self.client.post(self.signup_url, payload)
        assert response.status_code == status.HTTP_201_CREATED
        
        user = User.objects.get(email='test@example.com')
        assert not user.is_email_verified
        assert EmailVerificationToken.objects.filter(user=user).exists()

    def test_verify_email(self):
        # Create user + token
        user = User.objects.create_user(email='verify@example.com', password='password123')
        from apps.users.tokens import generate_verification_token
        raw_token, _ = generate_verification_token(user)
        
        # Verify
        response = self.client.post(self.verify_url, {'token': raw_token})
        assert response.status_code == status.HTTP_200_OK
        
        user.refresh_from_db()
        assert user.is_email_verified

    def test_login_returns_tokens(self):
        user = User.objects.create_user(email='login@example.com', password='password123', is_email_verified=True)
        
        response = self.client.post(self.login_url, {
            'email': 'login@example.com',
            'password': 'password123'
        })
        
        assert response.status_code == status.HTTP_200_OK
        assert 'access' in response.data
        assert 'refresh' in response.data
        assert response.data['user']['email'] == 'login@example.com'
