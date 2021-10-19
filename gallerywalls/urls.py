from django.urls import path
from django.conf.urls import url, include
from django.conf import settings
from django.conf.urls.static import static

from . import views

from django.contrib.auth import views as auth_views
from allauth.account.views import LoginView

urlpatterns = [
	
	url(r'^gallery-walls/$', views.get_gallery_walls, name='get_gallery_walls'),
	path('gallery-wall/<int:gallery_id>/', views.gallery_wall_detail, name='gallery_wall_detail'),
	url(r'^ajax/gallery-wall-detail-items/$', views.gallery_wall_detail_items, name='gallery_wall_detail_items'),
	url(r'^ajax/get-gallery-variation-and-price/$', views.get_gallery_variation_and_price, name='get_gallery_variation_and_price'),
	url(r'^ajax/add-gallery-wall-to-cart/$', views.add_gallery_wall_to_cart, name='add_gallery_wall_to_cart'),

	url(r'^create-gallery-wall/$', views.create_gallery_wall, name='create_gallery_wall'),
	url(r'^create-gw-data/$', views.create_gw_data, name='create_gw_data'),
	url(r'^ajax/save-new-gallery_wall/$', views.save_gw, name='save_gw'),
	
]  + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

