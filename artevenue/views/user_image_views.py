from django.shortcuts import render, get_object_or_404
from django.conf import settings
from django.core.paginator import EmptyPage, PageNotAnInteger, Paginator
from django.views.decorators.csrf import csrf_protect, csrf_exempt
from django.db.models import Count
from django.contrib.auth.models import User
from django.http import JsonResponse

from datetime import datetime
import datetime
import json
import os

from artevenue.models import Ecom_site, User_image, Print_medium
from .frame_views import *

from artevenue.forms import User_imageForm
from PIL import ExifTags

today = datetime.date.today()

def user_image(request):

	# get mouldings
	mouldings = get_mouldings(request)
	paper_mouldings_apply = mouldings['paper_mouldings_apply']
	paper_mouldings_show = mouldings['paper_mouldings_show']

	
	# get mounts
	mounts = get_mounts(request)

	# get arylics
	acrylics = get_acrylics(request)

	# get boards
	boards = get_boards(request)

	# get Stretches
	stretches = get_stretches(request)

	printmedium = Print_medium.objects.all()

	
	if request.user.is_authenticated:
		user = User.objects.get(username = request.user)
		user_instance = User_image.objects.filter(user = user, status = "INI").first()
	else:
		session_id = request.session.session_key
		user_instance = User_image.objects.filter(session_id = session_id, status = "INI").first()

	# If user uploaded image is not found then display the default image in frames
	if not user_instance:
		user_instance = User_image.objects.filter(status = "DEF").first()		

	return render(request, "artevenue/user_image.html", {'mounts':mounts,
			'mouldings_appply':paper_mouldings_apply, 
			'mouldings_show':paper_mouldings_show, 'mounts':mounts,
			'printmedium':printmedium, 'user_instance':user_instance,
			'acrylics':acrylics, 'boards':boards, 'stretches':stretches,			
			})
