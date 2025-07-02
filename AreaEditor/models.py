from django.db import models
from django.contrib.auth.models import User
from journal.models import SubjectArea, JournalSection,Journal

class AreaEditor(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)

    # Contact and Profile
    phone_number = models.CharField(max_length=20, blank=True, null=True)
    profile_picture = models.ImageField(upload_to='area_editor_profiles/', blank=True, null=True)
    cv = models.FileField(upload_to='area_editor_cvs/', blank=True, null=True)

    # Academic & Institutional Info
    institution = models.CharField(max_length=255)
    department = models.CharField(max_length=255, blank=True, null=True)
    position_title = models.CharField(max_length=255, blank=True, null=True)

    # Expertise
    subject_areas = models.ManyToManyField(SubjectArea, blank=True)
    journal_sections = models.ManyToManyField(JournalSection, blank=True)

    orcid_id = models.CharField(max_length=50, blank=True, null=True)
    research_interests = models.TextField(blank=True, null=True)

    # Additional Metadata
    editor_bio = models.TextField(blank=True, null=True)
    linkedin_profile = models.URLField(blank=True, null=True)
    google_scholar_profile = models.URLField(blank=True, null=True)
    scopus_id = models.CharField(max_length=100, blank=True, null=True)
    web_of_science_id = models.CharField(max_length=100, blank=True, null=True)

    country = models.CharField(max_length=100, blank=True, null=True)
    language_proficiency = models.CharField(max_length=255, blank=True, null=True)

    # Status & System Flags
    number_of_assignments_handled = models.PositiveIntegerField(default=0)
    is_active = models.BooleanField(default=True)
    is_approved = models.BooleanField(default=False)  # ✅ New field added
    date_joined = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.user.get_full_name()} ({self.user.email})"

class EducationDetailOfAreaEditor(models.Model):
    area_editor = models.ForeignKey('AreaEditor', on_delete=models.CASCADE, related_name='educations')
    
    degree = models.CharField(max_length=100)
    field_of_study = models.CharField(max_length=100)
    institution = models.CharField(max_length=255)
    start_year = models.PositiveIntegerField(null=True)
    end_year = models.PositiveIntegerField(null=True)
    grade_or_score = models.CharField(max_length=50, blank=True, null=True)
    certificate = models.FileField(upload_to='area_editor_certificates/', blank=True, null=True)

    def __str__(self):
        return f"{self.degree} in {self.field_of_study} from {self.institution}"
    
class AreaEditorJournalAssignment(models.Model):
    STATUS_CHOICES = [
        ('assigned', 'Assigned'),
        ('in_progress', 'In Progress'),
        ('completed', 'Completed'),
    ]

    journal = models.ForeignKey(Journal, on_delete=models.CASCADE)
    area_editor = models.ForeignKey(AreaEditor, on_delete=models.CASCADE)
    assigned_date = models.DateTimeField(auto_now_add=True)
    completed_date = models.DateTimeField(null=True, blank=True)
    status = models.CharField(max_length=50, choices=STATUS_CHOICES, default='assigned')
    notes = models.TextField(blank=True, null=True)

    def __str__(self):
        return f"{self.area_editor.user.get_full_name()} → {self.journal.title}"

# models.py

class AreaEditorRecommendation(models.Model):
    RECOMMENDATION_CHOICES = [
        ('accept', 'Accept'),
        ('minor_revision', 'Minor Revision'),
        ('major_revision', 'Major Revision'),
        ('reject', 'Reject'),
    ]

    journal = models.ForeignKey(Journal, on_delete=models.CASCADE)
    area_editor = models.ForeignKey(AreaEditor, on_delete=models.CASCADE)

    recommendation = models.CharField(max_length=20, choices=RECOMMENDATION_CHOICES)
    summary = models.TextField()
    overall_rating = models.PositiveSmallIntegerField()
    justification = models.TextField()
    public_comments_to_author = models.TextField(blank=True, null=True)
    submitted_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('journal', 'area_editor')

    def __str__(self):
        return f"Recommendation by {self.area_editor.user.get_full_name()} for {self.journal.title}"
