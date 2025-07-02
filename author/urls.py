# author/urls.py
from django.urls import path
from .views import *

urlpatterns = [
    path('register/', AuthorRegisterView.as_view(), name='author-register'), #end point to register
    path('login/', AuthorLoginView.as_view(), name='author-login'), #end point to login
    path('update/<int:pk>/', AuthorUpdateView.as_view(), name='author-update'), #end point to update author profile
    path('all/', AuthorListView.as_view(), name='author-list'), #end point to list all author
    path('detail/<int:id>/', AuthorDetailView.as_view(), name='author-detail'), #end point to get author details based on the id
    path('delete/<int:id>/', AuthorDeleteView.as_view(), name='author-delete'),
    path('validate-token/', ValidateTokenView.as_view(), name='validate-token'),
]
