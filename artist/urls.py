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
	
	url(r'^create-artist-group/$', views.create_artist_group, name='create_artist_group'),
	url(r'^artist-signup/$', views.register_as_artist, name='artist_signup'),
	path('artist-registration-confirmation/<int:id>', views.artist_registration_confirmation, name='artist_registration_confirmation'),
	path('artist/<str:url_name>', views.artist_webpage, name='artist_webpage'),
	url(r'^artist-profile/$', views.create_artist_profile, name='artist_profile'),
	url(r'^ajax/upload-artist-photo/$', views.upload_artist_photo, name='upload_artist_photo'),
	url(r'^ajax/validate-url-name/$', views.validate_url_name, name='validate_url_name'),
	url(r'^ajax/save-artist-profile/$', views.save_artist_profile, name='save_artist_profile'),

	url(r'^product-original-art/$', views.original_art_detail, name='original_art_detail'),
	path('product-original-art/<int:prod_id>/', views.original_art_detail, name='original_art_detail'),	

	url(r'^original-art-by-category/$', views.get_original_arts, name='original_art_by_category'),
	path('original-art-by-category/<str:cat_nm>/', views.get_original_arts, name='original_art_by_category'),
	path('original-art-by-category/<str:cat_nm>/<int:page>', views.get_original_arts, name='original_art_by_category'),

	url(r'^show-all-original-art-categories/$', views.show_all_original_art_categories, name='show_all_original_art_categories'),


	url(r'^upload-art/$', views.upload_art, name='upload_art'),
	path('upload-art/<str:part_number>/', views.upload_art, name='upload_art'),

	url(r'^original-artwork-approval/$', views.original_artwork_approval, name='original_artwork_approval'),
	url(r'^ajax/set-original-artwork-approval/$', views.set_original_artwork_approval, name='set_original_artwork_approval'),
	
	url(r'^get-my-artworks/$', views.get_my_artworks, name='get_my_artworks'),
	path('delist-artwork/<str:part_number>/', views.delist_artwork, name='delist_artwork'),

	url(r'^artist-page/$', views.artist_page, name='artist_page'),
	url(r'^artist-terms/$', views.artist_terms, name='artist_terms'),

	#url(r'^original-art-by-category/$', views.get_original_arts, name='original_art_by_category'),
	#path('original-art-by-category/<int:cat_id>/', views.get_original_arts, name='original_art_by_category'),
	#path('original-art-by-category/<int:cat_id>/<int:page>', views.get_original_arts, name='original_art_by_category'),

]  + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

