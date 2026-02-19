from rest_framework import serializers
from .models import Budget

class BudgetSerializer(serializers.ModelSerializer):
    class Meta:
        model = Budget
        fields = ['id', 'category', 'amount', 'currency', 'created_at']
        read_only_fields = ['id', 'created_at']

    def validate_category(self, value):
        user = self.context['request'].user
        # Check if budget for this category already exists for this user (excluding current instance if update)
        qs = Budget.objects.filter(user=user, category=value)
        if self.instance:
            qs = qs.exclude(pk=self.instance.pk)
        if qs.exists():
            raise serializers.ValidationError("Budget for this category already exists.")
        return value
