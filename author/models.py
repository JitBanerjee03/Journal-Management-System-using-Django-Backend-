from django.db import models
from django.contrib.auth.models import User

class Author(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)

    # Contact Information
    phone_number = models.CharField(max_length=20, blank=True, null=True)
    profile_picture = models.ImageField(upload_to='author_profile_picture/', blank=True, null=True)

    # Affiliation
    institution = models.CharField(max_length=255)
    department = models.CharField(max_length=255, blank=True, null=True)
    position_title = models.CharField(max_length=255, blank=True, null=True)

    # Address
    country = models.CharField(max_length=100)
    city = models.CharField(max_length=100, blank=True, null=True)
    address = models.TextField(blank=True, null=True)

    # Academic / Research Info
    orcid_id = models.CharField(max_length=50, blank=True, null=True)
    research_interests = models.TextField(blank=True, null=True)
    google_scholar_profile = models.URLField(blank=True, null=True)
    personal_website = models.URLField(blank=True, null=True)

    # Other Information
    biography = models.TextField(blank=True, null=True)
    languages_spoken = models.CharField(max_length=255, blank=True, null=True)

    # Role Options
    reviewer_interest = models.BooleanField(default=False)
    corresponding_author = models.BooleanField(default=False)

    # System Info
    date_joined = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.user.first_name} {self.user.last_name} ({self.user.email})"
