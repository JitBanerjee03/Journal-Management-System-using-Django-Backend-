from django.urls import path
from .views import *

urlpatterns = [
    path('register/', UserRegistrationAPIView.as_view(), name='user-registration'),
    path('login/', SSOLoginAPIView.as_view(), name='sso-login'),
    path('validate-token/', TokenValidationAPIView.as_view(), name='validate-token'),
    path('request-password-reset-otp/', RequestPasswordResetOTPAPIView.as_view(), name='request-password-reset-otp'),
    path('verify-otp-reset-password/', VerifyOTPAndResetPasswordAPIView.as_view(), name='verify-otp-reset-password'),
]
