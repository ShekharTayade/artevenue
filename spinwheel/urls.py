from django.urls import path
from django.conf.urls import url, include
from django.conf import settings
from django.conf.urls.static import static

from . import views

from django.contrib.auth import views as auth_views
from allauth.account.views import LoginView

urlpatterns = [
	
	url(r'^spin-wheel/$', views.spin_wheel, name='spin_wheel'),
	url(r'^ajax/set_prize/$', views.set_prize, name='set_prize'),
		
	
]  + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

