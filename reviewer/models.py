from django.db import models
from django.contrib.auth.models import User
from journal.models import SubjectArea,Journal  # Assuming you already have this model
# Create your models here.

class Reviewer(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)

    # Contact Information
    phone_number = models.CharField(max_length=20, blank=True, null=True)
    profile_picture = models.ImageField(upload_to='reviewer_profile_pictures/', blank=True, null=True)

    # Affiliation
    institution = models.CharField(max_length=255)
    department = models.CharField(max_length=255, blank=True, null=True)
    position_title = models.CharField(max_length=255, blank=True, null=True)

    # Resume
    resume = models.FileField(upload_to='reviewer_resumes/', blank=True, null=True)

    # Academic Info
    orcid_id = models.CharField(max_length=50, blank=True, null=True)
    research_interests = models.TextField(blank=True, null=True)
    google_scholar_profile = models.URLField(blank=True, null=True)
    personal_website = models.URLField(blank=True, null=True)

    # Language and Expertise
    languages_spoken = models.CharField(max_length=255, blank=True, null=True)
    subject_areas = models.ManyToManyField(SubjectArea, blank=True)

    # System Info
    is_approved = models.BooleanField(default=False)
    is_active = models.BooleanField(default=True)
    date_joined = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.user.first_name} {self.user.last_name} ({self.user.email})"

class EducationDetailOfReviewer(models.Model):
    reviewer = models.ForeignKey(Reviewer, on_delete=models.CASCADE, related_name='educations')
    
    degree = models.CharField(max_length=100)
    field_of_study = models.CharField(max_length=100)
    institution = models.CharField(max_length=255)
    start_year = models.PositiveIntegerField(null=True)
    end_year = models.PositiveIntegerField(null=True)
    grade_or_score = models.CharField(max_length=50, blank=True, null=True)
    certificate = models.FileField(upload_to='reviewer_certificates/', blank=True, null=True)

    def __str__(self):
        return f"{self.degree} in {self.field_of_study} from {self.institution}"

class ReviewerAssignmentHistory(models.Model):
    STATUS_CHOICES = [
        ('assigned', 'Assigned'),
        ('completed', 'Completed'),
        ('rejected', 'Rejected'),
    ]

    journal = models.ForeignKey(Journal, on_delete=models.CASCADE)
    reviewer = models.ForeignKey(Reviewer, on_delete=models.CASCADE)
    subject_area = models.ForeignKey(SubjectArea, on_delete=models.SET_NULL, null=True, blank=True)
    assigned_date = models.DateTimeField(auto_now_add=True)
    completed_date = models.DateTimeField(null=True, blank=True)
    status = models.CharField(max_length=50, choices=STATUS_CHOICES, default='assigned')
    rejection_reason = models.TextField(null=True, blank=True)

    def __str__(self):
        return f"Reviewer {self.reviewer.user.first_name} {self.reviewer.user.last_name} assigned to '{self.journal.title}'"

class ReviewFeedback(models.Model):
    journal = models.ForeignKey(Journal, on_delete=models.CASCADE)
    reviewer = models.ForeignKey(Reviewer, on_delete=models.CASCADE)

    feedback_text = models.TextField()
    rating = models.PositiveIntegerField(choices=[
        (1, 'Poor'), (2, 'Fair'), (3, 'Good'), (4, 'Very Good'), (5, 'Excellent')
    ], default=3)

    confidential_comments = models.TextField(
        blank=True, null=True,
        help_text="Comments to the editor that won't be shown to the author."
    )

    recommendation = models.CharField(
        max_length=50,
        choices=[
            ('accept', 'Accept'),
            ('minor_revision', 'Minor Revision'),
            ('major_revision', 'Major Revision'),
            ('reject', 'Reject')
        ],
        help_text="Overall recommendation regarding the manuscript."
    )

    review_date = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    file_upload = models.FileField(
        upload_to='review_feedback_files/', blank=True, null=True,
        help_text="Optional file (e.g., annotated manuscript or comments)."
    )

    is_final_submission = models.BooleanField(default=True)

    def __str__(self):
        return f"Feedback for '{self.journal.title}' by {self.reviewer.user.first_name} {self.reviewer.user.last_name}"
