import csv
from datetime import datetime
from decimal import Decimal
from django.db.models import Sum, Count, F
from django.http import HttpResponse, StreamingHttpResponse
from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated

from apps.common.permissions import IsEmailVerified
from .models import Expense
from .serializers import ExpenseSerializer
from .filters import ExpenseFilter

class ExpenseViewSet(viewsets.ModelViewSet):
    serializer_class = ExpenseSerializer
    permission_classes = [IsAuthenticated, IsEmailVerified]
    filterset_class = ExpenseFilter
    ordering_fields = ['expense_date', 'amount', 'created_at']
    ordering = ['-expense_date']

    def get_queryset(self):
        return Expense.objects.filter(user=self.request.user)

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)

    @action(detail=False, methods=['get'])
    def summary(self, request):
        """
        Get monthly summary of expenses.
        Query param: month=YYYY-MM
        """
        month_str = request.query_params.get('month')
        queryset = self.get_queryset()

        if month_str:
            try:
                date = datetime.strptime(month_str, '%Y-%m')
                queryset = queryset.filter(
                    expense_date__year=date.year,
                    expense_date__month=date.month
                )
            except ValueError:
                return Response(
                    {"error": "Invalid month format. Use YYYY-MM"}, 
                    status=status.HTTP_400_BAD_REQUEST
                )

        # Aggregate totals
        total_spend = queryset.aggregate(total=Sum('amount'))['total'] or 0
        
        # Group by category
        by_category = queryset.values('category').annotate(
            total=Sum('amount'),
            count=Count('id')
        ).order_by('-total')

        # Group by date for timeline
        timeline = queryset.values('expense_date').annotate(
            total=Sum('amount')
        ).order_by('expense_date')

        return Response({
            "total_spend": total_spend,
            "currency": "USD", 
            "breakdown": by_category,
            "timeline": timeline,
            "count": queryset.count()
        })

    @action(detail=False, methods=['get'])
    def export(self, request):
        """
        Stream CSV export of expenses.
        Respects filters (from=YYYY-MM-DD, to=YYYY-MM-DD).
        """
        queryset = self.filter_queryset(self.get_queryset())
        
        response = HttpResponse(content_type='text/csv')
        response['Content-Disposition'] = f'attachment; filename="expenses_{datetime.now().strftime("%Y%m%d")}.csv"'
        
        writer = csv.writer(response)
        writer.writerow(['ID', 'Date', 'Title', 'Amount', 'Currency', 'Category', 'Notes'])
        
        expenses = queryset.values_list(
            'id', 'expense_date', 'title', 'amount', 'currency', 'category', 'notes'
        )
        
        for expense in expenses:
            writer.writerow(expense)
            
        return response

class Echo:
    """An object that implements just the write method of the file-like interface."""
    def write(self, value):
        """Write the value by returning it, instead of storing in a buffer."""
        return value

class StreamingExpenseViewSet(ExpenseViewSet):
    """
    Alternative implementation for streaming large CSVs if needed.
    """
    @action(detail=False, methods=['get'])
    def export_stream(self, request):
        queryset = self.filter_queryset(self.get_queryset())
        
        pseudo_buffer = Echo()
        writer = csv.writer(pseudo_buffer)
        
        def rows():
            yield writer.writerow(['ID', 'Date', 'Title', 'Amount', 'Currency', 'Category', 'Notes'])
            for expense in queryset.iterator():
                yield writer.writerow([
                    str(expense.id),
                    str(expense.expense_date),
                    expense.title,
                    str(expense.amount),
                    expense.currency,
                    expense.category,
                    expense.notes
                ])
                
        response = StreamingHttpResponse(rows(), content_type='text/csv')
        response['Content-Disposition'] = f'attachment; filename="expenses_{datetime.now().strftime("%Y%m%d")}.csv"'
        return response
