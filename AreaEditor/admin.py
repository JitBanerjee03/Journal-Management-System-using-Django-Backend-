from django.contrib import admin
from .models import AreaEditor, EducationDetailOfAreaEditor
from .models import AreaEditorJournalAssignment

class EducationInline(admin.TabularInline):
    model = EducationDetailOfAreaEditor
    extra = 1
    fields = (
        'degree', 'field_of_study', 'institution',
        'start_year', 'end_year', 'grade_or_score', 'certificate'
    )
    readonly_fields = ()
    show_change_link = True

@admin.register(AreaEditor)
class AreaEditorAdmin(admin.ModelAdmin):
    list_display = (
        'user_full_name', 'email', 'institution', 'country',
        'is_approved', 'is_active', 'date_joined'
    )
    list_filter = ('is_approved', 'is_active', 'country', 'subject_areas')
    search_fields = ('user__first_name', 'user__last_name', 'user__email', 'institution', 'country')
    ordering = ('-date_joined',)
    inlines = [EducationInline]

    def user_full_name(self, obj):
        return obj.user.get_full_name()
    user_full_name.short_description = 'Name'

    def email(self, obj):
        return obj.user.email

@admin.register(EducationDetailOfAreaEditor)
class EducationDetailOfAreaEditorAdmin(admin.ModelAdmin):
    list_display = (
        'area_editor', 'degree', 'field_of_study', 'institution',
        'start_year', 'end_year', 'grade_or_score'
    )
    search_fields = ('degree', 'field_of_study', 'institution', 'area_editor__user__email')
    list_filter = ('start_year', 'end_year', 'institution')
    ordering = ('-end_year',)

@admin.register(AreaEditorJournalAssignment)
class AreaEditorJournalAssignmentAdmin(admin.ModelAdmin):
    list_display = ('journal', 'area_editor', 'assigned_date', 'completed_date', 'status')
    list_filter = ('status', 'assigned_date', 'completed_date')
    search_fields = (
        'journal__title',
        'area_editor__user__first_name',
        'area_editor__user__last_name',
        'area_editor__user__email',
    )
    autocomplete_fields = ('journal', 'area_editor')
    readonly_fields = ('assigned_date',)

# admin.py

from django.contrib import admin
from .models import AreaEditorRecommendation

@admin.register(AreaEditorRecommendation)
class AreaEditorRecommendationAdmin(admin.ModelAdmin):
    list_display = (
        'journal', 
        'get_area_editor_name',
        'recommendation', 
        'overall_rating',
        'submitted_at'
    )
    list_filter = ('recommendation', 'submitted_at')
    search_fields = (
        'journal__title', 
        'area_editor__user__first_name',
        'area_editor__user__last_name',
        'area_editor__user__email'
    )
    readonly_fields = ('submitted_at',)

    def get_area_editor_name(self, obj):
        return obj.area_editor.user.get_full_name()
    get_area_editor_name.short_description = 'Area Editor'

