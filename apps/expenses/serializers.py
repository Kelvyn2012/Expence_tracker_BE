from rest_framework import serializers
from .models import Expense
from django.utils import timezone

class ExpenseSerializer(serializers.ModelSerializer):
    class Meta:
        model = Expense
        fields = [
            'id', 'title', 'amount', 'currency', 'category', 
            'expense_date', 'notes', 'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']

    def validate_amount(self, value):
        if value <= 0:
            raise serializers.ValidationError("Amount must be greater than 0.")
        return value

    def validate_expense_date(self, value):
        if value > timezone.now().date():
             # Optional warning or error, requirement said "optional but recommended"
             # implementing as per requirement "expense_date <= today"
             raise serializers.ValidationError("Expense date cannot be in the future.")
        return value
    
    def create(self, validated_data):
        # Ensure user is attached (though view usually handles this via perform_create, 
        # it's good practice or we can pop it from context if needed, but view perform_create is standard)
        return super().create(validated_data)
