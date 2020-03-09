from django.contrib.auth.models import User, Group
from artevenue.models import Stock_image, Stock_image_category, Publisher, Homelane_data
from rest_framework import viewsets
from artevenue.serializers import Stock_image_categorySerializer, Homelane_dataSerializer

class Stock_image_categoryViewSet(viewsets.ModelViewSet):
    """
    API endpoint that allows Stck Images Categories to be viewed or edited.
    """
    queryset = Stock_image_category.objects.all()
    serializer_class = Stock_image_categorySerializer
	
	
class Homelane_dataViewSet(viewsets.ReadOnlyModelViewSet):
	"""
	API endpoint that allows Homelane_data viewed
	"""
	pagination_class = None
	queryset = Homelane_data.objects.all()
	serializer_class = Homelane_dataSerializer
	
