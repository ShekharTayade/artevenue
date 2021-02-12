from django.urls import path
from django.conf.urls import url, include
from django.conf import settings
from django.conf.urls.static import static

from . import views

from django.contrib.auth import views as auth_views
from allauth.account.views import LoginView

urlpatterns = [
	
	url(r'^orders-returns/$', views.initiate_returns, name='initiate_returns'),
	url(r'^ajax/get-orders-for-returns/$', views.get_orders_for_returns, name='get_orders_for_returns'),
	url(r'^choose-products-for-return/$', views.choose_products_for_return, name = 'choose_products_for_return'),
	url(r'^process-returns/$', views.process_returns, name = 'process_returns'),
]  + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

