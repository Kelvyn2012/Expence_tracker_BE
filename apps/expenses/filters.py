import django_filters
from .models import Expense

class ExpenseFilter(django_filters.FilterSet):
    from_date = django_filters.DateFilter(field_name='expense_date', lookup_expr='gte')
    to_date = django_filters.DateFilter(field_name='expense_date', lookup_expr='lte')
    min_amount = django_filters.NumberFilter(field_name='amount', lookup_expr='gte')
    max_amount = django_filters.NumberFilter(field_name='amount', lookup_expr='lte')
    category = django_filters.CharFilter(lookup_expr='iexact')
    currency = django_filters.CharFilter(lookup_expr='iexact')

    class Meta:
        model = Expense
        fields = ['category', 'currency', 'from_date', 'to_date', 'min_amount', 'max_amount']
