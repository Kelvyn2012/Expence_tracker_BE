import pytest
from django.urls import reverse
from rest_framework.test import APIClient
from rest_framework import status
from django.contrib.auth import get_user_model
from apps.expenses.models import Expense
from decimal import Decimal
from datetime import date

User = get_user_model()

@pytest.mark.django_db
class TestExpenses:
    def setup_method(self):
        self.client = APIClient()
        self.user = User.objects.create_user(email='user@example.com', password='password123', is_email_verified=True)
        self.client.force_authenticate(user=self.user)
        self.list_url = reverse('expense-list')

    def test_unverified_user_cannot_access_expenses(self):
        unverified_user = User.objects.create_user(email='unverified@example.com', password='password123', is_email_verified=False)
        self.client.force_authenticate(user=unverified_user)
        response = self.client.get(self.list_url)
        assert response.status_code == status.HTTP_403_FORBIDDEN

    def test_create_expense(self):
        payload = {
            'title': 'Lunch',
            'amount': '15.50',
            'currency': 'USD',
            'category': 'Food',
            'expense_date': '2023-10-01'
        }
        response = self.client.post(self.list_url, payload)
        assert response.status_code == status.HTTP_201_CREATED
        assert Expense.objects.filter(user=self.user).count() == 1

    def test_list_expenses_filtering(self):
        # Create 2 expenses
        Expense.objects.create(user=self.user, title='Lunch', amount=10, expense_date=date(2023, 10, 1), category='Food')
        Expense.objects.create(user=self.user, title='Taxi', amount=20, expense_date=date(2023, 10, 2), category='Transport')
        
        # Filter by category
        response = self.client.get(self.list_url, {'category': 'Food'})
        assert response.status_code == status.HTTP_200_OK
        assert response.data['count'] == 1
        assert response.data['results'][0]['title'] == 'Lunch'

    def test_monthly_summary(self):
        Expense.objects.create(user=self.user, title='Lunch', amount=10, expense_date=date(2023, 10, 1), category='Food')
        Expense.objects.create(user=self.user, title='Dinner', amount=20, expense_date=date(2023, 10, 2), category='Food')
        Expense.objects.create(user=self.user, title='Taxi', amount=15, expense_date=date(2023, 9, 1), category='Transport') # Different month

        url = reverse('expense-summary')
        response = self.client.get(url, {'month': '2023-10'})
        
        assert response.status_code == status.HTTP_200_OK
        assert response.data['total_spend'] == 30.00
        assert len(response.data['breakdown']) == 1
        assert response.data['breakdown'][0]['category'] == 'Food'

    def test_csv_export(self):
        Expense.objects.create(user=self.user, title='Lunch', amount=10, expense_date=date(2023, 10, 1), category='Food')
        url = reverse('expense-export')
        response = self.client.get(url)
        assert response.status_code == status.HTTP_200_OK
        assert response['Content-Type'] == 'text/csv'
        content = b"".join(response.streaming_content) if response.streaming else response.content
        assert b'Lunch' in content
        assert b'10.00' in content

    def test_user_expense_isolation(self):
        other_user = User.objects.create_user(email='other@example.com', password='password123', is_email_verified=True)
        Expense.objects.create(user=other_user, title='Secret', amount=100, expense_date=date(2023, 10, 1))
        
        response = self.client.get(self.list_url)
        assert response.status_code == status.HTTP_200_OK
        assert response.data['count'] == 0
