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
	url(r'^cancel-return-request/$', views.cancel_return_request, name = 'cancel_return_request'),
	url(r'^get-active-return-request/$', views.get_active_return_requests, name = 'get_active_return_request'),
	path('return-request-for-update/<int:ret_id>/', views.return_request_for_update, name = 'return_request_for_update'),
	url(r'^update-return-req-status/$', views.update_return_req_status, name = 'update_return_req_status'),
	url(r'^returns-report/$', views.returns_report, name = 'returns_report'),
	url(r'^ajax/get-returns-report/$', views.get_returns_report, name='get_returns_report'),
	
]  + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

