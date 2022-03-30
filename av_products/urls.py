from django.urls import path
from django.conf.urls import url, include
from django.conf import settings
from django.conf.urls.static import static

from . import views

from django.contrib.auth import views as auth_views
from allauth.account.views import LoginView

urlpatterns = [
	
	url(r'^round-shaped-wall-arts/$', views.show_av_products, name='show_av_products'),
	path('round-shaped-wall-art/<int:varient_id>/', views.av_product_page, name='av_product_page'),
	url(r'^round-shaped-wall-art/$', views.av_product_page, name='av_product_page'),
	url(r'create-set-single-round-artwork/$', views.create_set_single_round_artwork, name='create_set_single_round_artwork'),
	url(r'set-single-data-round-artwork/$', views.set_single_data_round_artwork, name='set_single_data_round_artwork'),
	url(r'save-set-single-round-artwork/$', views.save_set_single_round_artwork, name='save_set_single_round_artwork'),
]  + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

