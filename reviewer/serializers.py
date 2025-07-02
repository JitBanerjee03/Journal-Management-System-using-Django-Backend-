from rest_framework import serializers
from django.contrib.auth.models import User
from .models import Reviewer
from journal.models import SubjectArea
from rest_framework import serializers
from django.contrib.auth.models import User
from django.contrib.auth import authenticate
from rest_framework.exceptions import AuthenticationFailed
from rest_framework import serializers
from .models import Reviewer, EducationDetailOfReviewer
from journal.models import SubjectArea
from rest_framework import serializers
from .models import ReviewFeedback
from .models import ReviewerAssignmentHistory
from journal.models import Journal
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer

class ReviewerRegistrationSerializer(serializers.ModelSerializer): #serializer for registration of the reviewer
    first_name = serializers.CharField(write_only=True)
    last_name = serializers.CharField(write_only=True)
    email = serializers.EmailField(write_only=True)
    password = serializers.CharField(write_only=True, min_length=8)
    resume = serializers.FileField(required=True)

    subject_areas = serializers.PrimaryKeyRelatedField(
        many=True, queryset=SubjectArea.objects.all(), required=False
    )

    class Meta:
        model = Reviewer
        fields = [
            'first_name', 'last_name', 'email', 'password',
            'phone_number', 'profile_picture', 'institution', 
            'department', 'position_title', 'resume', 'orcid_id', 
            'research_interests', 'google_scholar_profile', 
            'personal_website', 'languages_spoken', 'subject_areas'
        ]

    '''def validate_email(self, value):
        if User.objects.filter(email=value).exists():
            raise serializers.ValidationError("Email already exists.")
        return value'''

    def create(self, validated_data):
        subject_areas = validated_data.pop('subject_areas', [])
        first_name = validated_data.pop('first_name')
        last_name = validated_data.pop('last_name')
        email = validated_data.pop('email')
        password = validated_data.pop('password')

        # Create the User object
        user = User.objects.create_user(
            username=first_name,
            email=email,
            first_name=first_name,
            last_name=last_name,
            password=password
        )

        # Create Reviewer object
        reviewer = Reviewer.objects.create(user=user, **validated_data)
        reviewer.subject_areas.set(subject_areas)

        return reviewer

class LoginSerializer(serializers.Serializer): #serializer for login of the reviewer
    email = serializers.EmailField()
    password = serializers.CharField(write_only=True)

    def validate(self, attrs):
        email = attrs.get('email')
        password = attrs.get('password')

        # Validate email and password
        user = authenticate(request=self.context.get('request'), username=email, password=password)

        if user is None:
            raise AuthenticationFailed('Invalid email or password.')

        attrs['user'] = user  # Add the user to the validated data to use later (e.g., generate token)
        return attrs

#serializer for getting the reviewer list
class EducationDetailOfReviewerSerializer(serializers.ModelSerializer):
    class Meta:
        model = EducationDetailOfReviewer
        exclude = ['reviewer']

class SubjectAreaSerializer(serializers.ModelSerializer):
    class Meta:
        model = SubjectArea
        fields = ['id', 'name']

class FullReviewerDetailSerializer(serializers.ModelSerializer):
    full_name = serializers.SerializerMethodField()
    email = serializers.EmailField(source='user.email')
    profile_picture = serializers.ImageField()
    resume = serializers.FileField()
    subject_areas = SubjectAreaSerializer(many=True)
    educations = EducationDetailOfReviewerSerializer(many=True)
    user_id = serializers.IntegerField(source='user.id', read_only=True)  # ✅ Added this line

    class Meta:
        model = Reviewer
        fields = [
            'id',
            'user_id',
            'full_name',
            'email',
            'phone_number',
            'profile_picture',
            'institution',
            'department',
            'position_title',
            'resume',
            'orcid_id',
            'research_interests',
            'google_scholar_profile',
            'personal_website',
            'languages_spoken',
            'subject_areas',
            'educations',
            'is_approved',
            'is_active',
            'date_joined',
        ]

    def get_full_name(self, obj):
        return f"{obj.user.first_name} {obj.user.last_name}"

# serializer for updating a particular reviewer details
'''class EducationDetailSerializer(serializers.ModelSerializer):
    class Meta:
        model = EducationDetailOfReviewer
        exclude = ['reviewer']

class ReviewerUpdateSerializer(serializers.ModelSerializer):
    subject_areas = serializers.PrimaryKeyRelatedField(
        many=True, 
        queryset=SubjectArea.objects.all(), 
        required=False
    )
    educations = EducationDetailSerializer(many=True, required=False)

    class Meta:
        model = Reviewer
        exclude = ['user', 'is_approved', 'date_joined']

    def update(self, instance, validated_data):
        # Handle subject_areas separately
        subject_areas_data = validated_data.pop('subject_areas', None)
        
        # Handle educations data
        educations_data = validated_data.pop('educations', None)

        # Update regular fields
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.save()

        # Update many-to-many relationship properly
        if subject_areas_data is not None:
            instance.subject_areas.set(subject_areas_data)

        # Handle educations
        if educations_data is not None:
            instance.educations.all().delete()
            for edu_data in educations_data:
                EducationDetailOfReviewer.objects.create(reviewer=instance, **edu_data)

        return instance'''

class EducationSerializer(serializers.ModelSerializer):
    class Meta:
        model = EducationDetailOfReviewer
        fields = ['degree', 'field_of_study', 'institution', 'start_year', 'end_year', 'grade_or_score']

'''class ReviewerUpdateSerializer(serializers.ModelSerializer):
    educations = EducationSerializer(many=True, required=False)
    
    class Meta:
        model = Reviewer
        fields = ['phone_number', 'institution', 'department', 'position_title', 
                 'orcid_id', 'research_interests', 'google_scholar_profile',
                 'personal_website', 'languages_spoken', 'subject_areas', 'educations',
                 'profile_picture', 'resume']

    def update(self, instance, validated_data):
        educations_data = validated_data.pop('educations', None)
        
        # Update basic fields
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        
        instance.save()
        
        # Handle educations
        if educations_data is not None:
            # Clear existing educations
            instance.educations.all().delete()
            
            # Create new educations
            for education_data in educations_data:
                EducationDetailOfReviewer.objects.create(reviewer=instance, **education_data)
        
        return instance'''

class ReviewerUpdateSerializer(serializers.ModelSerializer):
    educations = EducationSerializer(many=True, required=False)
    
    class Meta:
        model = Reviewer
        fields = ['phone_number', 'institution', 'department', 'position_title', 
                 'orcid_id', 'research_interests', 'google_scholar_profile',
                 'personal_website', 'languages_spoken', 'subject_areas', 'educations',
                 'profile_picture', 'resume']

    def update(self, instance, validated_data):
        educations_data = validated_data.pop('educations', None)
        subject_areas_data = validated_data.pop('subject_areas', None)
        
        # Update basic fields
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        
        # Handle subject_areas (many-to-many relationship)
        if subject_areas_data is not None:
            instance.subject_areas.set(subject_areas_data)
        
        instance.save()
        
        # Handle educations
        if educations_data is not None:
            # Clear existing educations
            instance.educations.all().delete()
            
            # Create new educations
            for education_data in educations_data:
                EducationDetailOfReviewer.objects.create(reviewer=instance, **education_data)
        
        return instance

class ReviewerSerializer(serializers.ModelSerializer): #serializer for getting the approved reviewer list
    full_name = serializers.SerializerMethodField()
    email = serializers.SerializerMethodField()

    class Meta:
        model = Reviewer
        fields = ['id', 'full_name', 'institution', 'department', 'position_title', 'email']

    def get_full_name(self, obj):
        return f"{obj.user.first_name} {obj.user.last_name}"

    def get_email(self, obj):
        return obj.user.email
    
class ReviewFeedbackSerializer(serializers.ModelSerializer): #serializer for review feedback from the reviewer for a particular journal
    class Meta:
        model = ReviewFeedback
        fields = '__all__'
        read_only_fields = ['review_date', 'updated_at']

class MinimalJournalSerializer(serializers.ModelSerializer): #serializer for getting the journal details in the reviewer assignment history
    author_name = serializers.SerializerMethodField()

    class Meta:
        model = Journal
        fields = ['id', 'title', 'author_name']

    def get_author_name(self, obj):
        try:
            return f"{obj.corresponding_author.user.first_name} {obj.corresponding_author.user.last_name}"
        except AttributeError:
            return None

'''class ReviewerAssignmentHistorySerializer(serializers.ModelSerializer):
    reviewer_name = serializers.SerializerMethodField()
    reviewer_email = serializers.SerializerMethodField()
    reviewer_phone = serializers.CharField(source='reviewer.phone_number')
    subject_area_name = serializers.SerializerMethodField()
    
    class Meta:
        model = ReviewerAssignmentHistory
        fields = [
            'id',
            'journal_id',
            'reviewer_id',
            'subject_area_id',
            'subject_area_name',  # New field
            'assigned_date',
            'completed_date',
            'status',
            'rejection_reason',
            'reviewer_name',
            'reviewer_email',
            'reviewer_phone'
        ]
    
    def get_reviewer_name(self, obj):
        return f"{obj.reviewer.user.first_name} {obj.reviewer.user.last_name}"
    
    def get_reviewer_email(self, obj):
        return obj.reviewer.user.email
    
    def get_subject_area_name(self, obj):
        return obj.subject_area.name if obj.subject_area else None'''

from rest_framework import serializers
from .models import ReviewerAssignmentHistory

class ReviewerAssignmentHistorySerializer(serializers.ModelSerializer):
    reviewer_name = serializers.SerializerMethodField()
    reviewer_email = serializers.SerializerMethodField()
    reviewer_phone = serializers.CharField(source='reviewer.phone_number')
    reviewer_approval_status = serializers.BooleanField(source='reviewer.is_approved', read_only=True)
    subject_area_name = serializers.SerializerMethodField()

    class Meta:
        model = ReviewerAssignmentHistory
        fields = [
            'id',
            'journal_id',
            'reviewer_id',
            'subject_area_id',
            'subject_area_name',
            'assigned_date',
            'completed_date',
            'status',
            'rejection_reason',
            'reviewer_name',
            'reviewer_email',
            'reviewer_phone',
            'reviewer_approval_status'  # <-- Added field
        ]
    
    def get_reviewer_name(self, obj):
        return f"{obj.reviewer.user.first_name} {obj.reviewer.user.last_name}"
    
    def get_reviewer_email(self, obj):
        return obj.reviewer.user.email
    
    def get_subject_area_name(self, obj):
        return obj.subject_area.name if obj.subject_area else None

class ReviewerJournalAssignmentSerializer(serializers.ModelSerializer):
    id = serializers.IntegerField()
    journal_id = serializers.IntegerField(source='journal.id')
    title = serializers.CharField(source='journal.title')
    author = serializers.SerializerMethodField()
    assigned_date = serializers.SerializerMethodField()
    submission_date = serializers.SerializerMethodField()
    status = serializers.CharField()

    class Meta:
        model = ReviewerAssignmentHistory
        fields = [
            'id',
            'journal_id',
            'title',
            'author',
            'status',
            'assigned_date',
            'submission_date'
        ]

    def get_author(self, obj):
        try:
            return f"{obj.journal.corresponding_author.user.first_name} {obj.journal.corresponding_author.user.last_name}"
        except AttributeError:
            return None

    def get_assigned_date(self, obj):
        return obj.assigned_date.date() if obj.assigned_date else None

    def get_submission_date(self, obj):
        return obj.completed_date.date() if obj.completed_date else None

class ReviewerTokenObtainPairSerializer(TokenObtainPairSerializer):
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
                    Reviewer.objects.get(user=user)
                    valid_user = user
                    break
                except Reviewer.DoesNotExist:
                    continue
        
        if not valid_user:
            raise serializers.ValidationError({'error': 'No active reviewer account found'})

        # Generate tokens
        refresh = self.get_token(valid_user)
        
        # Add custom claims
        refresh['email'] = valid_user.email
        refresh['first_name'] = valid_user.first_name
        refresh['last_name'] = valid_user.last_name
        refresh['reviewer_id'] = valid_user.reviewer.id
        refresh['is_approved'] = valid_user.reviewer.is_approved

        return {
            'reviewer_id': valid_user.reviewer.id,
            'username': valid_user.username,
            'email': valid_user.email,
            'first_name': valid_user.first_name,
            'last_name': valid_user.last_name,
            'is_approved': valid_user.reviewer.is_approved,
            'token': str(refresh.access_token)
        }