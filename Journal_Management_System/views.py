from django.http import HttpResponse
from django.shortcuts import render

def home(request):
    return HttpResponse("Hello from the backend side of the journal management system!")