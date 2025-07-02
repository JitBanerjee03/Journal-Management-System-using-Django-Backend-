from rest_framework import serializers
from django.contrib.auth.models import User
from django.core.mail import send_mail
from django.utils.html import strip_tags
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
from .models import (
    AssociateEditor,
    AssociateEditorAssignment,
    AssociateEditorRecommendation
)

from journal.models import SubjectArea, Journal, JournalSection
from rest_framework import serializers
from .models import AssociateEditorRecommendation
# ------------------------------
# Supporting Serializers
# ------------------------------

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'username', 'email', 'first_name', 'last_name']

class SubjectAreaSerializer(serializers.ModelSerializer):
    class Meta:
        model = SubjectArea
        fields = ['id', 'name']

class JournalSectionSerializer(serializers.ModelSerializer):
    class Meta:
        model = JournalSection
        fields = ['id', 'name']

class JournalSerializer(serializers.ModelSerializer):
    class Meta:
        model = Journal
        fields = ['id', 'title']


# ------------------------------
# Associate Editor Serializers
# ------------------------------

class AssociateEditorSerializer(serializers.ModelSerializer):
    subject_areas = SubjectAreaSerializer(many=True, read_only=True)
    journal_sections = JournalSectionSerializer(many=True, read_only=True)
    user_full_name = serializers.CharField(source='user.get_full_name', read_only=True)
    user_email = serializers.EmailField(source='user.email', read_only=True)

    class Meta:
        model = AssociateEditor
        fields = '__all__'
        extra_fields = ['user_full_name', 'user_email']  # Not required, but clarifies intention

class AssociateEditorAssignmentSerializer(serializers.ModelSerializer):
    journal = JournalSerializer()
    associate_editor = AssociateEditorSerializer()

    class Meta:
        model = AssociateEditorAssignment
        fields = [
            'id', 'journal', 'associate_editor',
            'assigned_date', 'completed_date', 'status'
        ]

class AssociateEditorRecommendationSerializer(serializers.ModelSerializer):
    class Meta:
        model = AssociateEditorRecommendation
        fields = [
            'id',
            'journal',
            'associate_editor',
            'recommendation',
            'summary',
            'overall_rating',
            'justification',
            'public_comments_to_author',
            'submitted_at'
        ]

class AssociateEditorRegistrationSerializer(serializers.ModelSerializer):
    first_name = serializers.CharField(write_only=True)
    last_name = serializers.CharField(write_only=True)
    email = serializers.EmailField(write_only=True)
    password = serializers.CharField(write_only=True)
    subject_areas = serializers.PrimaryKeyRelatedField(
        queryset=SubjectArea.objects.all(), many=True
    )
    journal_sections = serializers.PrimaryKeyRelatedField(  # ✅ New
        queryset=JournalSection.objects.all(), many=True
    )

    class Meta:
        model = AssociateEditor
        fields = [
            'first_name', 'last_name', 'email', 'password',
            'cv', 'institution', 'subject_areas', 'journal_sections'
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
        subject_areas = validated_data.pop('subject_areas')
        journal_sections = validated_data.pop('journal_sections')

        user = User.objects.create_user(
            username=first_name,
            first_name=first_name,
            last_name=last_name,
            email=email,
            password=password
        )

        ae = AssociateEditor.objects.create(user=user, **validated_data)
        ae.subject_areas.set(subject_areas)
        ae.journal_sections.set(journal_sections)
        return ae

class AssociateEditorBriefSerializer(serializers.ModelSerializer):
    user_email = serializers.EmailField(source='user.email', read_only=True)
    user_full_name = serializers.CharField(source='user.get_full_name', read_only=True)
    user_id = serializers.IntegerField(source='user.id', read_only=True)  # ✅ Added this line

    class Meta:
        model = AssociateEditor
        fields = [
            'id',
            'user_id',
            'user_full_name',
            'user_email',
            'institution',
            'department',
            'position_title',
            'country',
            'is_active',
            'number_of_reviews_completed',
            'number_of_assignments_handled',
            'profile_picture'
        ]

class AssociateEditorUpdateSerializer(serializers.ModelSerializer):
    subject_areas = serializers.PrimaryKeyRelatedField(
        queryset=SubjectArea.objects.all(), many=True, required=False
    )
    journal_sections = serializers.PrimaryKeyRelatedField(
        queryset=JournalSection.objects.all(), many=True, required=False
    )

    class Meta:
        model = AssociateEditor
        fields = '__all__'

from rest_framework import serializers
from .models import AssociateEditorAssignment  # adjust import path as needed

class AssignedJournalSerializer(serializers.ModelSerializer):
    journal_id = serializers.IntegerField(source='journal.id')
    title = serializers.CharField(source='journal.title')
    author_name = serializers.SerializerMethodField()
    author_email = serializers.SerializerMethodField()
    assigned_date = serializers.DateTimeField()
    status = serializers.CharField()
    subject_area = serializers.CharField(source='journal.subject_area.name')
    journal_section = serializers.CharField(source='journal.journal_section.name')

    class Meta:
        model = AssociateEditorAssignment
        fields = [
            'journal_id',
            'title',
            'author_name',
            'author_email',
            'subject_area',
            'journal_section',
            'assigned_date',
            'status',
        ]

    def get_author_name(self, obj):
        author = obj.journal.corresponding_author.user
        return f"{author.first_name} {author.last_name}"

    def get_author_email(self, obj):
        return obj.journal.corresponding_author.user.email

# serializers.py

class AssociateEditorAssignmentStatusUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = AssociateEditorAssignment
        fields = ['status']

    def validate_status(self, value):
        if value not in dict(AssociateEditorAssignment.STATUS_CHOICES):
            raise serializers.ValidationError("Invalid status.")
        return value

# serializers.py
from rest_framework import serializers
from .models import AssociateEditorAssignment

class AssociateEditorAssignmentListSerializer(serializers.ModelSerializer):
    journal_id = serializers.IntegerField(source='journal.id')
    journal_topic = serializers.CharField(source='journal.title')
    associate_editor_id = serializers.IntegerField(source='associate_editor.id')
    name = serializers.CharField(source='associate_editor.user.get_full_name')
    contact = serializers.EmailField(source='associate_editor.user.email')
    phone_number = serializers.CharField(source='associate_editor.phone_number')  # ✅ added phone number
    subject_area = serializers.CharField(source='journal.subject_area.name')
    assigned_date = serializers.DateTimeField()
    completed_date = serializers.DateTimeField()
    status = serializers.CharField()

    class Meta:
        model = AssociateEditorAssignment
        fields = [
            'journal_id',
            'journal_topic',
            'associate_editor_id',
            'name',
            'contact',
            'phone_number',  # ✅ include in output
            'subject_area',
            'assigned_date',
            'completed_date',
            'status',
        ]

class AssociateEditorTokenObtainPairSerializer(TokenObtainPairSerializer):
    username_field = 'email'

    def validate(self, attrs):
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
                    AssociateEditor.objects.get(user=user)
                    valid_user = user
                    break
                except AssociateEditor.DoesNotExist:
                    continue
        
        if not valid_user:
            raise serializers.ValidationError({'error': 'No active associate editor account found'})

        # Generate tokens
        refresh = self.get_token(valid_user)
        
        # Add custom claims
        refresh['email'] = valid_user.email
        refresh['first_name'] = valid_user.first_name
        refresh['last_name'] = valid_user.last_name
        refresh['associate_editor_id'] = valid_user.associateeditor.id
        refresh['is_active'] = valid_user.associateeditor.is_active

        return {
            'associate_editor_id': valid_user.associateeditor.id,
            'username': valid_user.username,
            'email': valid_user.email,
            'first_name': valid_user.first_name,
            'last_name': valid_user.last_name,
            'is_active': valid_user.associateeditor.is_active,
            'token': str(refresh.access_token)
        }