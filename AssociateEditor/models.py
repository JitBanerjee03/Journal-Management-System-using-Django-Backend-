from django.db import models
from django.contrib.auth.models import User
from journal.models import SubjectArea,Journal,JournalSection

class AssociateEditor(models.Model): 
    user = models.OneToOneField(User, on_delete=models.CASCADE)

    phone_number = models.CharField(max_length=20, blank=True, null=True)
    profile_picture = models.ImageField(upload_to='ae_profile_pictures/', blank=True, null=True)
    cv = models.FileField(upload_to='ae_cvs/', blank=True, null=True, help_text="Upload the CV/resume of the Associate Editor.")

    institution = models.CharField(max_length=255)
    department = models.CharField(max_length=255, blank=True, null=True)
    position_title = models.CharField(max_length=255, blank=True, null=True)

    subject_areas = models.ManyToManyField(SubjectArea, blank=True)
    journal_sections = models.ManyToManyField(JournalSection, blank=True)  # ✅ New field
    orcid_id = models.CharField(max_length=50, blank=True, null=True)
    research_interests = models.TextField(blank=True, null=True)

    # Additional fields previously discussed
    editor_bio = models.TextField(blank=True, null=True)
    linkedin_profile = models.URLField(blank=True, null=True)
    google_scholar_profile = models.URLField(blank=True, null=True)
    scopus_id = models.CharField(max_length=100, blank=True, null=True)
    web_of_science_id = models.CharField(max_length=100, blank=True, null=True)
    country = models.CharField(max_length=100, blank=True, null=True)
    language_proficiency = models.CharField(max_length=255, blank=True, null=True)

    number_of_reviews_completed = models.PositiveIntegerField(default=0)
    number_of_assignments_handled = models.PositiveIntegerField(default=0)

    is_active = models.BooleanField(default=True)
    date_joined = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.user.get_full_name()} ({self.user.email})"

class AssociateEditorAssignment(models.Model):
    STATUS_CHOICES = [
        ('assigned', 'Assigned'),
        ('reviewing', 'Reviewing'),
        ('completed', 'Completed'),
    ]

    journal = models.ForeignKey(Journal, on_delete=models.CASCADE)
    associate_editor = models.ForeignKey(AssociateEditor, on_delete=models.CASCADE)
    assigned_date = models.DateTimeField(auto_now_add=True)
    completed_date = models.DateTimeField(null=True, blank=True)
    status = models.CharField(max_length=50, choices=STATUS_CHOICES, default='assigned')

    def __str__(self):
        return f"{self.associate_editor.user.get_full_name()} → {self.journal.title}"

from django.core.validators import MinValueValidator, MaxValueValidator

class AssociateEditorRecommendation(models.Model):
    journal = models.ForeignKey(Journal, on_delete=models.CASCADE)
    associate_editor = models.ForeignKey(AssociateEditor, on_delete=models.CASCADE)

    recommendation = models.CharField(
        max_length=50,
        choices=[
            ('accept', 'Accept'),
            ('minor_revision', 'Minor Revision'),
            ('major_revision', 'Major Revision'),
            ('reject', 'Reject')
        ]
    )
    
    summary = models.TextField(null=True, blank=True)  # example

    overall_rating = models.IntegerField(default=3)

    justification = models.TextField(help_text="Detailed reasoning behind the recommendation.")
    public_comments_to_author = models.TextField(blank=True, null=True)
    submitted_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Recommendation for {self.journal.title} by AE {self.associate_editor.user.get_full_name()}"

