from django.contrib import admin

from .models import (
    AssociateEditor,
    AssociateEditorAssignment,
    AssociateEditorRecommendation
)

@admin.register(AssociateEditor)
class AssociateEditorAdmin(admin.ModelAdmin):
    list_display = (
        'user', 'institution', 'position_title', 'country',
        'is_active', 'number_of_reviews_completed', 'number_of_assignments_handled', 'date_joined'
    )
    list_filter = ('is_active', 'subject_areas', 'country')
    search_fields = (
        'user__first_name', 'user__last_name', 'user__email',
        'institution', 'department', 'country'
    )
    filter_horizontal = ('subject_areas',)

@admin.register(AssociateEditorAssignment)
class AssociateEditorAssignmentAdmin(admin.ModelAdmin):
    list_display = ('journal', 'associate_editor', 'status', 'assigned_date', 'completed_date')
    list_filter = ('status', 'assigned_date')
    search_fields = ('journal__title', 'associate_editor__user__email')

@admin.register(AssociateEditorRecommendation)
class AssociateEditorRecommendationAdmin(admin.ModelAdmin):
    list_display = ('journal', 'associate_editor', 'recommendation', 'submitted_at')
    list_filter = ('recommendation', 'submitted_at')
    search_fields = ('journal__title', 'associate_editor__user__email')
