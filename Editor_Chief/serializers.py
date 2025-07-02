# serializers.py
from rest_framework import serializers
from django.contrib.auth.models import User
from .models import EditorInChief

from rest_framework import serializers
from django.contrib.auth.models import User
from .models import EditorInChief

class EditorInChiefRegistrationSerializer(serializers.ModelSerializer):
    first_name = serializers.CharField(write_only=True)
    last_name = serializers.CharField(write_only=True)
    email = serializers.EmailField(write_only=True)
    password = serializers.CharField(write_only=True)

    class Meta:
        model = EditorInChief
        fields = [
            'first_name', 
            'last_name', 
            'email', 
            'password',
            'phone_number',
            'profile_picture',
            'cv',
            'institution',
            'position_title',
            'country',
            'editor_bio',
            'orcid_id',
            'linkedin_profile',
            'google_scholar_profile',
            'scopus_id',
            'web_of_science_id'
        ]

    '''def validate_email(self, value):
        if User.objects.filter(username=value).exists():
            raise serializers.ValidationError("A user with this email already exists.")
        return value'''

    def create(self, validated_data):
        first_name = validated_data.pop('first_name')
        last_name = validated_data.pop('last_name')
        email = validated_data.pop('email')
        password = validated_data.pop('password')

        user = User.objects.create_user(
            username=first_name,
            first_name=first_name,
            last_name=last_name,
            email=email,
            password=password
        )

        # Create EditorInChief with is_approved=False by default
        eic = EditorInChief.objects.create(user=user, is_approved=False, **validated_data)
        return eic

class EditorInChiefLoginResponseSerializer(serializers.ModelSerializer):
    email = serializers.EmailField(source='user.email')
    full_name = serializers.CharField(source='user.get_full_name')
    is_approved = serializers.BooleanField()

    class Meta:
        model = EditorInChief
        fields = ['id', 'email', 'full_name', 'is_approved', 'institution']

# serializers.py
class EditorInChiefUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = EditorInChief
        fields = [
            'phone_number',
            'profile_picture',
            'cv',
            'institution',
            'position_title',
            'country',
            'editor_bio',
            'orcid_id',
            'linkedin_profile',
            'google_scholar_profile',
            'scopus_id',
            'web_of_science_id'
        ]
        extra_kwargs = {
            'profile_picture': {'required': False},
            'cv': {'required': False}
        }

# serializers.py
class EditorInChiefListSerializer(serializers.ModelSerializer):
    email = serializers.EmailField(source='user.email')
    full_name = serializers.CharField(source='user.get_full_name')
    is_active = serializers.BooleanField(source='user.is_active')

    class Meta:
        model = EditorInChief
        fields = [
            'id',
            'email',
            'full_name',

            'is_active',
            'is_approved',
            'institution',
            'position_title',
            'country',
            'profile_picture',
            'date_joined'
        ]

# serializers.py
class EditorInChiefDetailSerializer(serializers.ModelSerializer):
    email = serializers.EmailField(source='user.email')
    full_name = serializers.CharField(source='user.get_full_name')
    is_active = serializers.BooleanField(source='user.is_active')

    class Meta:
        model = EditorInChief
        fields = [
            'id',
            'email',
            'full_name',
            'is_active',
            'is_approved',
            'phone_number',
            'profile_picture',
            'cv',
            'institution',
            'position_title',
            'country',
            'editor_bio',
            'orcid_id',
            'linkedin_profile',
            'google_scholar_profile',
            'scopus_id',
            'web_of_science_id',
            'date_joined'
        ]

from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
from rest_framework import serializers
from django.contrib.auth import get_user_model
from .models import EditorInChief

User = get_user_model()

class EditorInChiefTokenObtainPairSerializer(TokenObtainPairSerializer):
    username_field = 'email'  # Use email for authentication

    def validate(self, attrs):
        # Custom validation for Editor-in-Chief
        email = attrs.get('email', '')
        password = attrs.get('password', '')

        # Find active users with this email
        users = User.objects.filter(email=email, is_active=True)
        
        if not users.exists():
            raise serializers.ValidationError({'error': 'Invalid email or password'})
        
        # Check each user for matching password and EditorInChief profile
        valid_user = None
        editor_in_chief = None
        for user in users:
            if user.check_password(password):
                try:
                    editor_in_chief = EditorInChief.objects.get(user=user)
                    '''if not editor_in_chief.is_approved:
                        raise serializers.ValidationError({
                            'error': 'Account pending approval', 
                            'is_approved': False
                        })'''
                    valid_user = user
                    break
                except EditorInChief.DoesNotExist:
                    continue
        
        if not valid_user:
            raise serializers.ValidationError({'error': 'No active Editor-in-Chief account found'})

        # Generate tokens
        refresh = self.get_token(valid_user)
        
        # Add custom claims to the token
        refresh['email'] = valid_user.email
        refresh['first_name'] = valid_user.first_name
        refresh['last_name'] = valid_user.last_name
        refresh['editor_in_chief_id'] = editor_in_chief.id
        refresh['is_approved'] = editor_in_chief.is_approved

        # Build profile picture URL if exists
        profile_picture = None
        if editor_in_chief.profile_picture and hasattr(editor_in_chief.profile_picture, 'url'):
            request = self.context.get('request')
            profile_picture = request.build_absolute_uri(editor_in_chief.profile_picture.url)

        return {
            'token': str(refresh.access_token),
            'user_id': valid_user.id,
            'eic_id': editor_in_chief.id,
            'email': valid_user.email,
            'full_name': valid_user.get_full_name(),
            'is_approved': editor_in_chief.is_approved,
            'profile_picture': profile_picture,
            # Include any additional fields you want in the response
            'institution': editor_in_chief.institution,
        }
    
from rest_framework import serializers
from .models import EditorInChiefRecommendation, EditorInChiefFeedback

class EditorInChiefFeedbackSerializer(serializers.ModelSerializer):
    class Meta:
        model = EditorInChiefFeedback
        fields = '__all__'
        read_only_fields = ['created_at', 'updated_at']

class EditorInChiefRecommendationSerializer(serializers.ModelSerializer):
    feedbacks = EditorInChiefFeedbackSerializer(many=True, read_only=True)
    editor_name = serializers.CharField(source='editor_in_chief.user.get_full_name', read_only=True)
    journal_title = serializers.CharField(source='journal.title', read_only=True)
    
    class Meta:
        model = EditorInChiefRecommendation
        fields = [
            'id',
            'journal',
            'journal_title',
            'editor_in_chief',
            'editor_name',
            'recommendation',
            'decision_summary',
            'decision_notes',
            'decision_date',
            'requires_review',
            'review_deadline',
            'is_final_decision',
            'feedbacks'
        ]
        read_only_fields = ['decision_date', 'editor_in_chief']

'''class CreateRecommendationSerializer(serializers.ModelSerializer):
    class Meta:
        model = EditorInChiefRecommendation
        fields = ['journal', 'recommendation', 'decision_summary', 'requires_review', 'review_deadline']
        
    def validate(self, data):
        journal = data.get('journal')
        eic = self.context['request'].user.editorinchief

        # Check if recommendation already exists
        if EditorInChiefRecommendation.objects.filter(journal=journal, editor_in_chief=eic).exists():
            raise serializers.ValidationError("You've already made a recommendation for this journal.")
            
        return data'''

'''class CreateRecommendationSerializer(serializers.ModelSerializer):
    editor_in_chief = serializers.PrimaryKeyRelatedField(
        queryset=EditorInChief.objects.all(),
        required=True
    )
    
    class Meta:
        model = EditorInChiefRecommendation
        fields = [
            'journal', 
            'editor_in_chief',  # Now required in request data
            'recommendation', 
            'decision_summary', 
            'requires_review', 
            'review_deadline'
        ]
        
    def validate(self, data):
        journal = data.get('journal')
        editor_in_chief = data.get('editor_in_chief')  # Get from input data instead of request.user

        # Check for existing recommendation
        if EditorInChiefRecommendation.objects.filter(
            journal=journal, 
            editor_in_chief=editor_in_chief
        ).exists():
            raise serializers.ValidationError(
                "This editor has already made a recommendation for this journal."
            )
            
        return data'''

class CreateRecommendationSerializer(serializers.ModelSerializer):
    editor_in_chief = serializers.PrimaryKeyRelatedField(
        queryset=EditorInChief.objects.all(),
        required=True
    )
    
    class Meta:
        model = EditorInChiefRecommendation
        fields = [
            'journal', 
            'editor_in_chief',
            'recommendation', 
            'decision_summary', 
            'decision_notes',  # Added
            'requires_review', 
            'review_deadline',
            'is_final_decision'  # Added
        ]
        
    def validate(self, data):
        journal = data.get('journal')
        editor_in_chief = data.get('editor_in_chief')

        # Check for existing recommendation
        if EditorInChiefRecommendation.objects.filter(
            journal=journal, 
            editor_in_chief=editor_in_chief
        ).exists():
            raise serializers.ValidationError(
                "This editor has already made a recommendation for this journal."
            )
            
        # Validate that decision_notes is provided if is_final_decision is True
        if data.get('is_final_decision', False) and not data.get('decision_notes'):
            raise serializers.ValidationError(
                "Decision notes are required when making a final decision."
            )
            
        return data

class UpdateRecommendationSerializer(serializers.ModelSerializer):
    class Meta:
        model = EditorInChiefRecommendation
        fields = ['recommendation', 'decision_summary', 'decision_notes', 'is_final_decision']
        
    def validate_is_final_decision(self, value):
        if value and not self.instance.decision_summary:
            raise serializers.ValidationError("Cannot mark as final decision without a summary.")
        return value
    
class EditorInChiefRecommendationDetailSerializer(serializers.ModelSerializer):
    class Meta:
        model = EditorInChiefRecommendation
        fields = [
            'id',
            'journal',
            'editor_in_chief',
            'recommendation',
            'decision_summary',
            'decision_notes',
            'decision_date',
            'requires_review',
            'review_deadline',
            'is_final_decision',
        ]
        depth = 0  # Remove nested serialization