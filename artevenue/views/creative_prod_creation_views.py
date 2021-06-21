from django.shortcuts import render, get_object_or_404
from django.conf import settings
from django.core.paginator import EmptyPage, PageNotAnInteger, Paginator
from django.views.decorators.csrf import csrf_protect, csrf_exempt
from django.db.models import Count, Q, F
from django.contrib.admin.views.decorators import staff_member_required
from django.http import HttpRequest

from datetime import datetime
import datetime
import json
import statistics
from PIL import Image

from artevenue.models import Ecom_site, Stock_image, Stock_image_category
from artevenue.models import Stock_collage, Print_medium, Publisher_price
from artevenue.models import Wishlist, Wishlist_item_view, Collage_stock_image, Cart_item_view

from .frame_views import *
from .image_views import *
from .price_views import *

today = datetime.date.today()
env = settings.EXEC_ENV

def create_set_single(request, set_of=1):
	
	return render(request, "artevenue/set_single_data.html", {'set_of':set_of})

	
def get_product(request, product_id):
	
	if product_id is None:
		Return("No product ID supplied")
		
	product = Stock_image.objects.filter(product_id = product_id, is_published=True).first()
	
	if not product:
		Return("No product ID not found")
		
	printmedium = Print_medium.objects.all()
	price = Publisher_price.objects.filter(print_medium_id = 'PAPER') 

	# Get image price on paper and canvas
	per_sqinch_price = get_per_sqinch_price(prod_id, 'STOCK-IMAGE')
	per_sqinch_paper = per_sqinch_price['per_sqin_paper']
	per_sqinch_canvas = per_sqinch_price['per_sqin_canvas']

	# get mouldings
	mouldings = get_mouldings(request)
	# defaul we send is for PAPER
	paper_mouldings_apply = mouldings['paper_mouldings_apply']
	paper_mouldings_show = mouldings['paper_mouldings_show']
	moulding_diagrams = mouldings['moulding_diagrams']
	canvas_mouldings_show = mouldings['canvas_mouldings_show']
	# get mounts
	mounts = get_mounts(request)

	# get arylics
	acrylics = get_acrylics(request)
	
	# get boards
	boards = get_boards(request)

	# get Stretches
	stretches = get_stretches(request)

	return render(request, "artevenue/get_product.html", {'product':product,
		'prod_categories':prod_categories, 'printmedium':printmedium, 'product_category':product_category,
		'mouldings_apply':paper_mouldings_apply, 'paper_mouldings_show':paper_mouldings_show, 
		'canvas_mouldings_show':canvas_mouldings_show, 'mounts':mounts,
		'per_sqinch_paper':per_sqinch_paper, 'per_sqinch_canvas':per_sqinch_canvas, 'acrylics':acrylics,
		'boards':boards,'stretches':stretches, 'env':settings.EXEC_ENV)
		
