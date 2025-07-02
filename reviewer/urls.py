from django.urls import path
from .views import *

urlpatterns = [
    path('register-reviewer/', ReviewerRegistrationView.as_view(), name='register-reviewer'), # end point to apply for registration of the reviewer (POST request)
    path('login/', LoginView.as_view(), name='login'), #end point to login as a reviewer (POST request)
    path('all-reviewers/',ReviewerListAPIView.as_view(), name='reviewer-list'), #end point to get the list of all reviewers (GET request)
    path('get-profile/<int:reviewer_id>/', ReviewerDetailAPIView.as_view(), name='reviewer-detail'),
    path('update/<int:reviewer_id>/', ReviewerUpdateAPIView.as_view(), name='reviewer-update'),
    path('approve/<int:reviewer_id>/', ApproveReviewerAPIView.as_view(), name='approve-reviewer'), #end point to approve the reviewer by the higher authority (PATCH request)
    path('disapprove/<int:reviewer_id>/', DisapproveReviewerAPIView.as_view(), name='disapprove-reviewer'), #end point to disapprove the reviewer by the higher authority (PATCH request)
    path('subject-area/<int:subject_area_id>/', ReviewersBySubjectAreaAPIView.as_view(), name='reviewers-by-subject-area'), #end point to get the list of all approved reviewers by subject area (GET request)
    path('assign-reviewer/<int:reviewer_id>/<int:journal_id>/', AssignReviewerToJournalAPIView.as_view(), name='assign-reviewer'), #end point to assign the reviewer to a journal (POST request)
    path('assigned-journals/<int:reviewer_id>/', ReviewerAssignedJournalsAPIView.as_view(), name='reviewer-assigned-journals'), #end point to get the list of all journals assigned to the reviewer (GET request)
    path( #end point to reject the assigned journal by the reviewer (PATCH request)
        'reject/<int:journal_id>/<int:reviewer_id>/',
        RejectAssignedJournalAPIView.as_view(),
        name='reject-assignment'
    ),
    path('review-feedback/<int:journal_id>/<int:reviewer_id>/', SubmitReviewFeedbackAPIView.as_view(), name='submit-review-feedback'),
    path('approved/', ApprovedReviewerListAPIView.as_view(), name='approved-reviewer-list'),#end point to get the list of all approved reviewers
    path('unapproved/', UnApprovedReviewerListAPIView.as_view(), name='approved-reviewer-list'),#end point to get the list of all approved reviewers
    path('reviewer-assignments/', ReviewerAssignmentHistoryListView.as_view(), name='reviewer-assignments-list'),
    path('review-feedback/journal/<int:journal_id>/', review_feedback_by_journal, name='review-feedback-by-journal'),
    path('reviewer/<int:reviewer_id>/assignments/', ReviewerJournalAssignmentListView.as_view(), name='reviewer-assignments'),
    path('validate-token/', ValidateReviewerTokenView.as_view(), name='reviewer-validate-token'),
]