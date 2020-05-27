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

	path('product-original-art/<int:prod_id>/', views.original_art_detail, name='original_art_detail'),	

	url(r'^original-art-by-category/$', views.get_original_arts, name='original_art_by_category'),
	path('original-art-by-category/<str:cat_nm>/', views.get_original_arts, name='original_art_by_category'),
	path('original-art-by-category/<str:cat_nm>/<int:page>', views.get_original_arts, name='original_art_by_category'),


	#url(r'^original-art-by-category/$', views.get_original_arts, name='original_art_by_category'),
	#path('original-art-by-category/<int:cat_id>/', views.get_original_arts, name='original_art_by_category'),
	#path('original-art-by-category/<int:cat_id>/<int:page>', views.get_original_arts, name='original_art_by_category'),

]  + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

