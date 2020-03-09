from django.urls import path
from django.conf.urls import url, include
from django.conf import settings
from django.conf.urls.static import static

from . import views

from django.contrib.auth import views as auth_views
from allauth.account.views import LoginView

from django.contrib.sitemaps.views import sitemap


urlpatterns = [
	
	#url(r'^artist_signup/$', views.register_as_artist, name='artist_signup'),
	url(r'^blog/$', views.blog, name='blog'),
	path('get-blog/<int:post_id>', views.get_blog, name='get_blog'),

]  + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

