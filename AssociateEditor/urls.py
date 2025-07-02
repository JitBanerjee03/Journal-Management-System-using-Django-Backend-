from django.urls import path
from .views import *

urlpatterns = [
    path('register/',AssociateEditorRegistrationView.as_view(), name='ae-register'),
    path('login/', EmailLoginView.as_view(), name='login'),
    path('get-details/<int:id>/', AssociateEditorDetailView.as_view(), name='associate-editor-detail'),
    path('get-all/', AssociateEditorListView.as_view(), name='associate-editor-list'),
    path('update/<int:id>/', AssociateEditorUpdateView.as_view(), name='associate-editor-update'),
    path('subject-area/<int:subject_area_id>/', AssociateEditorsBySubjectAreaView.as_view(), name='associate-editors-by-subject'),
    path('assign-journal/<int:journal_id>/<int:editor_id>/', AssignJournalToEditorView.as_view(), name='assign-journal-to-editor'),
    path('by-section/<int:section_id>/', EditorsByJournalSectionView.as_view(), name='editors-by-section'),
    path('recommendations/submit/<int:journal_id>/<int:ae_id>/', SubmitRecommendationView.as_view(), name='submit-recommendation'),
    path('recommendations/journal/<int:journal_id>/', JournalRecommendationsView.as_view(), name='journal-recommendations'),
    path('assigned-journals/<int:editor_id>/', JournalsAssignedToEditorView.as_view(), name='assigned-journals'),
    path(
    'assignments/<int:journal_id>/<int:associate_editor_id>/set-reviewing/',
    SetAssignmentToReviewingView.as_view(),
    name='set-assignment-reviewing'
    ),
    path(
    'assignments/<int:journal_id>/<int:associate_editor_id>/set-completed/',
    SetAssignmentToCompletedView.as_view(),
    name='set-assignment-completed'
    ),
    path('associate-editor-assignment/', AssociateEditorAssignmentListView.as_view(), name='ae-assignment-list'),
    path('validate-token/', ValidateAssociateEditorTokenView.as_view(), name='associate-editor-validate-token'),
]
