from rest_framework.generics import CreateAPIView
from rest_framework.response import Response
from rest_framework import status,permissions
from django.core.mail import send_mail
from django.conf import settings
from .serializers import *
from rest_framework.views import APIView
from django.contrib.auth import authenticate
from rest_framework.authtoken.models import Token
from .models import AssociateEditor
from rest_framework.generics import ListAPIView,RetrieveUpdateAPIView
from journal.models import JournalSection,Journal
from .serializers import AssociateEditorBriefSerializer
from .models import AssociateEditor, AssociateEditorRecommendation
from .serializers import AssociateEditorRecommendationSerializer
from django.shortcuts import get_object_or_404
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from .models import AssociateEditorAssignment
from .serializers import AssignedJournalSerializer
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework_simplejwt.views import TokenObtainPairView
from rest_framework_simplejwt.authentication import JWTAuthentication

class AssociateEditorRegistrationView(CreateAPIView): #end point to register a new associate editor
    serializer_class = AssociateEditorRegistrationSerializer

    def perform_create(self, serializer):
        instance = serializer.save()

        # Send confirmation email
        subject = "Registration Successful"
        message = (
            f"Dear {instance.user.first_name},\n\n"
            "Thank you for registering as an Associate Editor.\n"
            "We have received your information successfully.\n\n"
            "Best regards,\nJournal Management Team"
        )
        from_email = settings.DEFAULT_FROM_EMAIL
        recipient_list = [instance.user.email]

        send_mail(subject, message, from_email, recipient_list, fail_silently=False)

    def create(self, request, *args, **kwargs):
        response = super().create(request, *args, **kwargs)
        return Response(
            {"message": "Registration successful. Confirmation email sent."},
            status=status.HTTP_201_CREATED
        )

'''class EmailLoginView(APIView):  # Endpoint to login as an associate editor
    def post(self, request):
        email = request.data.get('email')
        password = request.data.get('password')

        if not email or not password:
            return Response({'error': 'Email and password are required.'}, status=status.HTTP_400_BAD_REQUEST)

        # Since username is email
        user = authenticate(username=email, password=password)

        if user is not None:
            try:
                associate_editor = AssociateEditor.objects.get(user=user)
            except AssociateEditor.DoesNotExist:
                return Response({'error': 'No Associate Editor profile linked to this user.'}, status=status.HTTP_404_NOT_FOUND)

            token, created = Token.objects.get_or_create(user=user)
            return Response({
                'token': token.key,
                'associate_editor_id': associate_editor.id,
                'email': user.email,
                'full_name': user.get_full_name()
            })
        else:
            return Response({'error': 'Invalid email or password.'}, status=status.HTTP_401_UNAUTHORIZED)'''

class EmailLoginView(TokenObtainPairView):
    serializer_class = AssociateEditorTokenObtainPairSerializer
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

'''class AssociateEditorDetailView(APIView):  # Endpoint to get all details of a particular associate editor 
    def get(self, request, id):
        try:
            associate_editor = AssociateEditor.objects.get(id=id)
        except AssociateEditor.DoesNotExist:
            return Response({'error': 'Associate Editor not found'}, status=status.HTTP_404_NOT_FOUND)

        serializer = AssociateEditorSerializer(associate_editor)
        return Response(serializer.data, status=status.HTTP_200_OK)'''

class AssociateEditorDetailView(APIView):
    def get(self, request, id):
        try:
            associate_editor = AssociateEditor.objects.get(id=id)
        except AssociateEditor.DoesNotExist:
            return Response({'error': 'Associate Editor not found'}, status=status.HTTP_404_NOT_FOUND)

        serializer = AssociateEditorSerializer(associate_editor)
        data = serializer.data
        data['assignment_count'] = AssociateEditorAssignment.objects.filter(associate_editor=associate_editor).count()
        data['review_count'] = AssociateEditorRecommendation.objects.filter(associate_editor=associate_editor).count()
        return Response(data, status=status.HTTP_200_OK)

class AssociateEditorListView(ListAPIView): #end point to get all the details of all the associate editor
    queryset = AssociateEditor.objects.all()
    serializer_class = AssociateEditorBriefSerializer

class AssociateEditorUpdateView(RetrieveUpdateAPIView): #end point update deatils of a particular associate editor
    queryset = AssociateEditor.objects.all()
    serializer_class = AssociateEditorUpdateSerializer
    lookup_field = 'id'  # assuming you're passing the AE's ID in the URL

class AssociateEditorsBySubjectAreaView(ListAPIView): #end point to get the list of associate editor based on the subject area
    serializer_class = AssociateEditorBriefSerializer

    def get_queryset(self):
        subject_area_id = self.kwargs['subject_area_id']
        return AssociateEditor.objects.filter(subject_areas__id=subject_area_id).distinct()

class EditorsByJournalSectionView(APIView): #end point to get the list of associate editor based on the journal area
    #permission_classes = [permissions.IsAuthenticated]  # Optional: change as needed

    def get(self, request, section_id):
        try:
            section = JournalSection.objects.get(id=section_id)
        except JournalSection.DoesNotExist:
            return Response({"detail": "Journal section not found."}, status=status.HTTP_404_NOT_FOUND)

        editors = AssociateEditor.objects.filter(journal_sections=section)
        serializer = AssociateEditorBriefSerializer(editors, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

class AssignJournalToEditorView(APIView): #end point to assign a particular journal to a particular editor
    def post(self, request, journal_id, editor_id):
        try:
            journal = Journal.objects.get(id=journal_id)
            editor = AssociateEditor.objects.get(id=editor_id)

            # Check for existing assignment
            existing = AssociateEditorAssignment.objects.filter(
                journal=journal,
                associate_editor=editor
            ).first()

            if existing:
                return Response(
                    {"detail": "This journal is already assigned to this editor."},
                    status=status.HTTP_400_BAD_REQUEST
                )

            assignment = AssociateEditorAssignment.objects.create(
                journal=journal,
                associate_editor=editor
            )

            serializer = AssociateEditorAssignmentSerializer(assignment)
            return Response(serializer.data, status=status.HTTP_201_CREATED)

        except Journal.DoesNotExist:
            return Response({"detail": "Journal not found."}, status=status.HTTP_404_NOT_FOUND)
        except AssociateEditor.DoesNotExist:
            return Response({"detail": "Editor not found."}, status=status.HTTP_404_NOT_FOUND)

class SubmitRecommendationView(APIView): #end point to post recommendation for a particular journal by a particular editor
    # permission_classes = [permissions.IsAuthenticated]

    def post(self, request, journal_id, ae_id):
        journal = get_object_or_404(Journal, id=journal_id)
        associate_editor = get_object_or_404(AssociateEditor, id=ae_id)

        # Optional: Check if the user is the same as the AE
        # if request.user != associate_editor.user:
        #     return Response({"error": "Permission denied."}, status=status.HTTP_403_FORBIDDEN)

        # Prevent duplicate recommendations
        if AssociateEditorRecommendation.objects.filter(journal=journal, associate_editor=associate_editor).exists():
            return Response({"error": "Recommendation already exists."}, status=status.HTTP_400_BAD_REQUEST)

        # Collect relevant data from the request
        data = {
            'journal': journal.id,
            'associate_editor': associate_editor.id,
            'recommendation': request.data.get('recommendation'),
            'summary': request.data.get('summary'),
            'overall_rating': request.data.get('overall_rating'),
            'justification': request.data.get('justification'),
            'public_comments_to_author': request.data.get('public_comments_to_author'),
        }

        serializer = AssociateEditorRecommendationSerializer(data=data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class JournalRecommendationsView(APIView): #end point to fetch recommendation details for a particular journal
    def get(self, request, journal_id):
        journal = get_object_or_404(Journal, id=journal_id)
        recommendations = AssociateEditorRecommendation.objects.filter(journal=journal)

        if not recommendations.exists():
            return Response({"message": "No recommendations found for this journal."}, status=status.HTTP_404_NOT_FOUND)

        serializer = AssociateEditorRecommendationSerializer(recommendations, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

class JournalsAssignedToEditorView(APIView):
    #permission_classes = [IsAuthenticated]

    def get(self, request, editor_id):
        assignments = AssociateEditorAssignment.objects.filter(associate_editor_id=editor_id).select_related(
            'journal', 'journal__corresponding_author__user'
        )
        serializer = AssignedJournalSerializer(assignments, many=True)
        return Response(serializer.data)

class SetAssignmentToReviewingView(APIView): #end point to change the status of associate editor assignment as reviewing
    def patch(self, request, journal_id, associate_editor_id):
        try:
            assignment = AssociateEditorAssignment.objects.get(
                journal_id=journal_id,
                associate_editor_id=associate_editor_id
            )
        except AssociateEditorAssignment.DoesNotExist:
            return Response({"detail": "Assignment not found."}, status=status.HTTP_404_NOT_FOUND)

        if assignment.status == 'reviewing':
            return Response({"detail": "Already in 'reviewing' status."}, status=status.HTTP_400_BAD_REQUEST)

        serializer = AssociateEditorAssignmentStatusUpdateSerializer(
            assignment, data={'status': 'reviewing'}, partial=True
        )
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

# views.py
from django.utils.timezone import now

class SetAssignmentToCompletedView(APIView):
    def patch(self, request, journal_id, associate_editor_id):
        try:
            assignment = AssociateEditorAssignment.objects.get(
                journal_id=journal_id,
                associate_editor_id=associate_editor_id
            )
        except AssociateEditorAssignment.DoesNotExist:
            return Response({"detail": "Assignment not found."}, status=status.HTTP_404_NOT_FOUND)

        if assignment.status == 'completed':
            return Response({"detail": "Already in 'completed' status."}, status=status.HTTP_400_BAD_REQUEST)

        serializer = AssociateEditorAssignmentStatusUpdateSerializer(
            assignment, data={'status': 'completed'}, partial=True
        )
        if serializer.is_valid():
            assignment.completed_date = now()  # ✅ optionally set the completion timestamp
            assignment.save()
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

from rest_framework.generics import ListAPIView
from .models import AssociateEditorAssignment
from .serializers import AssociateEditorAssignmentListSerializer

class AssociateEditorAssignmentListView(ListAPIView):
    queryset = AssociateEditorAssignment.objects.select_related(
        'journal', 'associate_editor__user', 'journal__subject_area'
    )
    serializer_class = AssociateEditorAssignmentListSerializer

class ValidateAssociateEditorTokenView(APIView):
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated]

    def get(self, request):
        try:
            user = request.user
            associate_editor = AssociateEditor.objects.get(user=user)
            
            return Response({
                'associate_editor_id': associate_editor.id,
                'username': user.username,
                'email': user.email,
                'first_name': user.first_name,
                'last_name': user.last_name,
                'is_active': associate_editor.is_active,
                'token': str(request.auth)
            }, status=status.HTTP_200_OK)
            
        except AssociateEditor.DoesNotExist:
            return Response(
                {'error': 'No active associate editor account found'},
                status=status.HTTP_404_NOT_FOUND
            )
        except Exception as e:
            return Response(
                {'error': str(e)},
                status=status.HTTP_400_BAD_REQUEST
            )