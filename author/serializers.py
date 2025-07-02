from rest_framework import serializers
from django.contrib.auth.models import User
from .models import Author
from django.core.exceptions import ValidationError
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
from rest_framework_simplejwt.tokens import RefreshToken

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['username', 'email', 'password','first_name', 'last_name']
        extra_kwargs = {
            'password': {'write_only': True}
        }

    '''def validate_email(self, value):
        if self.instance is None or self.instance.email != value:
            if User.objects.filter(email=value).exists():
                raise serializers.ValidationError("A user with this email already exists.")
        return value'''

    def create(self, validated_data):
        return User.objects.create_user(**validated_data)

    def update(self, instance, validated_data):
        instance.username = validated_data.get('username', instance.username)
        instance.email = validated_data.get('email', instance.email)
        if 'password' in validated_data:
            instance.set_password(validated_data['password'])
        instance.save()
        return instance

class AuthorSerializer(serializers.ModelSerializer):
    user = UserSerializer()
    #profile_picture = serializers.SerializerMethodField()
    profile_picture = serializers.ImageField(required=False, allow_null=True)

    class Meta:
        model = Author
        fields = [
            'id', 'user', 'phone_number', 'profile_picture', 'institution', 'country', 'city',
            'department', 'position_title', 'address', 'orcid_id', 'research_interests',
            'google_scholar_profile', 'personal_website', 'biography', 'languages_spoken',
            'reviewer_interest', 'corresponding_author', 'date_joined'
        ]

    def get_profile_picture(self, obj):
        request = self.context.get('request')
        if obj.profile_picture and hasattr(obj.profile_picture, 'url'):
            return request.build_absolute_uri(obj.profile_picture.url)
        return None

    def create(self, validated_data):
        user_data = validated_data.pop('user')

        # Check if the email or username already exists
        '''if User.objects.filter(email=user_data['email']).exists():
            raise ValidationError({"email": "A user with this email already exists."})'''

        if User.objects.filter(username=user_data['username']).exists():
            raise ValidationError({"username": "A user with this username already exists."})

        user_serializer = UserSerializer(data=user_data)
        user_serializer.is_valid(raise_exception=True)
        user = user_serializer.save()
        return Author.objects.create(user=user, **validated_data)

    def update(self, instance, validated_data):
        user_data = validated_data.pop('user', None)
        if user_data:
            user_serializer = UserSerializer(instance=instance.user, data=user_data, partial=True)
            user_serializer.is_valid(raise_exception=True)
            user_serializer.save()

        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.save()
        return instance

from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
from rest_framework import serializers
from django.contrib.auth import get_user_model
from .models import Author

class CustomTokenObtainPairSerializer(TokenObtainPairSerializer):
    username_field = 'email'  # Important: Set this to use email as username

    def validate(self, attrs):
        # Manually handle the authentication
        email = attrs.get('email', '')
        password = attrs.get('password', '')

        # Find all active users with this email
        users = User.objects.filter(email=email, is_active=True)
        
        if not users.exists():
            raise serializers.ValidationError({'error': 'Invalid email or password'})
        
        # Check each user for matching password
        valid_user = None
        for user in users:
            if user.check_password(password):
                try:
                    Author.objects.get(user=user)
                    valid_user = user
                    break
                except Author.DoesNotExist:
                    continue
        
        if not valid_user:
            raise serializers.ValidationError({'error': 'No active author account found'})

        # Generate tokens
        refresh = self.get_token(valid_user)
        
        # Add custom claims
        refresh['email'] = valid_user.email
        refresh['first_name'] = valid_user.first_name
        refresh['last_name'] = valid_user.last_name
        refresh['author_id'] = valid_user.author.id

        return {
            'id': valid_user.author.id,
            'username': valid_user.username,
            'email': valid_user.email,
            'first_name': valid_user.first_name,
            'last_name': valid_user.last_name,
            'token': str(refresh.access_token)
        }