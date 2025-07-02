from rest_framework.generics import CreateAPIView,RetrieveUpdateAPIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.views import APIView
from rest_framework.permissions import IsAdminUser
from rest_framework.authtoken.models import Token
from django.contrib.auth import authenticate
from .models import EditorInChief
from .serializers import *
from django.conf import settings
# views.py
from rest_framework.permissions import IsAuthenticated
# Editor_Chief/views.py
from rest_framework.generics import ListAPIView
from rest_framework.permissions import IsAdminUser
from .models import EditorInChief
from .serializers import EditorInChiefListSerializer  # You'll need to create this
# views.py
from rest_framework.generics import RetrieveAPIView
from rest_framework.permissions import IsAuthenticated
from rest_framework.exceptions import PermissionDenied
from django.http import Http404
from rest_framework.generics import RetrieveAPIView
from rest_framework import serializers
from rest_framework.decorators import api_view

class EditorInChiefRegistrationView(CreateAPIView): #end point to registration
    serializer_class = EditorInChiefRegistrationSerializer

    def perform_create(self, serializer):
        instance = serializer.save()
        if settings.DEBUG:
            print(f"New EIC registered: {instance.user.email}")

    def create(self, request, *args, **kwargs):
        response = super().create(request, *args, **kwargs)
        return Response(
            {
                "message": "Registration successful. Pending admin approval.",
                "is_approved": False
            },
            status=status.HTTP_201_CREATED
        )

class ApproveEditorInChiefView(APIView): #end point to approve the editor in chief
    permission_classes = [IsAdminUser]
    
    def post(self, request, eic_id):
        try:
            eic = EditorInChief.objects.get(id=eic_id)
        except EditorInChief.DoesNotExist:
            return Response({"error": "Editor-in-Chief not found"}, status=status.HTTP_404_NOT_FOUND)
        
        if eic.is_approved:
            return Response({"message": "Already approved"}, status=status.HTTP_200_OK)
        
        eic.is_approved = True
        eic.save()
        
        if settings.DEBUG:
            print(f"EIC approved: {eic.user.email}")
        
        return Response({"message": "Approved successfully"}, status=status.HTTP_200_OK)

'''class EditorInChiefLoginView(APIView): #end point to login
    def post(self, request):
        email = request.data.get('email')
        password = request.data.get('password')

        if not email or not password:
            return Response(
                {'error': 'Both email and password are required'},
                status=status.HTTP_400_BAD_REQUEST
            )

        user = authenticate(username=email, password=password)
        if not user:
            return Response(
                {'error': 'Invalid credentials'},
                status=status.HTTP_401_UNAUTHORIZED
            )

        try:
            editor_in_chief = EditorInChief.objects.get(user=user)
            "if not editor_in_chief.is_approved:
                return Response(
                    {'error': 'Account pending approval', 'is_approved': False},
                    status=status.HTTP_403_FORBIDDEN
                )
            if not editor_in_chief.is_active:
                return Response(
                    {'error': 'Account deactivated'},
                    status=status.HTTP_403_FORBIDDEN
                )
        except EditorInChief.DoesNotExist:
            return Response(
                {'error': 'No Editor-in-Chief account found'},
                status=status.HTTP_403_FORBIDDEN
            )

        token, created = Token.objects.get_or_create(user=user)
        return Response({
            'token': token.key,
            'user_id': user.id,
            'eic_id': editor_in_chief.id,
            'email': user.email,
            'full_name': user.get_full_name(),
            'is_approved': editor_in_chief.is_approved,
            'profile_picture': request.build_absolute_uri(
                editor_in_chief.profile_picture.url
            ) if editor_in_chief.profile_picture else None
        }, status=status.HTTP_200_OK)'''

from rest_framework_simplejwt.views import TokenObtainPairView

class EditorInChiefLoginView(TokenObtainPairView):
    serializer_class = EditorInChiefTokenObtainPairSerializer

    def post(self, request, *args, **kwargs):
        # Ensure email and password are provided
        if 'email' not in request.data or 'password' not in request.data:
            return Response(
                {'error': 'Both email and password are required'},
                status=status.HTTP_400_BAD_REQUEST
            )

        try:
            # Create a copy of the request data
            data = request.data.copy()
            data['username'] = data['email']  # Map email to username field
            
            # Set the request in the serializer context for URL building
            serializer = self.get_serializer(data=data, context={'request': request})
            serializer.is_valid(raise_exception=True)
            
            return Response(serializer.validated_data, status=status.HTTP_200_OK)
            
        except serializers.ValidationError as e:
            return Response(
                {'error': str(e.detail)},
                status=status.HTTP_400_BAD_REQUEST
            )
        except Exception as e:
            return Response(
                {'error': 'Login failed. Please try again.'},
                status=status.HTTP_400_BAD_REQUEST
            )

class EditorInChiefListView(ListAPIView): #end point to get all the editor in chief details
    """
    View to list all Editor-in-Chief profiles
    Accessible only by admin users
    """
    serializer_class = EditorInChiefListSerializer
    #permission_classes = [IsAdminUser]
    queryset = EditorInChief.objects.all().select_related('user')
    
    def get_queryset(self):
        queryset = super().get_queryset()
        
        # Optional filtering by approval status
        is_approved = self.request.query_params.get('is_approved')
        if is_approved in ['true', 'false']:
            queryset = queryset.filter(is_approved=is_approved.lower() == 'true')
            
        return queryset

class EditorInChiefUpdateView(RetrieveUpdateAPIView): #end point to update a particular chief editor
    serializer_class = EditorInChiefUpdateSerializer
    #permission_classes = [IsAuthenticated]
    queryset = EditorInChief.objects.all()
    lookup_field = 'id'  # This tells DRF to look for 'id' in URL
    
    def get_object(self):
        # Get the EIC object from URL parameter
        eic = super().get_object()
        
        # Check if the requesting user is either:
        # 1. The EIC themselves OR
        # 2. An admin user
        '''if not (self.request.user == eic.user or self.request.user.is_staff):
            raise PermissionDenied("You don't have permission to edit this profile")'''
            
        return eic

    def perform_update(self, serializer):
        instance = serializer.save()
        if settings.DEBUG:
            print(f"EIC profile updated: {instance.user.email}")
 
class EditorInChiefDetailView(RetrieveAPIView): #end point to get all the details of a particular chief editor
    """
    Public endpoint to view any Editor-in-Chief's details
    No authentication or permission required
    """
    serializer_class = EditorInChiefDetailSerializer
    queryset = EditorInChief.objects.all().select_related('user')
    lookup_field = 'id'

from rest_framework_simplejwt.authentication import JWTAuthentication
from rest_framework.permissions import IsAuthenticated

class ValidateEditorInChiefTokenView(APIView):
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated]

    def get(self, request):
        try:
            user = request.user
            editor_in_chief = EditorInChief.objects.get(user=user)
            
            # Build profile picture URL if exists
            profile_picture = None
            if editor_in_chief.profile_picture and hasattr(editor_in_chief.profile_picture, 'url'):
                profile_picture = request.build_absolute_uri(editor_in_chief.profile_picture.url)
            
            return Response({
                'token': str(request.auth),
                'user_id': user.id,
                'eic_id': editor_in_chief.id,
                'email': user.email,
                'full_name': user.get_full_name(),
                'is_approved': editor_in_chief.is_approved,
                'profile_picture': profile_picture,
                # Include any additional fields
                'institution': editor_in_chief.institution,
                'position_title': editor_in_chief.position_title,
                'country': editor_in_chief.country
            }, status=status.HTTP_200_OK)
            
        except EditorInChief.DoesNotExist:
            return Response(
                {'error': 'No active Editor-in-Chief account found'},
                status=status.HTTP_404_NOT_FOUND
            )
        except Exception as e:
            return Response(
                {'error': str(e)},
                status=status.HTTP_400_BAD_REQUEST
            )
        
from rest_framework import generics, permissions, status
from rest_framework.response import Response
from .models import EditorInChiefRecommendation

from .serializers import (
    EditorInChiefRecommendationSerializer,
    CreateRecommendationSerializer,
    UpdateRecommendationSerializer
)

'''class EditorInChiefRecommendationListView(generics.ListAPIView):
    serializer_class = EditorInChiefRecommendationSerializer
    permission_classes = []
    
    def get_queryset(self):
        return EditorInChiefRecommendation.objects.filter(
            editor_in_chief=self.request.user.editorinchief
        ).select_related('journal', 'editor_in_chief__user')'''

class EditorInChiefRecommendationListView(generics.ListAPIView):
    serializer_class = EditorInChiefRecommendationSerializer
    permission_classes = []  # No authentication
    queryset = EditorInChiefRecommendation.objects.all().select_related(
        'journal', 'editor_in_chief__user'
    )

    # Remove get_queryset (no user filtering)

'''class CreateRecommendationView(generics.CreateAPIView):
    serializer_class = CreateRecommendationSerializer
    permission_classes = []
    
    def perform_create(self, serializer):
        serializer.save(editor_in_chief=self.request.user.editorinchief)'''

'''class CreateRecommendationView(generics.CreateAPIView):
    serializer_class = CreateRecommendationSerializer
    permission_classes = []
    
    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        # Additional validation for final decisions
        if serializer.validated_data.get('is_final_decision', False):
            if not serializer.validated_data.get('decision_summary'):
                return Response(
                    {"error": "Decision summary is required for final decisions"},
                    status=status.HTTP_400_BAD_REQUEST
                )
        
        self.perform_create(serializer)
        headers = self.get_success_headers(serializer.data)
        
        # Include the full recommendation data in the response
        response_data = EditorInChiefRecommendationSerializer(
            instance=serializer.instance,
            context=self.get_serializer_context()
        ).data
        
        return Response(
            response_data,
            status=status.HTTP_201_CREATED,
            headers=headers
        )'''

from rest_framework import generics, status
from rest_framework.response import Response
from django.http import Http404

class CreateRecommendationView(generics.CreateAPIView):
    """
    Endpoint that can both create AND update recommendations
    URL: /editor-chief/recommendations/create/
    Method: POST (works for both create and update)
    """
    serializer_class = CreateRecommendationSerializer
    permission_classes = []

    def post(self, request, *args, **kwargs):
        journal_id = request.data.get('journal')
        eic_id = request.data.get('editor_in_chief')
        
        instance = None  # Initialize instance variable
        serializer = None  # Initialize serializer variable
        
        # Try to find existing recommendation
        try:
            instance = EditorInChiefRecommendation.objects.get(
                journal_id=journal_id,
                editor_in_chief_id=eic_id
            )
            # If exists - update it
            serializer = UpdateRecommendationSerializer(
                instance, 
                data=request.data, 
                partial=True
            )
        except EditorInChiefRecommendation.DoesNotExist:
            # If doesn't exist - create new
            serializer = self.get_serializer(data=request.data)
        
        serializer.is_valid(raise_exception=True)
        
        # Handle final decision validation
        if serializer.validated_data.get('is_final_decision', False):
            if not serializer.validated_data.get('decision_summary'):
                return Response(
                    {"error": "Decision summary is required for final decisions"},
                    status=status.HTTP_400_BAD_REQUEST
                )
        
        # Save or update the instance
        serializer.save()
        
        # Return full recommendation data
        response_data = EditorInChiefRecommendationSerializer(
            instance=serializer.instance,
            context=self.get_serializer_context()
        ).data
        
        status_code = status.HTTP_200_OK if instance else status.HTTP_201_CREATED
        return Response(response_data, status=status_code)

class RecommendationDetailView(generics.RetrieveUpdateDestroyAPIView):
    queryset = EditorInChiefRecommendation.objects.all()
    permission_classes = []
    
    def get_serializer_class(self):
        if self.request.method in ['PUT', 'PATCH']:
            return UpdateRecommendationSerializer
        return EditorInChiefRecommendationSerializer
        
    def get_queryset(self):
        return self.queryset.filter(editor_in_chief=self.request.user.editorinchief)

'''class FinalizeRecommendationView(generics.UpdateAPIView):
    queryset = EditorInChiefRecommendation.objects.all()
    serializer_class = UpdateRecommendationSerializer
    permission_classes = []
    
    def patch(self, request, *args, **kwargs):
        instance = self.get_object()
        serializer = self.get_serializer(instance, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        
        if not instance.is_final_decision and serializer.validated_data.get('is_final_decision', False):
            # Additional logic when finalizing decision
            pass
            
        self.perform_update(serializer)
        return Response(serializer.data)'''

class FinalizeRecommendationView(APIView):
    def post(self, request, journal_id):
        try:
            # Get editor_in_chief_id from request body
            editor_in_chief_id = request.data.get('editor_in_chief_id')
            if not editor_in_chief_id:
                return Response(
                    {"error": "editor_in_chief_id is required"}, 
                    status=status.HTTP_400_BAD_REQUEST
                )

            # Get the specific recommendation for this journal and editor
            recommendation = EditorInChiefRecommendation.objects.get(
                journal_id=journal_id,
                editor_in_chief_id=editor_in_chief_id
            )
        except EditorInChiefRecommendation.DoesNotExist:
            return Response(
                {"error": "Recommendation not found for this journal and editor"}, 
                status=status.HTTP_404_NOT_FOUND
            )

        serializer = UpdateRecommendationSerializer(
            recommendation, 
            data=request.data, 
            partial=True
        )
        
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
class EditorInChiefRecommendationDetailView(RetrieveAPIView):
    """
    Endpoint to get details of a specific editor-in-chief recommendation
    Example URL: /editor-chief/recommendations/<journal_id>/<eic_id>/
    """
    serializer_class = EditorInChiefRecommendationDetailSerializer
    permission_classes = []  # Adjust permissions as needed
    
    def get_object(self):
        journal_id = self.kwargs.get('journal_id')
        eic_id = self.kwargs.get('eic_id')
        
        try:
            return EditorInChiefRecommendation.objects.get(
                journal_id=journal_id,
                editor_in_chief_id=eic_id
            )
        except EditorInChiefRecommendation.DoesNotExist:
            raise Http404("No recommendation found for this journal and editor")
        
@api_view(['GET'])
def get_editor_in_chief_approval_status(request, editor_in_chief_id):
    try:
        eic = EditorInChief.objects.get(id=editor_in_chief_id)
        return Response({'is_approved': eic.is_approved}, status=status.HTTP_200_OK)
    except EditorInChief.DoesNotExist:
        return Response({'error': 'EditorInChief not found'}, status=status.HTTP_404_NOT_FOUND)
    
from rest_framework import generics, permissions
from rest_framework.response import Response
from rest_framework.exceptions import NotFound
from .models import EditorInChiefRecommendation
from .serializers import EditorInChiefRecommendationSerializer

class RecommendationsByJournalView(generics.ListAPIView):
    serializer_class = EditorInChiefRecommendationSerializer
    #permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        journal_id = self.kwargs.get('journal_id')
        recommendations = EditorInChiefRecommendation.objects.filter(journal__id=journal_id)
        if not recommendations.exists():
            raise NotFound("No recommendations found for this journal.")
        return recommendations

