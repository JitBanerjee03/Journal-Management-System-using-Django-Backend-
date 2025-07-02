# author/urls.py
from django.urls import path
from .views import *

urlpatterns = [
    path('subjectarea/', SubjectAreaCreateAPIView.as_view(), name='subjectarea-create'), #end point to add new subject area (POST request)
    path('journalsection/', JournalSectionCreateAPIView.as_view(), name='journalsection-create'), #end point to add new journal section (POST request)
    path('subject-areas/', SubjectAreaListAPIView.as_view(), name='subjectarea-list'), #end point to get all subject areas (GET request)
    path('journal-sections/', JournalSectionListAPIView.as_view(), name='journalsection-list'), #end point to get all journal sections (GET request)
    path('submit-journal/<int:author_id>/', SubmitJournalAPIView.as_view(), name='submit-journal'), #end point to submit journal by the author
    path('get-all/', JournalListAPIView.as_view(), name='journal-list'), #end point to get all journals (GET request)
    path('detail/<int:journal_id>/', JournalDetailAPIView.as_view(), name='journal-detail'), #end point to get journal details by journal id (GET request) 
    path('submittedby-author/<int:author_id>/', JournalsByAuthorAPIView.as_view(), name='journals-by-author'), #end point to update the journal details by hournal id (PUT request)
    path('update-before-review/<int:journal_id>/', UpdateJournalBeforeReviewAPIView.as_view(), name='update-journal-before-review'), #end point to update journal details before the review phase (PATCH request)
    path('journal-status/<int:author_id>/', AuthorJournalStatusAPIView.as_view(), name='author-journal-status'), #end point to get journal status by the author id (GET request)
    
    #deletion of a particular journal by the author before the review phase
    path('request-deletion/<int:journal_id>/', RequestJournalDeletionAPIView.as_view()), #end point to request journal deletion (POST request) after hitting this an otp will be sent to the author registed email id
    path('confirm-deletion/<int:journal_id>/', ConfirmJournalDeletionAPIView.as_view()), #end point to confirm journal deletion (POST request) the otp is added in the body

    #end points to get journals based on the status of the journals eg:- submitted , rejected , unser review , accepted , etc
    path('submitted-journals/', SubmittedJournalsAPIView.as_view(), name='submitted-journals'), #end point to get all submitted journals (GET request)
    path('under-review-journals/', UnderReviewJournalsAPIView.as_view(), name='under-review-journals'), #end point to get all under review journals (GET request)
    path('revisions-required-journals/', RevisionsRequiredJournalsAPIView.as_view(), name='revisions-required-journals'), #end point to get all revisions required journals (GET request)
    path('accepted-journals/', AcceptedJournalsAPIView.as_view(), name='accepted-journals'), #end point to get all accepted journals (GET request)
    path('rejected-journals/', RejectedJournalsAPIView.as_view(), name='rejected-journals'), #end point to get all rejected journals (GET request)
    path('mark-assigned-to-area-editor/<int:journal_id>/', SetJournalAssignedToAreaEditorAPIView.as_view(), name='mark-assigned-to-area-editor'),
    path('mark-assigned-to-associate-editor/<int:journal_id>/', SetJournalAssignedToAssociateEditorAPIView.as_view(), name='mark-assigned-to-associate-editor'),
    path('mark-review-done/<int:journal_id>/', SetJournalReviewDoneAPIView.as_view(), name='mark-review-done'),
    
    #end points to change the status of the journal
    path('mark-under-review/<int:journal_id>/', SetJournalUnderReviewAPIView.as_view(), name='mark-under-review'), #end point to mark journal as under review (POST request)
    path('mark-revisions-required/<int:journal_id>/', SetJournalRevisionsRequiredAPIView.as_view(), name='mark-revisions-required'), #end point to mark journal as revisions required (POST request)
    path('mark-accepted/<int:journal_id>/', SetJournalAcceptedAPIView.as_view(), name='mark-accepted'), #end point to mark journal as accepted (POST request)
    path('mark-rejected/<int:journal_id>/', SetJournalRejectedAPIView.as_view(), name='mark-rejected'), #end point to mark journal as rejected (POST request)
    path('not-accepted-or-rejected/', NotAcceptedOrRejectedJournalsAPIView.as_view(), name='not-accepted-or-rejected-journals'),

    # urls.py
    path('by-corresponding-author/<int:corresponding_author_id>/', JournalsByCorrespondingAuthorAPIView.as_view(), name='journals-by-corresponding-author'), #end point to get journals by corrsponding author id
]
