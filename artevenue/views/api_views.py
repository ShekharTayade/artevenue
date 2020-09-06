from django.contrib.auth.models import User, Group
from artevenue.models import Stock_image, Stock_image_category, Publisher, Homelane_data
from rest_framework import viewsets
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated

from django.shortcuts import render,redirect

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
	

class livspace_login(APIView):
	permission_classes = (IsAuthenticated,) 

	def get(self, request):
		content = {'message': 'Hello, Livspace!'}
		return render(request, "artevenue/estore_base.html")
		
