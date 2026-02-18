from rest_framework import status, generics
from rest_framework.response import Response
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.views import APIView
from rest_framework_simplejwt.views import TokenObtainPairView
from django.db import transaction
from django.conf import settings
from django.core.mail import send_mail  # In prod, use task queue

from .models import User, EmailVerificationToken
from .serializers import (
    SignupSerializer, 
    UserSerializer, 
    CustomTokenObtainPairSerializer, 
    EmailVerificationSerializer,
    ResendVerificationSerializer,
    UserPreferenceSerializer
)
from .tokens import generate_verification_token, verify_token, mark_token_used

class SignupView(generics.CreateAPIView):
    queryset = User.objects.all()
    serializer_class = SignupSerializer
    permission_classes = [AllowAny]

    @transaction.atomic
    def perform_create(self, serializer):
        user = serializer.save()
        # Generate token
        raw_token, token_obj = generate_verification_token(user)
        
        # Send email (In real app, this should be async/Celery)
        # We mock the link for now
        verification_link = f"http://localhost:5173/verify-email?token={raw_token}"
        print(f"------------\nVERIFICATION LINK: {verification_link}\n------------")
        
        # In a real setup, actually send the email
        # send_mail(
        #     "Verify your email",
        #     f"Click here: {verification_link}",
        #     settings.DEFAULT_FROM_EMAIL,
        #     [user.email],
        #     fail_silently=True,
        # )

class VerifyEmailView(APIView):
    permission_classes = [AllowAny]
    serializer_class = EmailVerificationSerializer

    def post(self, request):
        token = request.data.get('token')
        if not token:
            return Response({'error': 'Token required'}, status=status.HTTP_400_BAD_REQUEST)
            
        token_obj = verify_token(token)
        if not token_obj:
            return Response({'error': 'Invalid or expired token'}, status=status.HTTP_400_BAD_REQUEST)
            
        mark_token_used(token_obj)
        return Response({'success': True, 'message': 'Email verified successfully'})

class ResendVerificationView(APIView):
    permission_classes = [AllowAny]
    serializer_class = ResendVerificationSerializer

    def post(self, request):
        email = request.data.get('email')
        try:
            user = User.objects.get(email=email)
        except User.DoesNotExist:
            # Don't reveal user existence? Or maybe do for MVP.
            # Requirement says "no-op success" if already verified.
            return Response({'success': True, 'message': 'If account exists, verification sent.'})
            
        if user.is_email_verified:
            return Response({'success': True, 'message': 'Already verified'})
            
        # Invalidate old tokens
        EmailVerificationToken.objects.filter(user=user, used_at__isnull=True).delete()
        
        # Generate new
        raw_token, token_obj = generate_verification_token(user)
        
        verification_link = f"http://localhost:5173/verify-email?token={raw_token}"
        print(f"------------\nRESEND VERIFICATION LINK: {verification_link}\n------------")
        
        return Response({'success': True, 'message': 'Verification email sent'})

class CustomTokenObtainPairView(TokenObtainPairView):
    serializer_class = CustomTokenObtainPairSerializer

class MeView(APIView):
    permission_classes = [IsAuthenticated]
    
    def get(self, request):
        serializer = UserSerializer(request.user)
        return Response(serializer.data)

class UserPreferencesView(generics.UpdateAPIView):
    permission_classes = [IsAuthenticated]
    serializer_class = UserPreferenceSerializer
    
    def get_object(self):
        return self.request.user
        
    def patch(self, request, *args, **kwargs):
        return super().patch(request, *args, **kwargs)
