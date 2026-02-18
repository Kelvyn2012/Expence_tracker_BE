from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from django.db import connection

@api_view(['GET'])
@permission_classes([AllowAny])
def health_check(request):
    try:
        connection.ensure_connection()
        db_valid = connection.is_usable()
    except Exception:
        db_valid = False
        
    return Response({
        "status": "ok",
        "database": "connected" if db_valid else "disconnected"
    })
