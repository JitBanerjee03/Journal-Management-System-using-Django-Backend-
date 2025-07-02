from django.shortcuts import render

# Create your views here.
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from .models import SubjectArea,JournalSection,Journal,DeletionOTP
from .serializers import SubjectAreaSerializer,JournalSectionSerializer,JournalSerializer,JournalStatusSerializer
from rest_framework.generics import ListAPIView
from author.models import Author
from rest_framework.parsers import MultiPartParser
from django.shortcuts import get_object_or_404
from .utils import generate_otp, send_otp_email

class SubjectAreaCreateAPIView(APIView): # end point to add subject area by the admin
    def post(self, request, *args, **kwargs):
        serializer = SubjectAreaSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()  # Save the new SubjectArea
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class JournalSectionCreateAPIView(APIView): # end point to add journal section by the admin 
    def post(self, request, *args, **kwargs):
        serializer = JournalSectionSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
class SubjectAreaListAPIView(ListAPIView): #end point to get all subject areas
    queryset = SubjectArea.objects.all()
    serializer_class = SubjectAreaSerializer

class JournalSectionListAPIView(ListAPIView): #end point to get all journal section
    queryset = JournalSection.objects.all()
    serializer_class = JournalSectionSerializer

class SubmitJournalAPIView(APIView):  # endpoint to submit journal by the author
    parser_classes = [MultiPartParser]

    def post(self, request, author_id, *args, **kwargs):
        try:
            author = Author.objects.get(id=author_id)
        except Author.DoesNotExist:
            return Response({'error': 'Author not found'}, status=404)

        data = request.data.dict()
        data['corresponding_author'] = author.id  # inject author ID directly

        # If you expect co_authors as a list
        co_authors = request.data.getlist('co_authors')
        files = request.FILES

        journal = Journal.objects.create(
            title=data.get('title'),
            abstract=data.get('abstract'),
            keywords=data.get('keywords'),
            subject_area_id=data.get('subject_area'),
            journal_section_id=data.get('journal_section'),
            language=data.get('language'),
            manuscript_file=files.get('manuscript_file'),
            supplementary_files=data.get('supplementary_files') or None,
            corresponding_author=author,
            author_name_text=f"{author.user.first_name} {author.user.last_name}",  # ✅ Auto-fill author name
            status=data.get('status', 'submitted'),
        )

        if co_authors:
            journal.co_authors.set(co_authors)

        journal.save()

        return Response({'message': 'Journal submitted successfully'}, status=201)
    
class JournalListAPIView(APIView): #end point to get all the journals (GET request)
    def get(self, request, *args, **kwargs):
        journals = Journal.objects.all()
        serializer = JournalSerializer(journals, many=True)
        return Response(serializer.data)
    
class JournalDetailAPIView(APIView): #end point to get journal details by journal id (GET request)
    def get(self, request, journal_id, *args, **kwargs):
        journal = get_object_or_404(Journal, id=journal_id)
        serializer = JournalSerializer(journal)
        return Response(serializer.data, status=status.HTTP_200_OK)
    
class JournalsByAuthorAPIView(APIView): #end point to get journal by a particular author (GET request)
    def get(self, request, author_id, *args, **kwargs):
        author = get_object_or_404(Author, id=author_id)
        journals = Journal.objects.filter(corresponding_author=author)
        serializer = JournalSerializer(journals, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

class UpdateJournalBeforeReviewAPIView(APIView): #end point to update journal details before the review phase (PATCH request)
    def patch(self, request, journal_id, *args, **kwargs):
        journal = get_object_or_404(Journal, id=journal_id)

        # Only allow update if journal is in 'submitted' status
        if journal.status != 'submitted':
            return Response(
                {"error": "Journal can only be updated before the review phase."},
                status=status.HTTP_400_BAD_REQUEST
            )

        serializer = JournalSerializer(journal, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class AuthorJournalStatusAPIView(APIView): #end point to get journal status by author id (GET request)
    def get(self, request, author_id, *args, **kwargs):
        author = get_object_or_404(Author, id=author_id)
        journals = Journal.objects.filter(corresponding_author=author)
        serializer = JournalStatusSerializer(journals, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

class RequestJournalDeletionAPIView(APIView): #end point to request journal delection (POST request) after hitting this an otp will be sent to the author registerd email id
    def post(self, request, journal_id):
        journal = get_object_or_404(Journal, id=journal_id)
        author = journal.corresponding_author

        if journal.status != 'submitted':
            return Response({"error": "Journal cannot be deleted unless it is still submitted."}, status=400)

        otp = generate_otp()
        DeletionOTP.objects.create(author=author, journal_id=journal.id, otp=otp)
        send_otp_email(author.user.email, otp)

        return Response({"message": "OTP sent to registered email."}, status=200)

class ConfirmJournalDeletionAPIView(APIView): #end point to confirm journ deleteion (POST request) the otp is added in the body
    def post(self, request, journal_id):
        otp_input = request.data.get('otp')
        journal = get_object_or_404(Journal, id=journal_id)
        author = journal.corresponding_author

        try:
            otp_obj = DeletionOTP.objects.filter(
                author=author, journal_id=journal.id, otp=otp_input
            ).latest('created_at')
        except DeletionOTP.DoesNotExist:
            return Response({"error": "Invalid or expired OTP."}, status=400)

        if not otp_obj.is_valid():
            return Response({"error": "OTP has expired."}, status=400)

        journal.delete()
        return Response({"message": "Journal deleted successfully."}, status=204)

class SubmittedJournalsAPIView(APIView):  # Endpoint to get all submitted journals
    def get(self, request, *args, **kwargs):
        # Filter journals by 'submitted' status
        submitted_journals = Journal.objects.filter(status='submitted')
        
        # Serialize the list of submitted journals
        serializer = JournalSerializer(submitted_journals, many=True)
        
        # Return the serialized data
        return Response(serializer.data, status=status.HTTP_200_OK)

class UnderReviewJournalsAPIView(APIView):  # Endpoint to get all journals under review
    def get(self, request, *args, **kwargs):
        under_review_journals = Journal.objects.filter(status='under_review')
        serializer = JournalSerializer(under_review_journals, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)
    
class RevisionsRequiredJournalsAPIView(APIView):  # Endpoint to get all journals requiring revisions
    def get(self, request, *args, **kwargs):
        revisions_required_journals = Journal.objects.filter(status='revisions_required')
        serializer = JournalSerializer(revisions_required_journals, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)
    
class AcceptedJournalsAPIView(APIView):  # Endpoint to get all accepted journals
    def get(self, request, *args, **kwargs):
        accepted_journals = Journal.objects.filter(status='accepted')
        serializer = JournalSerializer(accepted_journals, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)
    
class RejectedJournalsAPIView(APIView):  # Endpoint to get all rejected journals
    def get(self, request, *args, **kwargs):
        rejected_journals = Journal.objects.filter(status='rejected')
        serializer = JournalSerializer(rejected_journals, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

class SetJournalStatusMixin: # class to change the status of the journal
    new_status = None  # To be set by subclasses

    def post(self, request, journal_id, *args, **kwargs):
        journal = get_object_or_404(Journal, id=journal_id)
        old_status = journal.status
        journal.status = self.new_status
        journal.save()
        return Response({
            'message': f'Status updated from "{old_status}" to "{self.new_status}".',
            'journal_id': journal.id,
            'new_status': journal.status
        }, status=status.HTTP_200_OK)

class SetJournalUnderReviewAPIView(SetJournalStatusMixin, APIView): #end poin to set journal status to under review
    new_status = 'under_review'

class SetJournalRevisionsRequiredAPIView(SetJournalStatusMixin, APIView): #end point to set journal status to revision required
    new_status = 'revisions_required'

class SetJournalAcceptedAPIView(SetJournalStatusMixin, APIView): #end point to set journal status to accepted
    new_status = 'accepted'

class SetJournalRejectedAPIView(SetJournalStatusMixin, APIView): #end point to set journal status to rejected
    new_status = 'rejected'

class NotAcceptedOrRejectedJournalsAPIView(APIView):  # Endpoint to get all journals that are not accepted or rejected
    def get(self, request, *args, **kwargs):
        journals = Journal.objects.exclude(status__in=['accepted', 'rejected','revisions_required'])
        serializer = JournalSerializer(journals, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

class SetJournalAssignedToAreaEditorAPIView(SetJournalStatusMixin, APIView):  # POST: Mark as Assigned to Area Editor
    new_status = 'assigned_to_area_editor'

class SetJournalAssignedToAssociateEditorAPIView(SetJournalStatusMixin, APIView):  # POST: Mark as Assigned to Associate Editor
    new_status = 'assigned_to_associate_editor'

class SetJournalReviewDoneAPIView(SetJournalStatusMixin, APIView):  # POST: Mark as Review Done
    new_status = 'review_done'

class JournalsByCorrespondingAuthorAPIView(APIView):
    def get(self, request, corresponding_author_id, *args, **kwargs):
        author = get_object_or_404(Author, id=corresponding_author_id)
        journals = Journal.objects.filter(corresponding_author=author)
        serializer = JournalSerializer(journals, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)
