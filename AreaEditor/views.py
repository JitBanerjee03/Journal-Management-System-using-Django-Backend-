# views.py
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status, parsers
from .serializers import *
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.authtoken.models import Token
from rest_framework import generics, permissions
from .models import AreaEditor
from django.core.mail import send_mail
from django.conf import settings
from rest_framework.permissions import IsAuthenticated
from rest_framework.exceptions import NotFound
from journal.models import SubjectArea
from rest_framework.authtoken.models import Token
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.exceptions import AuthenticationFailed
from django.contrib.auth.models import User
from rest_framework import generics, status
from journal.models import Journal
from .models import AreaEditor,AreaEditorJournalAssignment
from .serializers import AreaEditorJournalAssignmentSerializer
from django.shortcuts import get_object_or_404
from django.utils import timezone
from rest_framework_simplejwt.authentication import JWTAuthentication
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from .models import AreaEditor
from django.shortcuts import get_object_or_404
from rest_framework import generics, permissions
from rest_framework.exceptions import NotFound
from .models import AreaEditorRecommendation
from .serializers import AreaEditorRecommendationSerializer

class AreaEditorRegistrationView(APIView): #end point to register as a new area editor
    parser_classes = [parsers.MultiPartParser, parsers.FormParser]  # Enable file uploads

    def post(self, request):
        serializer = AreaEditorRegistrationSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response({"message": "Area Editor registered successfully."}, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

'''class LoginView(APIView):  # Endpoint for login as an Area Editor
    def post(self, request):
        serializer = LoginSerializer(data=request.data)
        if serializer.is_valid():
            user = serializer.validated_data['user']
            token, _ = Token.objects.get_or_create(user=user)

            # Get AreaEditor instance
            try:
                area_editor = AreaEditor.objects.get(user=user)
                area_editor_id = area_editor.id
            except AreaEditor.DoesNotExist:
                return Response(
                    {"error": "AreaEditor profile not found."},
                    status=status.HTTP_404_NOT_FOUND
                )

            return Response({
                'token': token.key,
                'area_editor_id': area_editor_id,
                'email': user.email,
                'name': f"{user.first_name} {user.last_name}",
            })

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)'''

'''class LoginView(APIView):  # Endpoint for login as an Area Editor
    def post(self, request):
        serializer = LoginSerializer(data=request.data)
        if serializer.is_valid():
            user = serializer.validated_data['user']
            token, _ = Token.objects.get_or_create(user=user)

            # Get AreaEditor instance
            try:
                area_editor = AreaEditor.objects.get(user=user)
                area_editor_id = area_editor.id

                # Get Subject Areas
                subject_areas = area_editor.subject_areas.all()
                subject_area_list = [
                    {
                        'id': sa.id,
                        'name': sa.name  # assuming SubjectArea has a 'name' field
                    } for sa in subject_areas
                ]

            except AreaEditor.DoesNotExist:
                return Response(
                    {"error": "AreaEditor profile not found."},
                    status=status.HTTP_404_NOT_FOUND
                )

            return Response({
                'token': token.key,
                'area_editor_id': area_editor_id,
                'email': user.email,
                'name': f"{user.first_name} {user.last_name}",
                'subject_areas': subject_area_list,
            })

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)'''

from rest_framework_simplejwt.views import TokenObtainPairView

class LoginView(TokenObtainPairView):
    serializer_class = AreaEditorTokenObtainPairSerializer

    def post(self, request, *args, **kwargs):
        # Ensure email and password are provided
        if 'email' not in request.data or 'password' not in request.data:
            return Response(
                {'error': 'Both email and password are required'},
                status=status.HTTP_400_BAD_REQUEST
            )

        # Create a copy of the request data to avoid modifying the original
        data = request.data.copy()
        # Add username field expected by parent class
        data['username'] = data['email']
        
        try:
            response = super().post(request, *args, **kwargs)
            return Response(response.data, status=response.status_code)
        except Exception as e:
            return Response(
                {'error': str(e)},
                status=status.HTTP_400_BAD_REQUEST
            )

class AreaEditorUpdateByIdView(generics.RetrieveUpdateAPIView): #end point to update the details of a particular area editor
    queryset = AreaEditor.objects.all()
    serializer_class = AreaEditorUpdateSerializer
    #permission_classes = [permissions.IsAuthenticated]
    lookup_field = 'pk'  # This is the default, so you can omit this line

class AreaEditorListView(generics.ListAPIView): #end point to get the deatils of all the area editors
    queryset = AreaEditor.objects.all()
    serializer_class = AreaEditorListSerializer
    #permission_classes = [permissions.IsAuthenticated]  # Optional for frontend access

class AreaEditorDetailView(generics.RetrieveAPIView): #end point to get the deatils of a particular area editor
    queryset = AreaEditor.objects.all()
    serializer_class = AreaEditorDetailSerializer
    #permission_classes = [permissions.IsAuthenticated]
    lookup_field = 'pk'  # Lookup by the 'id' parameter in the URL

class ApproveAreaEditorView(APIView): #end point to approve a particular area editor
    #permission_classes = [IsAuthenticated]  # Ensure only authenticated users can approve

    def patch(self, request, pk):
        try:
            area_editor = AreaEditor.objects.get(pk=pk)
        except AreaEditor.DoesNotExist:
            raise NotFound(detail="Area Editor not found")

        # Update the is_approved field
        serializer = AreaEditorApprovalSerializer(area_editor, data={'is_approved': True}, partial=True)
        if serializer.is_valid():
            area_editor = serializer.save()

            # Send email to the Area Editor
            subject = "Congratulations! You are approved as an Area Editor"
            message = f"Dear {area_editor.user.first_name} {area_editor.user.last_name},\n\n" \
                      "We are pleased to inform you that you have been approved as an Area Editor. Congratulations on this achievement! " \
                      "We are looking forward to your contributions.\n\nBest Regards,\nThe Editorial Team"
            recipient_email = area_editor.user.email

            send_mail(
                subject,
                message,
                settings.DEFAULT_FROM_EMAIL,  # Sender email
                [recipient_email],  # Recipient email
                fail_silently=False,
            )

            return Response({"message": "Area Editor approved successfully and email sent."}, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class ApprovedAreaEditorListView(generics.ListAPIView): #end point to get the details of all the approved area editors
    queryset = AreaEditor.objects.filter(is_approved=True)
    serializer_class = AreaEditorDetailSerializer

class AssignJournalToAreaEditorAPIView(generics.CreateAPIView):
    serializer_class = AreaEditorJournalAssignmentSerializer

    def create(self, request, *args, **kwargs):
        journal_id = self.kwargs.get('journal_id')
        area_editor_id = self.kwargs.get('area_editor_id')

        journal = get_object_or_404(Journal, id=journal_id)
        area_editor = get_object_or_404(AreaEditor, id=area_editor_id)

        # Check if assignment already exists
        if AreaEditorJournalAssignment.objects.filter(journal=journal, area_editor=area_editor).exists():
            return Response({'detail': 'Journal already assigned to this Area Editor.'}, status=status.HTTP_400_BAD_REQUEST)

        assignment = AreaEditorJournalAssignment(journal=journal, area_editor=area_editor)
        assignment.save()

        serializer = self.get_serializer(assignment)
        return Response(serializer.data, status=status.HTTP_201_CREATED)

class JournalAssignmentsByAreaEditorView(generics.ListAPIView): #end point to get the list of all journal assignments for a particular area editor
    serializer_class = AreaEditorJournalAssignmentSerializer

    def get_queryset(self):
        area_editor_id = self.kwargs.get('area_editor_id')
        return AreaEditorJournalAssignment.objects.filter(area_editor__id=area_editor_id)

class SubmitAreaEditorRecommendationView(APIView):
    #permission_classes = [IsAuthenticated]

    def post(self, request, journal_id, area_editor_id):
        try:
            journal = Journal.objects.get(pk=journal_id)
            area_editor = AreaEditor.objects.get(pk=area_editor_id)
        except (Journal.DoesNotExist, AreaEditor.DoesNotExist):
            return Response({"detail": "Invalid journal or area editor ID."}, status=status.HTTP_404_NOT_FOUND)

        '''if AreaEditorRecommendation.objects.filter(journal=journal, area_editor=area_editor).exists():
            return Response({"detail": "Recommendation already submitted."}, status=status.HTTP_400_BAD_REQUEST)'''

        serializer = AreaEditorRecommendationSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save(journal=journal, area_editor=area_editor)
            return Response(serializer.data, status=status.HTTP_201_CREATED)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class SetAreaEditorAssignmentToCompletedView(APIView): #end point to change the status of the journal assignment to completed
    # No authentication required
    #authentication_classes = []
    #permission_classes = []

    def patch(self, request, journal_id, area_editor_id):
        try:
            # Get the assignment without user verification
            assignment = AreaEditorJournalAssignment.objects.get(
                journal_id=journal_id,
                area_editor_id=area_editor_id
            )
        except AreaEditorJournalAssignment.DoesNotExist:
            return Response(
                {"detail": "Assignment not found."},
                status=status.HTTP_404_NOT_FOUND
            )

        if assignment.status == 'completed':
            return Response(
                {"detail": "Assignment already completed."},
                status=status.HTTP_400_BAD_REQUEST
            )

        assignment.status = 'completed'
        assignment.completed_date = timezone.now()
        assignment.save()

        serializer = AreaEditorJournalAssignmentSerializer(assignment)
        return Response(serializer.data, status=status.HTTP_200_OK)
    
class SetAreaEditorAssignmentToInProgressView(APIView): #end point to change the status of the journal assignment to in progress
    # No authentication required
    #authentication_classes = []
    #permission_classes = []

    def patch(self, request, journal_id, area_editor_id):
        try:
            assignment = AreaEditorJournalAssignment.objects.get(
                journal=journal_id,
                area_editor=area_editor_id
                
            )
        except AreaEditorJournalAssignment.DoesNotExist:
            return Response(
                {"detail": "Assignment not found."},
                status=status.HTTP_404_NOT_FOUND
            )

        if assignment.status == 'in_progress':
            return Response(
                {"detail": "Assignment already in progress."},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        if assignment.status == 'completed':
            return Response(
                {"detail": "Cannot change status from completed to in_progress."},
                status=status.HTTP_400_BAD_REQUEST
            )

        assignment.status = 'in_progress'
        assignment.save()

        serializer = AreaEditorJournalAssignmentSerializer(assignment)
        return Response(serializer.data, status=status.HTTP_200_OK)
    
class ValidateAreaEditorTokenView(APIView):
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated]

    def get(self, request):
        try:
            # Get the user from the token
            user = request.user
            
            # Verify the user has an area editor profile
            area_editor = AreaEditor.objects.get(user=user)
            
            # Get subject areas
            subject_areas = area_editor.subject_areas.all()
            subject_area_list = [{'id': sa.id, 'name': sa.name} for sa in subject_areas]

            # Create a response similar to your login endpoint
            return Response({
                'area_editor_id': area_editor.id,
                'username': user.username,
                'email': user.email,
                'first_name': user.first_name,
                'last_name': user.last_name,
                'is_approved': area_editor.is_approved,
                'subject_areas': subject_area_list,
                'token': str(request.auth)  # The current access token
            }, status=status.HTTP_200_OK)
            
        except AreaEditor.DoesNotExist:
            return Response(
                {'error': 'No active area editor account found'},
                status=status.HTTP_404_NOT_FOUND
            )
        except Exception as e:
            return Response(
                {'error': str(e)},
                status=status.HTTP_400_BAD_REQUEST
            )

class JournalRecommendationsListView(generics.ListAPIView):
    serializer_class = AreaEditorRecommendationSerializer
    
    def get_queryset(self):
        journal_id = self.kwargs['journal_id']
        return AreaEditorRecommendation.objects.filter(journal_id=journal_id)
    
class AreaEditorApprovalStatusView(APIView):
    def get(self, request, area_editor_id):
        area_editor = get_object_or_404(AreaEditor, id=area_editor_id)
        return Response({
            'area_editor_id': area_editor.id,
            'full_name': area_editor.user.get_full_name(),
            'email': area_editor.user.email,
            'is_approved': area_editor.is_approved
        }, status=status.HTTP_200_OK)

class AreaEditorRecommendationsByJournalView(generics.ListAPIView):
    serializer_class = AreaEditorRecommendationSerializer
    #permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        journal_id = self.kwargs.get('journal_id')
        queryset = AreaEditorRecommendation.objects.filter(journal__id=journal_id)

        if not queryset.exists():
            raise NotFound("No recommendations found for this journal.")

        return queryset
