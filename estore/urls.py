from django.contrib import admin
from django.conf.urls import include, url

from django.urls import path

from rest_framework import routers
from artevenue.views import api_views

router = routers.DefaultRouter()
router.register(r'homelane', api_views.Homelane_dataViewSet)

urlpatterns = [
    url(r'^admin/', admin.site.urls),
    url('^', include('artevenue.urls')),
    url('^', include('artist.urls')),
	url('^', include('review.urls')),
    url('^', include('gallerywalls.urls')),
    url('^', include('returns.urls')),
    url('^', include('av_products.urls')),
    url('^', include('spinwheel.urls')),
	url(r'', include('webmaster_verification.urls')),
    path('', include(router.urls)),
    path('api-auth/', include('rest_framework.urls', namespace='rest_framework')),
	
	url(r'^tinymce/', include('tinymce.urls')),
    url('^', include('blog.urls')),	
]
