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
from .image_views import *

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


@csrf_exempt
def upload_user_image(request):

	if request.method == 'POST':
	
		file = request.FILES.get('file')
		session_id = request.session.session_key
		user = None
		
		if request.user.is_authenticated:
			try:
				user = User.objects.get(username = request.user)
				user_instance = User_image.objects.filter(user = user, status = "INI").first()
			except User.DoesNotExist:
				user = None
		else:
			if session_id is None:
				request.session.create()
				session_id = request.session.session_key
			user_instance = User_image.objects.filter(session_id = session_id, status = "INI").first()

		if user_instance :
			user_img = User_image(
				product_id = user_instance.product_id,
				product_type_id = user_instance.product_type,
				user = user_instance.user,
				image_to_frame = file,
				session_id = session_id,
				created_date = user_instance.created_date,
				updated_date = today,
				status = user_instance.status
			)
						
			user_img.save()

			
			#also save a thumbnail
			
		else :
			user_img = User_image(
				product_type_id = 'USER-IMAGE',
				user = user,
				session_id = session_id,
				image_to_frame = file,
				created_date = today,
				updated_date = today,
				status = 'INI'
			)
			user_img.save()

		# Read the image
		im=Image.open(user_img.image_to_frame)
		
		# Rotate image, if orientation is not 1
		exifData = {}
		exif_data = im._getexif()
		if exif_data:
			for tag, value in exif_data.items():
				decodedTag = ExifTags.TAGS.get(tag, tag)
				exifData[decodedTag] = value		
		
			if exifData :
				if 'Orientation' in exifData:
					if exifData['Orientation'] == 6:
						im.rotate(90)
					if exifData['Orientation'] == 3:
						im.rotate(180)
					if exifData['Orientation'] == 8:
						im.rotate(270)
			
		buffered = BytesIO()
		im.save(buffered, format='JPEG')
		img_data = buffered.getvalue()
		img_str = base64.b64encode(img_data)
					
		return HttpResponse(img_str)			

	else :
		return ({'msg':'FAILURE'})

			
@csrf_exempt	
def get_user_image_id(request):


	if request.user.is_authenticated:
		user = User.objects.get(username = request.user)
		user_instance = User_image.objects.filter(user = user, status = "INI").first()
	else:
		session_id = request.session.session_key
		user_instance = User_image.objects.filter(session_id = session_id, status = "INI").first()

	user_image_id = 0
	if user_instance:
		user_image_id = user_instance.product_id
	
	return JsonResponse({'user_image_id':user_image_id})

def validateUserImageSize(request):

	if request.user.is_authenticated:
		try:
			user = User.objects.get(username = request.user)
			user_instance = User_image.objects.filter(user = user, status = "INI").first()
		except User.DoesNotExist:
			user = None
	else:
		if session_id is None:
			request.session.create()
			session_id = request.session.session_key
		user_instance = User_image.objects.filter(session_id = session_id, status = "INI").first()
		
	if user_instance is None:
		return ({})
	
	ppi = 150
		
	width = user_instance.image_to_frame.width
	height = user_instance.image_to_frame.height
	
	max_width = math.floor(width / ppi)
	max_height = math.floor(height / ppi)

	return ({'max_height':max_height, 'max_width': max_width} )	
	
	
def show_mouldings_for_user_image(request):

	print_medium = request.GET.get('print_medium', '')

	if print_medium == '' or print_medium == '0':
		return

	if not request.is_ajax():
		return

	# get mouldings
	mouldings = get_mouldings(request)
	
	if print_medium == "CANVAS":
		mouldings_apply = mouldings['canvas_mouldings_apply']
		mouldings_show = mouldings['canvas_mouldings_show']
	if print_medium == "PAPER":
		mouldings_apply = mouldings['paper_mouldings_apply']
		mouldings_show = mouldings['paper_mouldings_show']
		

	session_id = request.session.session_key
	
	if request.user.is_authenticated:
		try:
			user = User.objects.get(username = request.user)
			user_instance = User_image.objects.filter(user = user, status = "INI").first()
		except User.DoesNotExist:
			user = None
	else:
		if session_id is None:
			request.session.create()
			session_id = request.session.session_key
		user_instance = User_image.objects.filter(session_id = session_id, status = "INI").first()

	# If user uploaded image is not found then display the default image in frames
	if not user_instance:
		user_instance = User_image.objects.filter(status = "DEF").first()
		
	
	return render(request, "artevenue/mouldings_include_for_user_image.html", {
		'mouldings_apply':mouldings_apply, 'mouldings_show':mouldings_show,
		'user_instance':user_instance} )

@csrf_exempt
def remove_user_image(request):	
	user_image_id = request.POST.get('user_image_id', '')	
	
	if user_image_id:
		User_image.objects.filter(product_id = user_image_id).delete()
	
	img_str = ''
	return HttpResponse(img_str)
