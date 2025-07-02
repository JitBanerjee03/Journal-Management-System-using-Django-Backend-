from django.conf import settings
from django.contrib.auth import authenticate, get_user_model
from django.core.mail import send_mail
from django.utils.crypto import get_random_string

from rest_framework import generics, status
from rest_framework.parsers import MultiPartParser, FormParser
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.response import Response
from rest_framework.views import APIView

from rest_framework_simplejwt.authentication import JWTAuthentication
from rest_framework_simplejwt.tokens import AccessToken
from rest_framework_simplejwt.views import TokenObtainPairView

from .models import Author
from .serializers import AuthorSerializer, UserSerializer, CustomTokenObtainPairSerializer


class AuthorRegisterView(generics.CreateAPIView): #End point to register a new author
    queryset = Author.objects.all()
    serializer_class = AuthorSerializer

'''class AuthorUpdateView(generics.UpdateAPIView): #end point to update author profile
    queryset = Author.objects.all()
    serializer_class = AuthorSerializer'''

class AuthorUpdateView(generics.UpdateAPIView): #end point to update author profile
    queryset = Author.objects.all()
    serializer_class = AuthorSerializer
    parser_classes = (MultiPartParser, FormParser)

class AuthorListView(generics.ListAPIView):  #End point to list all authors
    queryset = Author.objects.all()
    serializer_class = AuthorSerializer

'''class AuthorLoginView(APIView):  # endpoint to login author
    def post(self, request):
        email = request.data.get('email')
        password = request.data.get('password')

        try:
            user = User.objects.get(email=email)
        except User.DoesNotExist:
            return Response({'error': 'Invalid email or password'}, status=status.HTTP_400_BAD_REQUEST)

        user = authenticate(username=user.username, password=password)

        if user is not None:
            try:
                author = Author.objects.get(user=user)

                #  Get or create token
                token, _ = Token.objects.get_or_create(user=user)

                return Response({
                    'id': author.id,
                    'username': user.username,
                    'email': user.email,
                    'token': token.key  # Return the token
                }, status=status.HTTP_200_OK)
            except Author.DoesNotExist:
                return Response({'error': 'Author profile not found.'}, status=status.HTTP_404_NOT_FOUND)
        else:
            return Response({'error': 'Invalid email or password'}, status=status.HTTP_400_BAD_REQUEST)'''

class AuthorLoginView(TokenObtainPairView): # End poin to login as a author and sending a custom token as a response 
    serializer_class = CustomTokenObtainPairSerializer

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

class AuthorDetailView(generics.RetrieveAPIView): # End point to get author details based on their id
    queryset = Author.objects.all()
    serializer_class = AuthorSerializer
    lookup_field = 'id'  # Use 'id' instead of 'pk'

    def get_serializer_context(self):
        return {'request': self.request}

class AuthorDeleteView(generics.DestroyAPIView):  # End point to delete an author
    queryset = Author.objects.all()
    serializer_class = AuthorSerializer
    lookup_field = 'id'

    def delete(self, request, *args, **kwargs):
        author = self.get_object()
        user = author.user
        self.perform_destroy(author)  # Deletes the Author
        user.delete()  # Explicitly delete the associated User
        return Response({'message': 'Author and associated user deleted successfully.'}, status=status.HTTP_204_NO_CONTENT)

class ValidateTokenView(APIView):
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated]

    def get(self, request):
        try:
            # Get the user from the token
            user = request.user
            
            # Verify the user has an author profile
            author = Author.objects.get(user=user)
            
            # Create a response similar to your login endpoint
            return Response({
                'id': author.id,
                'username': user.username,
                'email': user.email,
                'first_name': user.first_name,
                'last_name': user.last_name,
                'token': str(request.auth)  # The current access token
            }, status=status.HTTP_200_OK)
            
        except Author.DoesNotExist:
            return Response(
                {'error': 'No active author account found'},
                status=status.HTTP_404_NOT_FOUND
            )
        except Exception as e:
            return Response(
                {'error': str(e)},
                status=status.HTTP_400_BAD_REQUEST
            )