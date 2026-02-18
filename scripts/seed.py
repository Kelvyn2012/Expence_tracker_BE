import os
import sys
import django
import random
from datetime import timedelta
from django.utils import timezone
from decimal import Decimal

# Setup Django environment
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings.base")
django.setup()

from django.contrib.auth import get_user_model
from apps.expenses.models import Expense

User = get_user_model()

def run_seed():
    print("Seeding data...")
    
    # Create Demo User
    email = "demo@example.com"
    if not User.objects.filter(email=email).exists():
        user = User.objects.create_user(
            email=email,
            password="password123",
            first_name="Demo",
            last_name="User",
            is_email_verified=True
        )
        print(f"Created user: {email}")
    else:
        user = User.objects.get(email=email)
        print(f"User {email} already exists")

    # Create Expenses
    categories = ['Food', 'Transport', 'Utilities', 'Entertainment', 'Health']
    
    # Clear existing expenses for demo user to avoid duplicates on re-run
    # Expense.objects.filter(user=user).delete() 
    
    if Expense.objects.filter(user=user).count() < 5:
        print("Creating expenses...")
        for i in range(20):
            date = timezone.now().date() - timedelta(days=random.randint(0, 30))
            category = random.choice(categories)
            amount = Decimal(random.randint(10, 200)) + Decimal(random.randint(0, 99)) / 100
            
            Expense.objects.create(
                user=user,
                title=f"{category} expense {i+1}",
                amount=amount,
                currency="USD",
                category=category,
                expense_date=date,
                notes=f"Notes for expense {i+1}"
            )
        print("Created 20 expenses")
    else:
        print("Expenses already exist")

    print("Seeding complete.")

if __name__ == "__main__":
    run_seed()
