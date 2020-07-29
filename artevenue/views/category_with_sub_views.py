from django.shortcuts import render, get_object_or_404
from django.conf import settings
from django.core.paginator import EmptyPage, PageNotAnInteger, Paginator
from django.views.decorators.csrf import csrf_protect, csrf_exempt
from django.db.models import Count, Q, F, When, Case
from django.contrib.admin.views.decorators import staff_member_required

from datetime import datetime
import datetime
import json
#import imagehash
import os

from artevenue.models import Ecom_site, Stock_image, Stock_image_category
from artevenue.models import Publisher_price, Original_art_original_art_category, Original_art
from artevenue.models import Stock_image_stock_image_category, Cart_stock_image, Cart_item_view
from artevenue.models import Print_medium, Publisher_price, Promotion_stock_image, Promotion_product_view
from artevenue.models import Curated_collection, Curated_category, Promotion
from artevenue.models import Wishlist, Wishlist_item_view, Homelane_data

from .price_views import *


def category_landing_page(request, featured_ids = None):
	## Abstract
	curated_coll_id = 3
	if featured_ids:
		featured_prods = featured_ids.split(",")
		featured_prods = list(filter(None, featured_prods))  ## Remove empty elements
	else:
		featured_prods = None

	curated_coll = Curated_collection.objects.filter(curated_category_id = curated_coll_id,
			product_type_id = 'STOCK-IMAGE').values('product_id')
	try:
		product_cate = Curated_category.objects.get(category_id = curated_coll_id);
	except Curated_category.DoesNotExist:
		product_cate = {}
	products = Stock_image.objects.filter(product_id__in = curated_coll, 
		is_published = True)

	if featured_prods:
		products = products.filter(product_id__in = featured_prods)
	
	env = settings.EXEC_ENV
	prod_categories = Stock_image_category.objects.filter(store_id=settings.STORE_ID, trending = True )
	

	if curated_coll_id == 3 :
		template = 'artevenue/abstract_category_landing.html'
	if curated_coll_id == 5 :
		template = 'artevenue/floral_category_landing.html'
	if curated_coll_id == 7 :
		template = 'artevenue/landscape_category_landing.html'

	return render(request, template, {'prod_categories':prod_categories,
		'product_category':product_cate, 
		'products':products, 'env': env} )
