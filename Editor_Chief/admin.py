from django.contrib import admin
from .models import EditorInChief,EditorInChiefRecommendation

@admin.register(EditorInChief)
class EditorInChiefAdmin(admin.ModelAdmin):
    list_display = ('user_full_name', 'institution', 'position_title', 'country', 'is_active', 'date_joined')
    search_fields = ('user__first_name', 'user__last_name', 'user__email', 'institution', 'country')
    list_filter = ('is_active', 'country')
    readonly_fields = ('date_joined',)

    def user_full_name(self, obj):
        return obj.user.get_full_name()
    user_full_name.short_description = 'Name'

@admin.register(EditorInChiefRecommendation)
class EditorInChiefRecommendationAdmin(admin.ModelAdmin):
    list_display = ('id', 'get_journal', 'get_editor', 'get_recommendation', 'get_decision_summary', 'is_final_decision', 'decision_date')
    list_filter = ('recommendation', 'is_final_decision', 'editor_in_chief')
    search_fields = ('journal__title', 'editor_in_chief__user__username', 'recommendation', 'decision_summary')
    readonly_fields = ('decision_date',)
    
    def get_queryset(self, request):
        return super().get_queryset(request).select_related('journal', 'editor_in_chief__user')
    
    def get_journal(self, obj):
        return obj.journal.title if obj.journal else ''
    get_journal.short_description = 'Journal'
    get_journal.admin_order_field = 'journal__title'
    
    def get_editor(self, obj):
        return obj.editor_in_chief.user.get_full_name() if obj.editor_in_chief else ''
    get_editor.short_description = 'Editor'
    get_editor.admin_order_field = 'editor_in_chief__user__last_name'
    
    def get_recommendation(self, obj):
        return obj.get_recommendation_display()  # This will show the human-readable choice
    get_recommendation.short_description = 'Recommendation'
    
    def get_decision_summary(self, obj):
        return obj.decision_summary[:50] + '...' if obj.decision_summary else ''
    get_decision_summary.short_description = 'Decision Summary'