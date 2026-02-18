import hashlib
import secrets
from datetime import timedelta
from django.utils import timezone
from django.conf import settings
from .models import EmailVerificationToken

def generate_verification_token(user):
    # Generate a random token
    raw_token = secrets.token_urlsafe(32)
    # Hash it
    token_hash = hashlib.sha256(raw_token.encode()).hexdigest()
    
    # Expiry 24 hours
    expires_at = timezone.now() + timedelta(hours=24)
    
    # Invalidate old tokens (optional policy: "Only most recent unexpired unused token should be valid")
    # Actually, the requirement says invalidating older tokens on resend.
    # We can do that in the service that calls this.
    
    token_obj = EmailVerificationToken.objects.create(
        user=user,
        token_hash=token_hash,
        expires_at=expires_at
    )
    
    return raw_token, token_obj

def verify_token(raw_token):
    token_hash = hashlib.sha256(raw_token.encode()).hexdigest()
    
    try:
        token_obj = EmailVerificationToken.objects.get(
            token_hash=token_hash,
            used_at__isnull=True,
            expires_at__gt=timezone.now()
        )
        return token_obj
    except EmailVerificationToken.DoesNotExist:
        return None

def mark_token_used(token_obj):
    token_obj.used_at = timezone.now()
    token_obj.save()
    
    user = token_obj.user
    user.is_email_verified = True
    user.save()
    return user
