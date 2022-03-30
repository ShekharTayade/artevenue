from django.shortcuts import render, get_object_or_404
from django.conf import settings
from django.core.paginator import EmptyPage, PageNotAnInteger, Paginator
from django.views.decorators.csrf import csrf_protect, csrf_exempt
from django.db.models import Count, Q, F
from django.contrib.admin.views.decorators import staff_member_required
from django.http import HttpRequest
from django.core.exceptions import ObjectDoesNotExist

from datetime import datetime
import datetime
import json
import statistics
from PIL import Image

from stock_curve.models import Stock_curve, Stock_curve_variation
from artevenue.models import Ecom_site, Stock_image, Stock_image_category
from artevenue.models import Stock_curve, Print_medium, Publisher_price
from artevenue.models import Wishlist, Wishlist_item_view, Collage_stock_image, Cart_item_view

from .frame_views import *
from .image_views import *
from .price_views import *

today = datetime.date.today()
env = settings.EXEC_ENV


@csrf_exempt		
def stock_curve_products(request,):
	
	ikeywords = request.GET.get('keywords', '')
	keywords = ikeywords.split()
	keyword_filter = False # Turned on only if a keyword filter is present (through the AJAX call)
	sortOrder = request.GET.get("sort")
	show = request.GET.get("show", '100')
	page = request.GET.get("page", '')
	set_of = request.GET.get("set_of", '')

	if page is None or page == 0:
		page = 1 #default

	collages = Stock_curve.objects.filter(is_published = True, set_of__gt = 1).order_by('category_disp_priority')
	
	if set_of :
		if set_of > 0 :
			collages = collages.filter(set_of = set_of)

	cate = Stock_curve.objects.filter(
		is_published = True).values('stock_image_category__name').distinct()

	width = 0
	height = 0
	if request.is_ajax():
		#Apply the user selected filters -

		# Get data from the request.
		json_data = json.loads(request.body.decode("utf-8"))

		major_array = []
		sub_array = []
		size_key = None
		size_val = None
		
		t_f = Q()
		for majorkey, subdict in json_data.items():
			#######################################
			s_keys = json_data[majorkey]
			f = Q()
			for s in s_keys:
				if majorkey == 'SIZE':
					# Get the size
					idx = s.find("_")
					width = int(s[:idx])
					height = int(s[(idx+1):])
					ratio = round(Decimal(width)/Decimal(height), 18)
					f = f | ( Q( aspect_ratio = ratio) & Q(max_width__gte = width) & Q(max_height__gte = height))			
				if majorkey == 'PAINTING-ORIENTATION':
					f = f | Q(orientation = s)
				if majorkey == 'COLORS':
					#f = f | Q(colors__icontains = s)
					f = f | Q(key_words__icontains = s)					
				if majorkey == 'CATEGORIES':
					cat = Stock_image_category.objects.filter(
						name = s)
					f = f | Q(stock_image_category__in = cat)
				if majorkey == 'SET-OF':
					#f = f | Q(colors__icontains = s)
					f = f | Q(set_of__icontains = s)
				if majorkey == 'KEY-WORDS':
					ikeywords = s_keys[s] 
					print("Keywords: " + ikeywords)
					keywords = ikeywords.split()
					#f = f | Q(key_words__icontains = keywords)
					keyword_filter = True
				if majorkey == 'PAGE':									
					page = s_keys[s]
				if majorkey == 'SORT':
					sortOrder =  s_keys[s]
				if majorkey == 'SHOW':
					show =  str(s_keys[s])
			
			t_f = t_f & f
		print (t_f)
		collages = collages.filter( t_f )	

	# Apply keyword filter (through ajax or search)
	for word in keywords:
		collages = collages.filter( key_words__icontains = word )

	prod_filters = ['CATEGORIES', 'SET-OF', 'PAINTING-ORIENTATION', 'COLORS']
	prod_filter_values ={}
	orientation_values = collages.values('orientation')
	or_arr = []
	for v in orientation_values:
		if v['orientation'] not in or_arr:
			or_arr.append ( v['orientation'] )
	prod_filter_values['PAINTING-ORIENTATION'] = or_arr 
	
	im_arr = ['Red', 'Orange',  'Yellow', 'Green', 'Blue', 'Purple', 'Pink', 'Brown', 'black', 'White']
	prod_filter_values['COLORS'] = im_arr

	c_arr = []
	for c in cate:
		c_arr.append( c['stock_image_category__name'] )
	prod_filter_values['CATEGORIES'] = c_arr

	prod_filter_values['SET-OF'] = [2, 3]


	if request.user.is_authenticated:
		user = User.objects.get(username = request.user)
		wishlist = Wishlist.objects.filter(
			user = user).values('wishlist_id')
		wishlistitems = Wishlist_item_view.objects.filter(
			wishlist_id__in = wishlist)
	else:
		session_id = request.session.session_key
		wishlist = Wishlist.objects.filter(
			session_id = session_id).values('wishlist_id')
		wishlistitems = Wishlist_item_view.objects.filter(
			wishlist_id__in = wishlist)

	wishlist_prods = []
	if wishlistitems:
		for w in wishlistitems:
			wishlist_prods.append(w.product_id)

	price = Publisher_price.objects.filter(print_medium_id = 'PAPER') 


	if show == None :
		show = 100
	
	if show == '100':
		perpage = 100 #default
		show = '100'
	else:
		if show == '500':
			perpage = 500
			show = '500'
		else:
			if show == '1000':
				perpage = 1000
				show = '1000'
			else:
				show = '100' # default
				perpage = 100
				
	paginator = Paginator(collages, perpage) 
	if not page:
		page = request.GET.get('page')

	coll = paginator.get_page(page)
	
	#=====================
	index = coll.number - 1 
	max_index = len(paginator.page_range)
	start_index = index - 5 if index >= 5 else 0
	end_index = index + 5 if index <= max_index - 5 else max_index
	page_range = list(paginator.page_range)[start_index:end_index]
	#=====================
	
	if request.is_ajax():

		template = "artevenue/collage_display_include.html"
	else :
		template = "artevenue/stock_collage_products.html"
		
	return render(request, template,
			{'coll':coll, 'wishlist_prods':wishlist_prods, 
			'page':page, 'wishlistitems':wishlistitems,
			'sortOrder':sortOrder, 'show':show,'prod_filters':prod_filters,
			'prod_filter_values':prod_filter_values, 'ikeywords':ikeywords,
			'page':page, 'env': env})
			

@csrf_exempt
def get_stock_curve_price(request):

	item_price = 0
	img_height = 0
	img_width = 0
	print_medium_size = 0 
	acrylic_size = 0
	moulding_size= 0
	mount_size = 0
	board_size = 0 
	stretch_size = 0
	print_medium_id = ''
	acrylic_id = 0
	moulding_id = 0
	mount_id = 0
	board_id = 0
	stretch_id = 0
	prod_id = 0

	msg = ""

	# Get data from the request.
	json_data = json.loads(request.body.decode("utf-8"))

	major_array = []
	sub_array = []
	for majorkey, subdict in json_data.items():
		for subkey, value in subdict.items():
			
			# Get image height and width
			if majorkey.upper().strip() == "IMAGE":
				if subkey == "HEIGHT":
					img_height = value
				if subkey == "WIDTH":
					img_width = value

			# Get print medium
			if majorkey.upper().strip() == "PRINT_MEDIUM":
				if subkey == "ID":
					print_medium_id = value
				if subkey == "SIZE":
					print_medium_size = value
					

			# Get acrylic
			if majorkey.upper().strip() == "ACRYLIC":
				if subkey == "ID":
					acrylic_id = value
				if subkey == "SIZE":
					acrylic_size = value

			# Get moulding
			if majorkey.upper().strip() == "MOULDING":
				if subkey == "ID":
					moulding_id = value
				if subkey == "SIZE":
					moulding_size = value

			# Get Mount
			if majorkey.upper().strip() == "MOUNT":
				if subkey == "ID":
					mount_id = value
				if subkey == "SIZE":
					mount_size = value
					
			# Get Board
			if majorkey.upper().strip() == "BOARD":
				if subkey == "ID":
					board_id = value
				if subkey == "SIZE":
					baord_size = value

			# Get Stretch
			if majorkey.upper().strip() == "STRETCH":
				if subkey == "ID":
					stretch_id = value
				if subkey == "SIZE":
					stretch_size = value

			# Get product id
			if majorkey.upper().strip() == "PRODUCT":
				if subkey == "ID":
					prod_id = value

			if majorkey.upper().strip() == "PRODUCT_TYPE":
				if subkey == "ID":
					prod_type = value

	collages = Collage_stock_image.objects.filter( stock_collage_id = prod_id )
	total_price = 0
	total_cash_disc = 0
	total_percent_disc = 0
	total_item_price_withoutdisc = 0
	total_disc_amt = 0
	disc_applied = False
	promotion_id = None


	#####################################
	#    Get the item price for each
	#####################################
	for c in collages:
		price = get_prod_price(c.stock_image_id, 
				prod_type=prod_type,
				image_width=img_width, 
				image_height=img_height,
				print_medium_id = print_medium_id,
				acrylic_id = acrylic_id,
				moulding_id = moulding_id,
				mount_size = mount_size,
				mount_id = mount_id,
				board_id = board_id,
				stretch_id = stretch_id)					

		item_price = price['item_price']
		msg = price['msg']
		cash_disc = price['cash_disc']
		percent_disc = price['percent_disc']
		#item_price_withoutdisc = price['item_unit_price']
		if not 'item_price_without_disc' in price:	
			item_price_withoutdisc = item_price
		else:
			item_price_withoutdisc = price['item_price_without_disc']
		disc_amt = price['disc_amt']
		disc_applied = price['disc_applied']
		promotion_id = price['promotion_id']
		
		total_price = total_price + item_price
		total_cash_disc = total_cash_disc + cash_disc
		total_percent_disc = statistics.mean([total_percent_disc, percent_disc])
		total_item_price_withoutdisc = total_item_price_withoutdisc + item_price_withoutdisc
		total_disc_amt = total_disc_amt + disc_amt
		
	return JsonResponse({"msg":msg, "item_price" : total_price, 'cash_disc':total_cash_disc,
				'percent_disc':total_percent_disc, 'item_unit_price':total_item_price_withoutdisc,
				'disc_amt':total_disc_amt, 'disc_applied':disc_applied, 'promotion_id':promotion_id})
	
	
	
def stock_curve_detail(request, prod_id = '', variation_id=''):
	cart_item_id = request.GET.get("cart_item_id", "")
	wishlist_item_id = request.GET.get("wishlist_item_id", "")
	if not prod_id or prod_id == '' :
		prod_id = request.GET.get("product_id", "")
	
	if prod_id == None:
		return
	
	if variation_id == '':
		variation_id = request.GET.get('variation_id','')

	# get the product
	product = get_object_or_404(Stock_curve, is_published = True, pk=prod_id)			
	product_variations = Stock_curve_variation.objects.filter(stock_curve_id = prod_id)
	prices = {}
	for v in product_variations:
		v_price = 0
		if v.stock_curve_variation_id:
			v_price = get_variation_price(i.stock_curve_variation_id)
		if v_price == 0:
			continue
		prices[v.id] = v_price


		
	if request.user.is_authenticated:
		user = User.objects.get(username = request.user)
		wishlist = Wishlist.objects.filter(
			user = user).values('wishlist_id')
		wishlistitems = Wishlist_item_view.objects.filter(
			wishlist_id__in = wishlist)
	else:
		session_id = request.session.session_key
		wishlist = Wishlist.objects.filter(
			session_id = session_id).values('wishlist_id')
		wishlistitems = Wishlist_item_view.objects.filter(
			wishlist_id__in = wishlist)

	wishlist_prods = []
	if wishlistitems:
		for w in wishlistitems:
			wishlist_prods.append(w.product_id)
	

	# Check if request contains any components, if it does send those to the front end
	cart_item_view = {}
	if cart_item_id != '':
		cart_item_view = Cart_item_view.objects.filter(cart_item_id = cart_item_id).first()
	wishlist_item_view = {}
	if wishlist_item_id != '':
		wishlist_item_view = Wishlist_item_view.objects.filter(wishlist_item_id = wishlist_item_id).first()



	return render(request, "artevenue/stock_curve_detail.html", {'product':product, "product_variations" : product_variations,
		'variation_id' : variation_id, 'cart_item':cart_item_view, 'variation_id': variation_id, 'price':price, 
		'wishlist_prods':wishlist_prods, 'wishlist_item':wishlist_item_view, 'ENV':settings.EXEC_ENV,} )
	


def get_variation_price(stock_curve_variation_id=None):
	product_variation = Stock_curve_variation.objects.filter(stock_curve_variation_id = stock_curve_variation_id)
	v_price = 0
	if stock_curve_variation_id:		
		v_price = product_variation.price
		
	return price