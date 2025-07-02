from django.db import models
from django.contrib.auth.models import User
from author.models import Author  # Import Author model from the correct app
from django.utils import timezone
from datetime import timedelta

class SubjectArea(models.Model):
    name = models.CharField(max_length=100, unique=True)

    def __str__(self):
        return self.name

class JournalSection(models.Model):
    name = models.CharField(max_length=100, unique=True)

    def __str__(self):
        return self.name

class Journal(models.Model):
    STATUS_CHOICES = [
        ('submitted', 'Submitted'),
        ('under_review', 'Under Review'),
        ('revisions_required', 'Revisions Required'),
        ('accepted', 'Accepted'),
        ('rejected', 'Rejected'),
        ('review_done','Review Done'),
        ('assigned_to_area_editor', 'Assigned to Area Editor'),
        ('assigned_to_associate_editor', 'Assigned to Associate Editor'), 
    ]

    title = models.CharField(max_length=255)
    abstract = models.TextField()
    keywords = models.CharField(max_length=255, help_text="Comma-separated keywords")
    subject_area = models.ForeignKey(SubjectArea, on_delete=models.SET_NULL, null=True)
    journal_section = models.ForeignKey(JournalSection, on_delete=models.SET_NULL, null=True)
    language = models.CharField(max_length=50)
    manuscript_file = models.FileField(upload_to='journals/')
    supplementary_files = models.JSONField(blank=True, null=True, help_text="List of supplementary file names or URLs")
    corresponding_author = models.ForeignKey(Author, on_delete=models.CASCADE)
    author_name_text = models.CharField(max_length=255,blank=True,null=True)  # ✅ New field to store author name as text
    co_authors = models.ManyToManyField(Author, related_name='coauthored_journals', blank=True)
    submission_date = models.DateTimeField(auto_now_add=True)
    status = models.CharField(max_length=50, choices=STATUS_CHOICES, default='submitted')

    def __str__(self):
        return self.title


class DeletionOTP(models.Model):
    author = models.ForeignKey(Author, on_delete=models.CASCADE)
    journal_id = models.IntegerField()
    otp = models.CharField(max_length=6)
    created_at = models.DateTimeField(auto_now_add=True)

    def is_valid(self):
        return timezone.now() < self.created_at + timedelta(minutes=10)
