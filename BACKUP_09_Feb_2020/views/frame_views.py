from django.shortcuts import render, get_object_or_404
from django.http import HttpResponse
from django.conf import settings
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_protect, csrf_exempt
from django.db import IntegrityError, DatabaseError, Error
from django.http import JsonResponse
from django.db.models import Q

from datetime import datetime
import datetime
from decimal import Decimal

from artevenue.models import Ecom_site, Mount, Moulding_image
from artevenue.models import Moulding, Acrylic, Board, Stretch


today = datetime.date.today()
ecom = get_object_or_404 (Ecom_site, store_id=settings.STORE_ID )


def show_frames(request):

		return render(request, "artevenue/show_frames.html")
		
def get_mouldings(request):

	# get frames to be applied and shown
	canvas_mouldings_apply =  Moulding_image.objects.filter(image_type__iexact = "APPLY").select_related(
		'moulding').filter((Q( moulding__applies_to="C") | Q( moulding__applies_to="B")), moulding__is_published = True ).values('image_id', 'url',
			'border_slice', 'moulding_id', 'moulding__name', 'moulding__description', 'moulding__width_inches')

	canvas_mouldings_show =  Moulding_image.objects.filter(image_type__iexact = "APPLY").select_related(
		'moulding').filter((Q( moulding__applies_to="C") | Q( moulding__applies_to="B")), moulding__is_published = True ).values('image_id', 'url',
			'border_slice', 'moulding_id', 'moulding__name', 'moulding__description', 'moulding__width_inches')
	paper_mouldings_apply =  Moulding_image.objects.filter(image_type__iexact = "APPLY").select_related(
		'moulding').filter((Q( moulding__applies_to="P") | Q( moulding__applies_to="B")), moulding__is_published = True ).values('image_id', 'url',
			'border_slice', 'moulding_id', 'moulding__name', 'moulding__description', 'moulding__width_inches')

	paper_mouldings_show =  Moulding_image.objects.filter(image_type__iexact = "APPLY").select_related(
		'moulding').filter((Q( moulding__applies_to="P") | Q( moulding__applies_to="B")), moulding__is_published = True ).values('image_id', 'url',
			'border_slice', 'moulding_id', 'moulding__name', 'moulding__description', 'moulding__width_inches')
			
	moulding_diagrams =  Moulding_image.objects.filter(image_type__iexact = "DIAGRAM").select_related(
		'moulding')
							
	return ({'canvas_mouldings_apply':canvas_mouldings_apply, 'canvas_mouldings_show':canvas_mouldings_show,
			 'paper_mouldings_apply':paper_mouldings_apply, 'paper_mouldings_show':paper_mouldings_show,
			 'moulding_diagrams':moulding_diagrams})


def get_mounts(request):

	mounts = Mount.objects.all()
	
	return (mounts)

def get_acrylics(request):

	# Currently there is only one
	acrylics = Acrylic.objects.first()
	
	return (acrylics)
	
def get_boards(request):

	# Currently there is only one
	boards = Board.objects.first()
	
	return (boards)	

def get_stretches(request):

	# Currently there is only one
	stretches = Stretch.objects.first()
	
	return (stretches)	
	

def get_moulding_price(request):
	id = request.GET.get("id", "")
	if id == "":
		return JsonResponse({"sqin_price" : "0"})
	moulding = Moulding.objects.filter(moulding_id = id).first()

	if moulding :
		return JsonResponse({"sqin_price" : moulding.price})
	else :
		return JsonResponse({"sqin_price" : "0"})

def get_moulding_price_by_id(id):	
	if id == "":
		return JsonResponse({"sqin_price" : "0"})
	moulding = Moulding.objects.filter(moulding_id = id).first()

	if moulding :
		return moulding.price
	else :
		return 0
	
def get_mount_price(request):
	id = request.GET.get("id", "")
	if id == "":
		return JsonResponse({"sqin_price" : "0"})
	mount = Mount.objects.filter(mount_id = id).first()

	if mount :
		return JsonResponse({"sqin_price" : mount.price})		
	else :
		return JsonResponse({"sqin_price" : "0"})

def get_mount_price_by_id(id):
	if id == "":
		return JsonResponse({"sqin_price" : "0"})
	mount = Mount.objects.filter(mount_id = id).first()

	if mount :
		return mount.price
	else :
		return 0
		
def get_board_price(request) :
	board = request.GET.get("id", "")
	print("board = " + board)
	if board == "":
		return JsonResponse({"sqin_price" : "0"})
	boardObj = Board.objects.filter(board_id = board).first()

	if boardObj :
		return JsonResponse({"sqin_price" : boardObj.price})
	else :
		return JsonResponse({"sqin_price" : "0"})

	
def get_board_price_by_id(id) :
	if id == "":
		return JsonResponse({"sqin_price" : "0"})
	boardObj = Board.objects.filter(board_id = id).first()

	if boardObj :
		return boardObj.price
	else :
		return Decimal(0)
	
def get_acrylic_price(request) :
	acrylic = request.GET.get("id", "")
	print("acrylic = " + acrylic)
	if acrylic == "":
		return JsonResponse({"sqin_price" : "0"})
	acrylicObj = Acrylic.objects.filter(acrylic_id = acrylic).first()
	
	if acrylicObj :
		return JsonResponse({"sqin_price" : acrylicObj.price})
	else :
		return JsonResponse({"sqin_price" : "0"})
	
def get_acrylic_price_by_id(acr_id) :
	if acr_id == "":
		return JsonResponse({"sqin_price" : "0"})
	acrylicObj = Acrylic.objects.filter(acrylic_id = acr_id).first()
	if acrylicObj :
		return acrylicObj.price
	else :
		return 0
	
	
def get_stretch_price(request) :
	stretch = request.GET.get("id", "")
	print("Stretch = " + stretch)
	if stretch == "":
		return JsonResponse({"sqin_price" : "0"})
	stretchObj = Stretch.objects.filter(stretch_id = stretch).first()

	if stretchObj :
		return JsonResponse({"sqin_price" : stretchObj.price})
	else :
		return JsonResponse({"sqin_price" : "0"})
	
def get_stretch_price_by_id(strt_id) :
	print("stretch = " + str(strt_id))
	if strt_id == "":
		return JsonResponse({"sqin_price" : "0"})
	stretchObj = Stretch.objects.filter(stretch_id = strt_id).first()

	if stretchObj :
		return stretchObj.price
	else :
		return 0


	
