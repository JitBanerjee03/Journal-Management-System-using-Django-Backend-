import random
from django.core.mail import send_mail

def generate_otp():
    return f"{random.randint(100000, 999999)}"

def send_otp_email(user_email, otp):
    send_mail(
        subject='OTP for Journal Deletion',
        message=f'Your OTP to delete the journal is: {otp}',
        from_email='noreply@yourdomain.com',
        recipient_list=[user_email],
    )
