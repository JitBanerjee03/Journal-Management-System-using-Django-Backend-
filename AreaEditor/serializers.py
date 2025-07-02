from rest_framework import serializers
from django.contrib.auth.models import User
from .models import AreaEditor,AreaEditorJournalAssignment,AreaEditorRecommendation
from journal.models import SubjectArea, JournalSection
from django.contrib.auth import authenticate
from rest_framework.exceptions import AuthenticationFailed
from django.conf import settings

class AreaEditorRegistrationSerializer(serializers.ModelSerializer):
    first_name = serializers.CharField(write_only=True)
    last_name = serializers.CharField(write_only=True)
    email = serializers.EmailField(write_only=True)
    password = serializers.CharField(write_only=True, min_length=8)
    cv = serializers.FileField(required=True)

    subject_areas = serializers.PrimaryKeyRelatedField(
        many=True, queryset=SubjectArea.objects.all(), required=False
    )
    journal_sections = serializers.PrimaryKeyRelatedField(
        many=True, queryset=JournalSection.objects.all(), required=False
    )

    class Meta:
        model = AreaEditor
        fields = [
            'first_name', 'last_name', 'email', 'password',
            'institution', 'position_title', 'country', 'cv',
            'subject_areas', 'journal_sections'
        ]

    '''def validate_email(self, value):
        if User.objects.filter(email=value).exists():
            raise serializers.ValidationError("Email already exists.")
        return value'''

    def create(self, validated_data):
        subject_areas = validated_data.pop('subject_areas', [])
        journal_sections = validated_data.pop('journal_sections', [])
        first_name = validated_data.pop('first_name')
        last_name = validated_data.pop('last_name')
        email = validated_data.pop('email')
        password = validated_data.pop('password')

        user = User.objects.create_user(
            username=first_name,
            email=email,
            first_name=first_name,
            last_name=last_name,
            password=password
        )

        area_editor = AreaEditor.objects.create(user=user, **validated_data)
        area_editor.subject_areas.set(subject_areas)
        area_editor.journal_sections.set(journal_sections)

        return area_editor
    
class LoginSerializer(serializers.Serializer):
    email = serializers.EmailField()
    password = serializers.CharField(write_only=True)

    def validate(self, data):
        email = data.get('email')
        password = data.get('password')

        try:
            user = User.objects.get(email=email)
        except User.DoesNotExist:
            raise AuthenticationFailed("Invalid email or password.")

        if not user.check_password(password):
            raise AuthenticationFailed("Invalid email or password.")

        if not user.is_active:
            raise AuthenticationFailed("User account is disabled.")

        data['user'] = user
        return data

class AreaEditorUpdateSerializer(serializers.ModelSerializer):
    subject_areas = serializers.PrimaryKeyRelatedField(
        many=True, queryset=SubjectArea.objects.all(), required=False
    )
    journal_sections = serializers.PrimaryKeyRelatedField(
        many=True, queryset=JournalSection.objects.all(), required=False
    )

    class Meta:
        model = AreaEditor
        exclude = ['user', 'date_joined', 'number_of_assignments_handled']

class AreaEditorListSerializer(serializers.ModelSerializer):
    full_name = serializers.SerializerMethodField()
    email = serializers.EmailField(source='user.email')
    user_id = serializers.IntegerField(source='user.id', read_only=True)  # ✅ Add this line
    class Meta:
        model = AreaEditor
        fields = [
            'id', 'full_name', 'email','user_id',
            'institution', 'department', 'position_title', 'country',
            'language_proficiency', 'editor_bio', 'cv',
            'linkedin_profile', 'google_scholar_profile',
            'subject_areas', 'is_approved', 'profile_picture'
        ]

    def get_full_name(self, obj):
        return obj.user.get_full_name()

'''class AreaEditorDetailSerializer(serializers.ModelSerializer):
    full_name = serializers.SerializerMethodField()
    email = serializers.EmailField(source='user.email')

    class Meta:
        model = AreaEditor
        fields = [
            'id', 'full_name', 'email',
            'institution', 'department', 'position_title', 'country',
            'language_proficiency', 'editor_bio', 'cv',
            'linkedin_profile', 'google_scholar_profile',
            'subject_areas', 'is_approved', 'profile_picture',
            'phone_number', 'orcid_id', 'research_interests', 'scopus_id',
            'web_of_science_id', 'date_joined', 'number_of_assignments_handled'
        ]

    def get_full_name(self, obj):
        return obj.user.get_full_name()'''

class AreaEditorDetailSerializer(serializers.ModelSerializer):
    full_name = serializers.SerializerMethodField()
    email = serializers.EmailField(source='user.email')
    cv = serializers.SerializerMethodField()
    profile_picture = serializers.SerializerMethodField()  # <-- override here
    user_id = serializers.IntegerField(source='user.id', read_only=True)  # ✅ Add this line
    subject_area_names = serializers.SerializerMethodField()  # <-- Separate key here

    class Meta:
        model = AreaEditor
        fields = [
            'id', 'full_name', 'email','user_id',
            'institution', 'department', 'position_title', 'country',
            'language_proficiency', 'editor_bio', 'cv',
            'linkedin_profile', 'google_scholar_profile',
            'subject_areas', 'subject_area_names','is_approved', 'profile_picture',
            'phone_number', 'orcid_id', 'research_interests', 'scopus_id',
            'web_of_science_id', 'date_joined', 'number_of_assignments_handled'
        ]

    def get_full_name(self, obj):
        return obj.user.get_full_name()
    
    def get_cv(self, obj):
        if obj.cv:
            return obj.cv.url.replace(settings.MEDIA_URL, 'media/')
        return None

    def get_profile_picture(self, obj):
        if obj.profile_picture:
            return obj.profile_picture.url.replace(settings.MEDIA_URL, 'media/')
        return None

    def get_subject_area_names(self, obj):
        return [sa.name for sa in obj.subject_areas.all()]
    
class AreaEditorApprovalSerializer(serializers.ModelSerializer):
    class Meta:
        model = AreaEditor
        fields = ['is_approved']

    def update(self, instance, validated_data):
        instance.is_approved = validated_data.get('is_approved', instance.is_approved)
        instance.save()
        return instance

class AreaEditorJournalAssignmentSerializer(serializers.ModelSerializer):
    journal_title = serializers.CharField(source='journal.title', read_only=True)

    class Meta:
        model = AreaEditorJournalAssignment
        fields = [
            'id', 'journal', 'journal_title', 'area_editor',
            'status', 'assigned_date', 'completed_date', 'notes'
        ]
        read_only_fields = ['id', 'status', 'assigned_date', 'completed_date', 'journal_title']

# serializers.py

# serializers.py

class AreaEditorRecommendationSerializer(serializers.ModelSerializer):
    journal_title = serializers.CharField(source='journal.title', read_only=True)
    area_editor_name = serializers.CharField(source='area_editor.user.get_full_name', read_only=True)

    class Meta:
        model = AreaEditorRecommendation
        fields = [
            'id', 'journal', 'journal_title',
            'area_editor', 'area_editor_name',
            'recommendation', 'summary', 'overall_rating',
            'justification', 'public_comments_to_author',
            'submitted_at'
        ]
        read_only_fields = [
            'id', 'journal', 'journal_title',
            'area_editor', 'area_editor_name', 'submitted_at'
        ]

from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
from rest_framework import serializers
from django.contrib.auth import get_user_model
from .models import AreaEditor

User = get_user_model()

class AreaEditorTokenObtainPairSerializer(TokenObtainPairSerializer):
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
                    AreaEditor.objects.get(user=user, is_approved=True)
                    valid_user = user
                    break
                except AreaEditor.DoesNotExist:
                    continue
        
        if not valid_user:
            raise serializers.ValidationError({'error': 'No active area editor account found or account not approved'})

        # Generate tokens
        refresh = self.get_token(valid_user)
        
        # Add custom claims
        refresh['email'] = valid_user.email
        refresh['first_name'] = valid_user.first_name
        refresh['last_name'] = valid_user.last_name
        refresh['area_editor_id'] = valid_user.areaeditor.id

        # Get subject areas
        subject_areas = valid_user.areaeditor.subject_areas.all()
        subject_area_list = [{'id': sa.id, 'name': sa.name} for sa in subject_areas]

        return {
            'area_editor_id': valid_user.areaeditor.id,
            'username': valid_user.username,
            'email': valid_user.email,
            'first_name': valid_user.first_name,
            'last_name': valid_user.last_name,
            'is_approved': valid_user.areaeditor.is_approved,
            'subject_areas': subject_area_list,
            'token': str(refresh.access_token)
        }