from django.urls import path
from .views import *

urlpatterns = [
    path('register/', AreaEditorRegistrationView.as_view(), name='register-area-editor'), #end point to register as a new area editor
    path('login/', LoginView.as_view(), name='login'), #end point to login as area editor
    path('update/<int:pk>/', AreaEditorUpdateByIdView.as_view(), name='area-editor-update-by-id'), #end point to update a particular area editor
    path('get-all/', AreaEditorListView.as_view(), name='area-editor-list'), #end point to get the details of all the area editors
    path('get-details/<int:pk>/', AreaEditorDetailView.as_view(), name='area-editor-detail'), #end point to get the details of a particular area editor
    path('approve-area-editor/<int:pk>/', ApproveAreaEditorView.as_view(), name='approve-area-editor'), #end point to approve a particular area editor
    path('get-approved-area-editors/', ApprovedAreaEditorListView.as_view(), name='approved-area-editors'), #end point to get the list of approved area editors
    path('assign/<int:journal_id>/<int:area_editor_id>/', AssignJournalToAreaEditorAPIView.as_view(), name='assign-journal-to-area-editor'), #end point to assign a aparticular journal to a partiular area editor
    path('journal-assignments/<int:area_editor_id>/', JournalAssignmentsByAreaEditorView.as_view(), name='journal-assignments-by-area-editor'), #end point to get the list of journal assignments for a particular area editor
    path(
        'submit-recommendation/<int:area_editor_id>/journal/<int:journal_id>/',
        SubmitAreaEditorRecommendationView.as_view(),
        name='submit-area-editor-recommendation'
    ),
    path(
    'assignments/<int:journal_id>/<int:area_editor_id>/set-completed/',
    SetAreaEditorAssignmentToCompletedView.as_view(),
    name='area-editor-set-completed'
    ),

    path(
    'assignments/<int:journal_id>/<int:area_editor_id>/set-in-progress/',
    SetAreaEditorAssignmentToInProgressView.as_view(),
    name='area-editor-set-in-progress'
    ),

    path('validate-token/', ValidateAreaEditorTokenView.as_view(), name='validate_area_editor_token'),

        # ... your existing URLs ...
    path('<int:journal_id>/recommendations/', JournalRecommendationsListView.as_view(), name='journal-recommendations-list'),

    path('approval-status/<int:area_editor_id>/', AreaEditorApprovalStatusView.as_view(), name='area-editor-approval-status'),

    path('recommendations/by-journal/<int:journal_id>/', AreaEditorRecommendationsByJournalView.as_view(), name='areaeditor-recommendations-by-journal'),
]