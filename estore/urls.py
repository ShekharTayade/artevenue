"""estore URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/2.1/topics/http/urls/
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
from django.conf.urls import include, url

from django.urls import path

from rest_framework import routers
from artevenue.views import api_views

router = routers.DefaultRouter()
router.register(r'homelane', api_views.Homelane_dataViewSet)

urlpatterns = [
    url(r'^admin/', admin.site.urls),
    url('^', include('artevenue.urls')),
    url('^', include('artist.urls')),
	url('^', include('review.urls')),
	url(r'', include('webmaster_verification.urls')),
    path('', include(router.urls)),
    path('api-auth/', include('rest_framework.urls', namespace='rest_framework')),
	
	url(r'^tinymce/', include('tinymce.urls')),
    url('^', include('blog.urls')),
]
