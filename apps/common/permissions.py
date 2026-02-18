from rest_framework import permissions

class IsEmailVerified(permissions.BasePermission):
    """
    Allocates access only to users with verified email addresses.
    """
    message = 'Email verification required.'

    def has_permission(self, request, view):
        return bool(request.user and request.user.is_authenticated and request.user.is_email_verified)
