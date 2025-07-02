from rest_framework import serializers
from django.contrib.auth.models import User
from django.contrib.auth.password_validation import validate_password
from journal.models import SubjectArea
from reviewer.models import Reviewer
from AssociateEditor.models import AssociateEditor
from AreaEditor.models import AreaEditor
from Editor_Chief.models import EditorInChief
from author.models import Author
from rest_framework import serializers
from django.contrib.auth import authenticate
from rest_framework.exceptions import AuthenticationFailed
from rest_framework_simplejwt.tokens import RefreshToken
from datetime import timedelta
# serializers.py
import random
from django.core.mail import send_mail
from rest_framework import serializers
from .models import PasswordResetOTP
from django.contrib.auth import get_user_model
class UserRegistrationSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, validators=[validate_password])
    first_name = serializers.CharField(write_only=True)
    last_name = serializers.CharField(write_only=True)
    phone_number = serializers.CharField(write_only=True)
    cv = serializers.FileField(write_only=True, required=False, allow_null=True)
    institution = serializers.CharField(write_only=True)
    position_title = serializers.CharField(write_only=True)
    subject_areas = serializers.PrimaryKeyRelatedField(queryset=SubjectArea.objects.all(), many=True, write_only=True, required=False)
    roles = serializers.ListField(
        child=serializers.ChoiceField(choices=['reviewer', 'associate_editor', 'area_editor', 'editor_in_chief', 'author']),
        write_only=True
    )

    class Meta:
        model = User
        fields = ('first_name', 'last_name', 'email', 'password', 'phone_number', 'cv',
                  'institution', 'position_title', 'subject_areas', 'roles')

    def create(self, validated_data):
        roles = validated_data.pop('roles')
        subject_areas = validated_data.pop('subject_areas', [])
        phone_number = validated_data.pop('phone_number')
        cv = validated_data.pop('cv', None)
        institution = validated_data.pop('institution')
        position_title = validated_data.pop('position_title')

        user = User.objects.create(
            username=validated_data['email'],
            email=validated_data['email'],
            first_name=validated_data['first_name'],
            last_name=validated_data['last_name']
        )
        user.set_password(validated_data['password'])
        user.save()

        for role in roles:
            if role == 'reviewer':
                reviewer = Reviewer.objects.create(
                    user=user,
                    phone_number=phone_number,
                    resume=cv,
                    institution=institution,
                    position_title=position_title,
                )
                reviewer.subject_areas.set(subject_areas)

            elif role == 'associate_editor':
                ae = AssociateEditor.objects.create(
                    user=user,
                    phone_number=phone_number,
                    cv=cv,
                    institution=institution,
                    position_title=position_title,
                )
                ae.subject_areas.set(subject_areas)

            elif role == 'area_editor':
                area_editor = AreaEditor.objects.create(
                    user=user,
                    phone_number=phone_number,
                    cv=cv,
                    institution=institution,
                    position_title=position_title,
                )
                area_editor.subject_areas.set(subject_areas)

            elif role == 'editor_in_chief':
                EditorInChief.objects.create(
                    user=user,
                    phone_number=phone_number,
                    cv=cv,
                    institution=institution,
                    position_title=position_title,
                )

            elif role == 'author':
                Author.objects.create(
                    user=user,
                    phone_number=phone_number,
                    institution=institution,
                    position_title=position_title,
                    country='',  # Fill appropriately if required during registration
                )

        return user

'''class SSOLoginSerializer(serializers.Serializer):
    email = serializers.EmailField()
    password = serializers.CharField(write_only=True)

    def validate(self, attrs):
        email = attrs.get('email')
        password = attrs.get('password')

        user = authenticate(email=email, password=password)
        if not user:
            raise AuthenticationFailed("Invalid credentials")

        # Collect role-specific data
        roles = {}
        try:
            reviewer = Reviewer.objects.get(user=user)
            roles['reviewer_id'] = reviewer.id
            roles['is_reviewer_approved'] = reviewer.is_approved
        except Reviewer.DoesNotExist:
            pass

        try:
            ae = AssociateEditor.objects.get(user=user)
            roles['associate_editor_id'] = ae.id
            roles['is_associate_editor_active'] = ae.is_active
        except AssociateEditor.DoesNotExist:
            pass

        try:
            area_editor = AreaEditor.objects.get(user=user)
            roles['area_editor_id'] = area_editor.id
            roles['is_area_editor_approved'] = area_editor.is_approved
            roles['subject_areas'] = list(area_editor.subject_areas.values('id', 'name'))
        except AreaEditor.DoesNotExist:
            pass

        try:
            eic = EditorInChief.objects.get(user=user)
            roles['eic_id'] = eic.id
            roles['is_editor_in_chief_approved'] = eic.is_approved
            roles['profile_picture'] = eic.profile_picture if eic.profile_picture else None
        except EditorInChief.DoesNotExist:
            pass

        try:
            author = Author.objects.get(user=user)
            roles['id'] = author.id
        except Author.DoesNotExist:
            pass

        refresh = RefreshToken.for_user(user)
        refresh.set_exp(lifetime=timedelta(days=365))  # 1 year validity
        access_token = refresh.access_token

        # Add custom claims to token
        access_token['email'] = user.email
        access_token['first_name'] = user.first_name
        access_token['last_name'] = user.last_name
        access_token['user_id'] = user.id

        for key, value in roles.items():
            access_token[key] = value

        return {
            'token': str(access_token),
            'user_id': user.id,
            'email': user.email,
            'first_name': user.first_name,
            'last_name': user.last_name,
            **roles
        }'''

from rest_framework import serializers
from django.contrib.auth import get_user_model
from rest_framework.exceptions import AuthenticationFailed
from rest_framework_simplejwt.tokens import RefreshToken
from datetime import timedelta
from django.contrib.auth.hashers import check_password

User = get_user_model()

class SSOLoginSerializer(serializers.Serializer):
    email = serializers.EmailField()
    password = serializers.CharField(write_only=True)

    def validate(self, attrs):
        email = attrs.get('email')
        password = attrs.get('password')

        users = User.objects.filter(email=email, is_active=True)
        if not users.exists():
            raise AuthenticationFailed("Invalid credentials")

        user = None
        for u in users:
            if u.check_password(password):
                user = u
                break

        if not user:
            raise AuthenticationFailed("Invalid credentials")

        roles = {}

        # Collect Reviewer info
        try:
            reviewer = Reviewer.objects.get(user=user)
            roles['reviewer_id'] = reviewer.id
        except Reviewer.DoesNotExist:
            pass

        # Collect Associate Editor info
        try:
            ae = AssociateEditor.objects.get(user=user)
            roles['associate_editor_id'] = ae.id
        except AssociateEditor.DoesNotExist:
            pass

        # Collect Area Editor info
        try:
            area_editor = AreaEditor.objects.get(user=user)
            roles['area_editor_id'] = area_editor.id
            roles['is_area_editor_approved'] = area_editor.is_approved
            roles['subject_areas'] = list(area_editor.subject_areas.values('id', 'name'))
        except AreaEditor.DoesNotExist:
            pass

        # Collect Editor in Chief info
        try:
            eic = EditorInChief.objects.get(user=user)
            roles['eic_id'] = eic.id
            roles['is_chief_editor_approved']=eic.is_approved
        except EditorInChief.DoesNotExist:
            pass

        # Collect Author info
        try:
            author = Author.objects.get(user=user)
            roles['id'] = author.id
        except Author.DoesNotExist:
            pass

        # Generate token
        refresh = RefreshToken.for_user(user)
        refresh.set_exp(lifetime=timedelta(days=365))
        access_token = refresh.access_token

        # Add claims to token
        access_token['email'] = user.email
        access_token['first_name'] = user.first_name
        access_token['last_name'] = user.last_name
        access_token['user_id'] = user.id

        for key, value in roles.items():
            access_token[key] = value

        return {
            'token': str(access_token),
            'user_id': user.id,
            'email': user.email,
            'first_name': user.first_name,
            'last_name': user.last_name,
            **roles
        }

from django.core.mail import send_mail
from .models import PasswordResetOTP
import random

class RequestPasswordResetSerializer(serializers.Serializer):
    email = serializers.EmailField()

    def validate_email(self, value):
        if not User.objects.filter(email=value).exists():
            raise serializers.ValidationError("User with this email does not exist.")
        return value

    def create(self, validated_data):
        email = validated_data['email']
        otp = f"{random.randint(100000, 999999)}"

        PasswordResetOTP.objects.create(email=email, otp=otp)

        # === Customized Email Content ===
        subject = "Password Reset Request"
        message = f"""
Hello,

You recently requested to reset your password.

Your One-Time Password (OTP): {otp}

Please enter this OTP on the password reset page to set a new password.

⚠️ Note: This OTP is valid for 5 minutes.

If you did not request this password reset, please ignore this email or contact our support team.
"""
        send_mail(
            subject=subject,
            message=message,
            from_email=None,  # Uses DEFAULT_FROM_EMAIL from settings.py
            recipient_list=[email],
            fail_silently=False,
        )

        return {'detail': 'OTP has been sent to your email.'}

class VerifyOTPAndResetPasswordSerializer(serializers.Serializer):
    email = serializers.EmailField()
    otp = serializers.CharField(max_length=6)
    new_password = serializers.CharField(write_only=True)

    def validate(self, attrs):
        email = attrs.get('email')
        otp = attrs.get('otp')
        try:
            otp_obj = PasswordResetOTP.objects.filter(email=email, otp=otp, is_used=False).latest('created_at')
        except PasswordResetOTP.DoesNotExist:
            raise serializers.ValidationError("Invalid OTP or email.")

        if otp_obj.is_expired():
            raise serializers.ValidationError("OTP has expired.")

        attrs['otp_obj'] = otp_obj
        return attrs

    def create(self, validated_data):
        email = validated_data['email']
        new_password = validated_data['new_password']
        otp_obj = validated_data['otp_obj']

        user = User.objects.get(email=email)
        user.set_password(new_password)
        user.save()

        otp_obj.is_used = True
        otp_obj.save()

        return {'detail': 'Password has been reset successfully.'}
