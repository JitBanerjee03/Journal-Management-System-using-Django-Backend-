"""
URL configuration for Journal_Management_System project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path,include
from . import views
from django.conf.urls.static import static
from django.conf import settings

urlpatterns = [
    path('admin/', admin.site.urls),
    path('',views.home),
    path('author/', include('author.urls')),  # Include author app URLS
    path('journal/',include('journal.urls')), #include journal app URLS
    path('reviewer/',include('reviewer.urls')), #include reviewer app URLS
    path('associate-editor/',include('AssociateEditor.urls')), #include AssociateEditor app URLS
    path('area-editor/',include('AreaEditor.urls')), #include AssociateEditor app URLS
    path('editor-chief/',include('Editor_Chief.urls')), #include editor chief app URLS
    path('sso-auth/',include('sso_auth.urls')), #include sso_auth app URLS
]+ static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
