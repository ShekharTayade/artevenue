from django.urls import path
from django.conf.urls import url, include
from django.conf import settings
from django.conf.urls.static import static

from . import views

from django.contrib.auth import views as auth_views
from allauth.account.views import LoginView

urlpatterns = [
	
	url(r'^write-customer-review/$', views.write_customer_review, name='write_customer_review'),
	path('write-customer-review/<int:prod_id>/<str:prod_type>/', views.write_customer_review, name='write_customer_review'),
	path('customer-review/<int:review_id>/', views.customer_review_one, name='customer_review_one'),
	url(r'^ajax/upload-photo/$', views.upload_photo, name='upload_photo'),
	url(r'^all-customer-reviews/$', views.all_customer_reviews, name='all_customer_reviews'),
	
]  + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

