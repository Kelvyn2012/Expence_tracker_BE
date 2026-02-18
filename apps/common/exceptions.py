from rest_framework.views import exception_handler
from rest_framework.response import Response
from rest_framework import status

def custom_exception_handler(exc, context):
    response = exception_handler(exc, context)

    if response is not None:
        custom_response_data = {
            "success": False,
            "error": {
                "code": response.status_code,
                "message": response.data.get("detail", "An error occurred"),
                "details": response.data
            }
        }
        # If detail is the only key, we can simplify/redundant it, but keeping it in details is fine.
        # Often DRF returns {"field": ["error"]}, so we want to keep that structure in details.
        
        response.data = custom_response_data

    return response
