from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from .serializers import *
from rest_framework import status
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework_simplejwt.authentication import JWTAuthentication
from author.models import Author
# views.py
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from .serializers import RequestPasswordResetSerializer, VerifyOTPAndResetPasswordSerializer

class UserRegistrationAPIView(APIView):
    def post(self, request):
        serializer = UserRegistrationSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response({"detail": "User registered successfully."}, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class SSOLoginAPIView(APIView):
    def post(self, request):
        serializer = SSOLoginSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        return Response(serializer.validated_data, status=status.HTTP_200_OK)

class TokenValidationAPIView(APIView):
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated]

    def get(self, request):
        user = request.user
        roles = {}

        try:
            reviewer = Reviewer.objects.get(user=user)
            roles['reviewer_id'] = reviewer.id
        except Reviewer.DoesNotExist:
            pass

        try:
            ae = AssociateEditor.objects.get(user=user)
            roles['associate_editor_id'] = ae.id
        except AssociateEditor.DoesNotExist:
            pass

        try:
            area_editor = AreaEditor.objects.get(user=user)
            roles['area_editor_id'] = area_editor.id
            roles['is_area_editor_approved'] = area_editor.is_approved
            roles['subject_areas'] = list(area_editor.subject_areas.values('id', 'name'))
        except AreaEditor.DoesNotExist:
            pass

        try:
            eic = EditorInChief.objects.get(user=user)
            roles['eic_id'] = eic.id
            roles['is_chief_editor_approved']=eic.is_approved
        except EditorInChief.DoesNotExist:
            pass

        try:
            author = Author.objects.get(user=user)
            roles['id'] = author.id      # ✅ `id` will be Author.id
        except Author.DoesNotExist:
            pass  # If no author, no 'id' key in response

        return Response({
            'user_id': user.id,          # ✅ user_id always present
            'id': roles.get('id', None), # ✅ id = author.id if exists else null
            'email': user.email,
            'first_name': user.first_name,
            'last_name': user.last_name,
            **roles
        }, status=200)

class RequestPasswordResetOTPAPIView(APIView):
    def post(self, request):
        serializer = RequestPasswordResetSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        data = serializer.save()
        return Response(data, status=status.HTTP_200_OK)

class VerifyOTPAndResetPasswordAPIView(APIView):
    def post(self, request):
        serializer = VerifyOTPAndResetPasswordSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        data = serializer.save()
        return Response(data, status=status.HTTP_200_OK)
