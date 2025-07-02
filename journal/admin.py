from django.contrib import admin

# Register your models here.
from .models import Journal, SubjectArea, JournalSection

@admin.register(SubjectArea)
class SubjectAreaAdmin(admin.ModelAdmin):
    list_display = ['id', 'name']
    search_fields = ['name']

@admin.register(JournalSection)
class JournalSectionAdmin(admin.ModelAdmin):
    list_display = ['id', 'name']
    search_fields = ['name']

@admin.register(Journal)
class JournalAdmin(admin.ModelAdmin):
    list_display = ['id', 'title', 'corresponding_author', 'submission_date', 'status']
    list_filter = ['status', 'subject_area', 'journal_section']
    search_fields = ['title', 'abstract', 'keywords']
    filter_horizontal = ['co_authors']
    readonly_fields = ['submission_date']
