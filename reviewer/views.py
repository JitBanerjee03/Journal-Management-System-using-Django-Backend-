from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from .serializers import *
from rest_framework.views import APIView
from rest_framework.authtoken.models import Token
from rest_framework.exceptions import AuthenticationFailed
from .models import *
from rest_framework.permissions import IsAuthenticated
from rest_framework.exceptions import NotFound
from django.core.mail import send_mail
from django.conf import settings
from rest_framework.status import HTTP_200_OK
from journal.models import SubjectArea,Journal
from rest_framework.exceptions import NotFound, ValidationError
from django.utils import timezone
from rest_framework.views import APIView
from rest_framework.response import Response
from .models import Reviewer, Journal, ReviewFeedback, ReviewerAssignmentHistory
from django.shortcuts import get_object_or_404
from rest_framework.exceptions import NotFound, PermissionDenied
from rest_framework.generics import ListAPIView
from rest_framework import generics
from django.db.models import Prefetch
from rest_framework.parsers import MultiPartParser, FormParser, JSONParser
import json
from rest_framework_simplejwt.views import TokenObtainPairView
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework_simplejwt.authentication import JWTAuthentication

class ReviewerRegistrationView(APIView): #end point to apply for registration as a reviewer
    def post(self, request):
        serializer = ReviewerRegistrationSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response({"message": "Reviewer registered successfully."}, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

'''class LoginView(APIView): #end point to login as a reviewer
    def post(self, request, *args, **kwargs):
        serializer = LoginSerializer(data=request.data)
        if serializer.is_valid():
            user = serializer.validated_data['user']
            token, created = Token.objects.get_or_create(user=user)

            try:
                reviewer = Reviewer.objects.get(user=user)
                reviewer_id = reviewer.id
            except Reviewer.DoesNotExist:
                raise AuthenticationFailed("Reviewer profile not found.")

            return Response({
                'token': token.key,
                'reviewer_id': reviewer_id
            }, status=status.HTTP_200_OK)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)'''

class LoginView(TokenObtainPairView):
    serializer_class = ReviewerTokenObtainPairSerializer
    permission_classes = [AllowAny]

    def post(self, request, *args, **kwargs):
        if 'email' not in request.data or 'password' not in request.data:
            return Response(
                {'error': 'Both email and password are required'},
                status=status.HTTP_400_BAD_REQUEST
            )

        data = request.data.copy()
        data['username'] = data['email']
        
        try:
            response = super().post(request, *args, **kwargs)
            return Response(response.data, status=response.status_code)
        except Exception as e:
            return Response(
                {'error': str(e)},
                status=status.HTTP_400_BAD_REQUEST
            )

class ReviewerListAPIView(APIView): #end point to get the list of all reviewers
    def get(self, request):
        reviewers = Reviewer.objects.all()
        serializer = FullReviewerDetailSerializer(reviewers, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

'''class ReviewerUpdateAPIView(APIView): #end point to update the reviewer profile
    def patch(self, request, reviewer_id, *args, **kwargs):
        try:
            reviewer = Reviewer.objects.get(id=reviewer_id)
        except Reviewer.DoesNotExist:
            return Response({'error': 'Reviewer not found'}, status=status.HTTP_404_NOT_FOUND)

        serializer = ReviewerUpdateSerializer(reviewer, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)'''

class ReviewerUpdateAPIView(APIView):
    parser_classes = [MultiPartParser, FormParser, JSONParser]

    def patch(self, request, reviewer_id, *args, **kwargs):
        try:
            reviewer = Reviewer.objects.get(id=reviewer_id)
        except Reviewer.DoesNotExist:
            return Response({'error': 'Reviewer not found'}, status=status.HTTP_404_NOT_FOUND)

        # Handle education data sent as JSON string
        if 'educations' in request.data and isinstance(request.data['educations'], str):
            try:
                request.data._mutable = True
                request.data['educations'] = json.loads(request.data['educations'])
                request.data._mutable = False
            except json.JSONDecodeError:
                return Response({'error': 'Invalid education data format'}, status=status.HTTP_400_BAD_REQUEST)

        serializer = ReviewerUpdateSerializer(reviewer, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
class ApproveReviewerAPIView(APIView): #end point to approve the reviewer by the higher authority
    def patch(self, request, reviewer_id):
        try:
            reviewer = Reviewer.objects.get(id=reviewer_id)
        except Reviewer.DoesNotExist:
            raise NotFound(detail="Reviewer not found.")

        # Update the 'is_approved' field to True
        reviewer.is_approved = True
        reviewer.save()

        # Send the approval email
        subject = "Congratulations! Your Reviewership Has Been Approved"
        message = f"Dear {reviewer.user.first_name} {reviewer.user.last_name},\n\n" \
                  "We are pleased to inform you that your reviewership status has been approved. " \
                  "Thank you for your valuable contribution to our journal.\n\n" \
                  "Best regards,\nThe Editorial Team"
        recipient_email = reviewer.user.email

        send_mail(
            subject,
            message,
            settings.DEFAULT_FROM_EMAIL,  # Your system's default sender email
            [recipient_email],
            fail_silently=False
        )

        return Response({"message": "Reviewer approved successfully and notified via email."}, status=HTTP_200_OK)
    
class DisapproveReviewerAPIView(APIView): #end point to disapprove the reviewer by the higher authority
    def patch(self, request, reviewer_id):
        try:
            reviewer = Reviewer.objects.get(id=reviewer_id)
        except Reviewer.DoesNotExist:
            raise NotFound(detail="Reviewer not found.")

        # Update the 'is_approved' field to False
        reviewer.is_approved = False
        reviewer.save()

        # Send the disapproval email
        subject = "Your Reviewership Has Been Disapproved"
        message = f"Dear {reviewer.user.first_name} {reviewer.user.last_name},\n\n" \
                  "We regret to inform you that your reviewership status has been disapproved. " \
                  "Please contact the editorial team if you have any questions.\n\n" \
                  "Best regards,\nThe Editorial Team"
        recipient_email = reviewer.user.email

        send_mail(
            subject,
            message,
            settings.DEFAULT_FROM_EMAIL,  # Your system's default sender email
            [recipient_email],
            fail_silently=False
        )

        return Response({"message": "Reviewer disapproved successfully and notified via email."}, status=HTTP_200_OK)

class ReviewersBySubjectAreaAPIView(APIView): #end point to get the list of approved reviewers for a specific subject area
    def get(self, request, subject_area_id):
        try:
            subject_area = SubjectArea.objects.get(id=subject_area_id)
        except SubjectArea.DoesNotExist:
            raise NotFound("Subject area not found.")

        reviewers = Reviewer.objects.filter(subject_areas=subject_area, is_approved=True)
        if not reviewers.exists():
            return Response({"message": "No approved reviewers found for this subject area."}, status=status.HTTP_200_OK)

        serializer = ReviewerSerializer(reviewers, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

class AssignReviewerToJournalAPIView(APIView): #end point to assign a approved reviewer to a journal
    def post(self, request, reviewer_id, journal_id):
        try:
            reviewer = Reviewer.objects.get(id=reviewer_id, is_approved=True)
        except Reviewer.DoesNotExist:
            raise NotFound("Reviewer not found or not approved.")

        try:
            journal = Journal.objects.get(id=journal_id)
        except Journal.DoesNotExist:
            raise NotFound("Journal not found.")

        # Check if this reviewer is already assigned to this journal
        if ReviewerAssignmentHistory.objects.filter(
            journal=journal, 
            reviewer=reviewer,
            status__in=['assigned', 'completed']
        ).exists():
            raise ValidationError("This reviewer is already assigned to this journal.")

        # If not, assign
        assignment = ReviewerAssignmentHistory.objects.create(
            journal=journal,
            reviewer=reviewer,
            subject_area=journal.subject_area  # optional
        )

        return Response({
            "message": "Reviewer assigned to journal successfully.",
            "assignment_id": assignment.id
        }, status=status.HTTP_201_CREATED)

class RejectAssignedJournalAPIView(APIView): #end point to reject the assigned journal review by the reviewer
    def patch(self, request, assignment_id):
        try:
            assignment = ReviewerAssignmentHistory.objects.get(id=assignment_id)
        except ReviewerAssignmentHistory.DoesNotExist:
            raise NotFound("Assignment not found.")

        if assignment.status == 'completed':
            return Response({"message": "Cannot reject a completed review."}, status=status.HTTP_400_BAD_REQUEST)

        rejection_reason = request.data.get("rejection_reason")
        subject_area_id = request.data.get("subject_area_id")

        if not rejection_reason:
            raise ValidationError("Rejection reason is required.")
        
        if subject_area_id:
            try:
                subject_area = SubjectArea.objects.get(id=subject_area_id)
                assignment.subject_area = subject_area
            except SubjectArea.DoesNotExist:
                raise NotFound("Subject area not found.")

        assignment.status = 'rejected'
        assignment.rejection_reason = rejection_reason
        assignment.completed_date = timezone.now()
        assignment.save()

        return Response({"message": "Journal review assignment rejected successfully."}, status=status.HTTP_200_OK)

class ReviewerAssignedJournalsAPIView(APIView): #end point to get the list of all journals assigned to the reviewer
    def get(self, request, reviewer_id):
        try:
            reviewer = Reviewer.objects.get(id=reviewer_id, is_approved=True)
        except Reviewer.DoesNotExist:
            raise NotFound("Approved reviewer not found.")

        assignments = ReviewerAssignmentHistory.objects.filter(
            reviewer=reviewer,
            status='assigned'
        ).select_related('journal', 'journal__corresponding_author')

        serializer = ReviewerAssignmentHistorySerializer(assignments, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)
    
class RejectAssignedJournalAPIView(APIView): #end point to reject the assigned journal review by the reviewer
    def patch(self, request, journal_id, reviewer_id):
        try:
            assignment = ReviewerAssignmentHistory.objects.get(
                journal_id=journal_id,
                reviewer_id=reviewer_id,
                status='assigned'  # Only allow rejecting if still assigned
            )
        except ReviewerAssignmentHistory.DoesNotExist:
            raise NotFound("Active assignment not found for this reviewer and journal.")

        rejection_reason = request.data.get("rejection_reason")
        subject_area_id = request.data.get("subject_area_id")

        if not rejection_reason:
            raise ValidationError("Rejection reason is required.")

        if subject_area_id:
            try:
                subject_area = SubjectArea.objects.get(id=subject_area_id)
                assignment.subject_area = subject_area
            except SubjectArea.DoesNotExist:
                raise NotFound("Subject area not found.")

        assignment.status = 'rejected'
        assignment.rejection_reason = rejection_reason
        assignment.completed_date = timezone.now()
        assignment.save()

        return Response({"message": "Journal review assignment rejected successfully."}, status=status.HTTP_200_OK)
    
class SubmitReviewFeedbackAPIView(APIView):  # endpoint to submit the review feedback by the reviewer
    def post(self, request, journal_id, reviewer_id):
        journal = get_object_or_404(Journal, id=journal_id)
        reviewer = get_object_or_404(Reviewer, id=reviewer_id)

        # Ensure reviewer is assigned and not rejected
        assignment_exists = ReviewerAssignmentHistory.objects.filter(
            journal=journal,
            reviewer=reviewer,
            status='assigned'
        ).exists()

        if not assignment_exists:
            return Response(
                {"error": "Reviewer is not currently assigned to this journal or has already completed/rejected it."},
                status=status.HTTP_400_BAD_REQUEST
            )

        # Check for duplicate feedback
        '''if ReviewFeedback.objects.filter(journal=journal, reviewer=reviewer).exists():
            return Response(
                {"error": "Feedback has already been submitted for this journal."},
                status=status.HTTP_400_BAD_REQUEST
            )'''

        # Inject journal and reviewer IDs
        data = request.data.copy()
        data['journal'] = journal.id
        data['reviewer'] = reviewer.id

        serializer = ReviewFeedbackSerializer(data=data)
        if serializer.is_valid():
            serializer.save()

            # Update assignment status to completed
            assignment = ReviewerAssignmentHistory.objects.get(journal=journal, reviewer=reviewer, status='assigned')
            assignment.status = 'completed'
            assignment.completed_date = timezone.now()
            assignment.save()

            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class ReviewerDetailAPIView(APIView):  # Endpoint to get full details of a specific reviewer
    def get(self, request, reviewer_id):
        try:
            reviewer = Reviewer.objects.get(id=reviewer_id)
        except Reviewer.DoesNotExist:
            return Response({'error': 'Reviewer not found'}, status=status.HTTP_404_NOT_FOUND)

        serializer = FullReviewerDetailSerializer(reviewer)
        return Response(serializer.data, status=status.HTTP_200_OK)

class ApprovedReviewerListAPIView(ListAPIView): #end point to get list of approved reviewers
    queryset = Reviewer.objects.filter(is_approved=True)
    serializer_class = FullReviewerDetailSerializer

class UnApprovedReviewerListAPIView(ListAPIView): #end point to get list of unapproved reviewers
    queryset = Reviewer.objects.filter(is_approved=False)
    serializer_class = FullReviewerDetailSerializer

class ReviewerAssignmentHistoryListView(generics.ListAPIView):
    """
    API endpoint to get all reviewer assignment history with reviewer details
    Includes:
    - Basic assignment info (journal_id, reviewer_id, dates, status)
    - Reviewer details (name, email, phone)
    """
    serializer_class = ReviewerAssignmentHistorySerializer
    queryset = ReviewerAssignmentHistory.objects.select_related(
        'reviewer__user',
        'subject_area'
    ).order_by('-assigned_date')

    def get_queryset(self):
        # You can add additional filtering here if needed
        return super().get_queryset()
    
# views.py
from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status
from .models import ReviewFeedback
from .serializers import ReviewFeedbackSerializer

@api_view(['GET'])
def review_feedback_by_journal(request, journal_id): #end point to get feedback of the reviewer by the journal id
    feedbacks = ReviewFeedback.objects.filter(journal_id=journal_id)
    if not feedbacks.exists():
        return Response({"detail": "No feedback found for this journal."}, status=status.HTTP_404_NOT_FOUND)
    
    serializer = ReviewFeedbackSerializer(feedbacks, many=True)
    return Response(serializer.data, status=status.HTTP_200_OK)

from rest_framework.generics import ListAPIView
from rest_framework.permissions import IsAuthenticated
from .models import ReviewerAssignmentHistory
from .serializers import ReviewerJournalAssignmentSerializer

class ReviewerJournalAssignmentListView(ListAPIView): 
    serializer_class = ReviewerJournalAssignmentSerializer
    # permission_classes = [IsAuthenticated]  # optional based on your needs

    def get_queryset(self):
        reviewer_id = self.kwargs.get('reviewer_id')
        return ReviewerAssignmentHistory.objects.filter(reviewer_id=reviewer_id)

class ValidateReviewerTokenView(APIView):
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated]

    def get(self, request):
        try:
            user = request.user
            reviewer = Reviewer.objects.get(user=user)
            
            return Response({
                'reviewer_id': reviewer.id,
                'username': user.username,
                'email': user.email,
                'first_name': user.first_name,
                'last_name': user.last_name,
                'is_approved': reviewer.is_approved,
                'token': str(request.auth)
            }, status=status.HTTP_200_OK)
            
        except Reviewer.DoesNotExist:
            return Response(
                {'error': 'No active reviewer account found'},
                status=status.HTTP_404_NOT_FOUND
            )
        except Exception as e:
            return Response(
                {'error': str(e)},
                status=status.HTTP_400_BAD_REQUEST
            )