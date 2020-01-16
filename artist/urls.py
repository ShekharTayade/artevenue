from django.urls import path
from django.conf.urls import url, include
from django.conf import settings
from django.conf.urls.static import static

from . import views

from django.contrib.auth import views as auth_views
from allauth.account.views import LoginView

from django.contrib.sitemaps.views import sitemap
from artevenue.sitemaps import *
sitemaps = {
   'static': StaticSitemap(),
}


urlpatterns = [
	
	url(r'^create_artist_group/$', views.create_artist_group, name='create_artist_group'),
	url(r'^artist_signup/$', views.register_as_artist, name='artist_signup'),
	path('artist_registration_confirmation/<int:id>', views.artist_registration_confirmation, name='artist_registration_confirmation'),
	path('artist/<str:profile_name>', views.artist_webpage, name='artist_profile'),
	path('create_artist_profile/<int:id>', views.create_artist_profile, name='create_artist_profile'),

]  + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

