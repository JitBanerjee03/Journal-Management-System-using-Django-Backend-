from django.contrib import admin

# Register your models here.
from .models import Reviewer, EducationDetailOfReviewer,ReviewerAssignmentHistory,ReviewFeedback  # Import models

# Register the Reviewer model
class ReviewerAdmin(admin.ModelAdmin):
    list_display = ('user', 'institution', 'position_title', 'is_approved', 'is_active', 'date_joined')
    search_fields = ('user__first_name', 'user__last_name', 'user__email', 'institution')
    list_filter = ('is_approved', 'is_active', 'institution')

admin.site.register(Reviewer, ReviewerAdmin)

# Register the EducationDetailOfReviewer model
class EducationDetailOfReviewerAdmin(admin.ModelAdmin):
    list_display = ('reviewer', 'degree', 'field_of_study', 'institution', 'start_year', 'end_year')
    search_fields = ('reviewer__user__first_name', 'reviewer__user__last_name', 'degree', 'institution')
    list_filter = ('degree', 'field_of_study')

admin.site.register(EducationDetailOfReviewer, EducationDetailOfReviewerAdmin)

@admin.register(ReviewerAssignmentHistory)
class ReviewerAssignmentHistoryAdmin(admin.ModelAdmin):
    list_display = ('journal', 'reviewer', 'subject_area', 'status', 'assigned_date', 'completed_date')
    list_filter = ('status', 'subject_area')
    search_fields = ('journal__title', 'reviewer__user__first_name', 'reviewer__user__last_name')

@admin.register(ReviewFeedback)
class ReviewFeedbackAdmin(admin.ModelAdmin):
    list_display = ('id', 'journal', 'reviewer', 'rating', 'review_date', 'recommendation')
    search_fields = ('journal__title', 'reviewer__user__first_name', 'reviewer__user__last_name')
    list_filter = ('rating', 'recommendation', 'review_date')
    readonly_fields = ('review_date',)