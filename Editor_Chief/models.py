from django.db import models
from django.contrib.auth.models import User

class EditorInChief(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)

    phone_number = models.CharField(max_length=20, blank=True, null=True)
    profile_picture = models.ImageField(upload_to='eic_profile_pictures/', blank=True, null=True)
    cv = models.FileField(upload_to='eic_cvs/', blank=True, null=True)

    institution = models.CharField(max_length=255)
    position_title = models.CharField(max_length=255, blank=True, null=True)
    country = models.CharField(max_length=100, blank=True, null=True)

    editor_bio = models.TextField(blank=True, null=True)
    orcid_id = models.CharField(max_length=50, blank=True, null=True)
    linkedin_profile = models.URLField(blank=True, null=True)
    google_scholar_profile = models.URLField(blank=True, null=True)
    scopus_id = models.CharField(max_length=100, blank=True, null=True)
    web_of_science_id = models.CharField(max_length=100, blank=True, null=True)

    is_active = models.BooleanField(default=True)
    is_approved = models.BooleanField(default=False)  # New field
    date_joined = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.user.get_full_name()} ({self.user.email})"
    
from django.db import models
from django.contrib.auth.models import User
from journal.models import Journal

class EditorInChiefRecommendation(models.Model):
    RECOMMENDATION_CHOICES = [
        ('accept', 'Accept'),
        ('minor_revision', 'Minor Revision'),
        ('major_revision', 'Major Revision'),
        ('reject', 'Reject'),
        ('pending', 'Pending Review'),
    ]

    journal = models.ForeignKey(Journal, on_delete=models.CASCADE, related_name='eic_recommendations')
    editor_in_chief = models.ForeignKey('EditorInChief', on_delete=models.CASCADE)
    
    recommendation = models.CharField(
        max_length=20,
        choices=RECOMMENDATION_CHOICES,
        default='pending'
    )
    
    # Decision Details
    decision_summary = models.TextField(blank=True, null=True)
    decision_notes = models.TextField(blank=True, null=True)
    decision_date = models.DateTimeField(auto_now_add=True)
    
    # Review Process
    requires_review = models.BooleanField(default=False)
    review_deadline = models.DateField(blank=True, null=True)
    
    # Status Tracking
    is_final_decision = models.BooleanField(default=False)
    
    class Meta:
        unique_together = ('journal', 'editor_in_chief')
        ordering = ['-decision_date']
        
    def __str__(self):
        return f"{self.editor_in_chief.user.get_full_name()}'s recommendation for {self.journal.title}"

class EditorInChiefFeedback(models.Model):
    recommendation = models.ForeignKey(EditorInChiefRecommendation, on_delete=models.CASCADE, related_name='feedbacks')
    
    feedback_text = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    # Can be internal or for authors
    is_public = models.BooleanField(default=False)
    
    def __str__(self):
        return f"Feedback on {self.recommendation}"