from django.shortcuts import render, get_object_or_404
from django.conf import settings
from django.core.paginator import EmptyPage, PageNotAnInteger, Paginator
from django.views.decorators.csrf import csrf_protect, csrf_exempt
from django.db.models import Count, Q, F
from django.contrib.admin.views.decorators import staff_member_required

from datetime import datetime
import datetime
import json

from artevenue.models import Ecom_site, Stock_image, Stock_image_category, Publisher_price
from artevenue.models import Stock_image_stock_image_category, Cart_stock_image, Cart_item_view
from artevenue.models import Print_medium, Publisher_price, Promotion_stock_image, Promotion_product_view
from artevenue.models import Curated_collection, Curated_category
from artevenue.models import Wishlist, Wishlist_item_view

from .frame_views import *
from .image_views import *
from .price_views import *

today = datetime.date.today()
		
@csrf_exempt		
def category_stock_images(request, cat_id = ''):
	if cat_id == None:
		return

	ikeywords = request.GET.get('keywords', '')
	keywords = ikeywords.split()
	keyword_filter = False # Turned on only if a keyword filter is present (through the AJAX call)
	sortOrder = request.GET.get("sort")
	show = request.GET.get("show", '50')
	
	page = 1 # default

	prod_categories = Stock_image_category.objects.filter(store_id=settings.STORE_ID, trending = True )

	if cat_id:
		category_prods = Stock_image_stock_image_category.objects.filter(
				stock_image_category_id = cat_id).values('stock_image_id')
		
		product_cate = get_object_or_404 (Stock_image_category, category_id = cat_id)
	else :
		category_prods = Stock_image_stock_image_category.objects.values('stock_image_id')		
		product_cate = {}
		
	products = Stock_image.objects.filter(product_id__in = category_prods, 
				is_published = True)

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
			
				if majorkey == 'IMAGE-TYPE':
					f = f | Q(image_type = s)
				if majorkey == 'ORIENTATION':
					f = f | Q(orientation = s)
				#if majorkey == 'SIZE':
					#f = f | ( (Q(max_width__gte = width) & Q(max_height__gte = height) ) &  Q(aspect_ratio = ratio) )
				if majorkey == 'ARTIST':
					f = f | Q(artist = s)
				if majorkey == 'COLORS':
					#f = f | Q(colors__icontains = s)
					f = f | Q(key_words__icontains = s)
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
		products = products.filter( t_f )	

	# Apply keyword filter (through ajax or search)
	for word in keywords:
		products = products.filter( key_words__icontains = word )
		
	dt =  today.day
	if dt >= 1 and dt <= 5:
		products = products.order_by('?')
	elif dt > 5 and dt <= 10:
		products = products.order_by('product_id')
	elif dt > 10 and dt <= 20:
		products = products.order_by('name')
	else:
		products = products.order_by('part_number')

	prod_filters = ['ORIENTATION', 'ARTIST', 'IMAGE-TYPE', 'COLORS']	
	prod_filter_values ={}
	orientation_values = products.values('orientation').distinct()
	
	or_arr = []
	for v in orientation_values:
		if v['orientation'] not in or_arr:
			or_arr.append ( v['orientation'] )
	prod_filter_values['ORIENTATION'] = or_arr 
	
	artist_values = products.values('artist').distinct().order_by('artist')
	ar_arr = []
	for a in artist_values:
		if a['artist'] not in ar_arr:
			ar_arr.append(a['artist'] )
	prod_filter_values['ARTIST'] = ar_arr 
	
	image_type_values = products.values('image_type').distinct()
	im_arr = []
	for i in image_type_values:
		if i['image_type'] not in im_arr:
			im_arr.append(i['image_type'] )
	prod_filter_values['IMAGE-TYPE'] = im_arr


	#image_type_values = products.values('colors').distinct()
	im_arr = ['Red', 'Orange',  'Yellow', 'Green', 'Blue', 'Purple', 'Pink', 'Brown', 'black', 'White']
	prod_filter_values['COLORS'] = im_arr
	
	price = Publisher_price.objects.filter(print_medium_id = 'PAPER') 

	if show == None :
		show = 50
	
	if show == '50':
		perpage = 50 #default
		show = '50'
	else:
		if show == '100':
			perpage = 100
			show = '100'
		else:
			if show == 'ALL':
				perpage = 999999
				show = 'ALL'
			else:
				show = '50' # default
				perpage = 50
				
	paginator = Paginator(products, perpage) 
	if not page:
		page = request.GET.get('page')
	
	prods = paginator.get_page(page)		
	
	if request.is_ajax():

		template = "artevenue/prod_display_include.html"
	else :
		template = "artevenue/category_products.html"

	return render(request, template, {'prod_categories':prod_categories, 
		'category_prods': category_prods, 'product_category':product_cate, 
		'products':products, 'prods':prods, 'sortOrder':sortOrder, 'show':show,'prod_filters':prod_filters,
		'prod_filter_values':prod_filter_values, 'price':price, 'ikeywords':ikeywords,
		'page':page, 'wishlistitems':wishlistitems, 'wishlist_prods':wishlist_prods,
		'width':width, 'height':height} )

def show_categories(request):

	sortOrder = request.GET.get("sort")
	show = request.GET.get("show")

	# Get all the categories along with count of images in each
	categories_list = Stock_image_category.objects.annotate(Count(
		'stock_image_stock_image_category')).filter(
		stock_image_stock_image_category__count__gt = 0).order_by('name')

	print( categories_list )
		
	if show == None or show == '50':
		perpage = 50 #default
		show = '50'
	else:
		if show == '100':
			perpage = 100
		else:
			if show == 'ALL':
				perpage = 999999
				
	paginator = Paginator(categories_list, perpage) 
	page = request.GET.get('page')
	categories = paginator.get_page(page)
	
	return render(request, "artevenue/show_all_categories.html", {'categories':categories,
	'sortOrder':sortOrder, 'show':show})
		
		

@csrf_exempt	
def search_products_by_keywords(request):
		
	ikeywords = request.GET.get('keywords', '')
	keywords = ikeywords.split()		
	sortOrder = request.GET.get("sort")
	show = request.GET.get("show")
	
	prod_categories = Stock_image_category.objects.filter(store_id=settings.STORE_ID, trending = True )
	
	for word in keywords:
		products = Stock_image.objects.filter(is_published = True, key_words__icontains = word )

	# In AJAX, the keywords are pased back in a JSON, which is processed below. So in AJAX case,
	# Let's strat with all the products and then it will get filtered below
	if not keywords:
		products = Stock_image.objects.filter(is_published = True)
		
	width = 0
	height = 0
	if request.is_ajax():

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
			
				if majorkey == 'IMAGE-TYPE':
					f = f | Q(image_type = s)
				if majorkey == 'ORIENTATION':
					f = f | Q(orientation = s)
				if majorkey == 'ARTIST':
					f = f | Q(artist = s)
				if majorkey == 'COLORS':
					f = f | Q(colors__icontains = s)
				if majorkey == 'KEY-WORDS':
					f = f | Q(key_words__icontains = s)
			
			t_f = t_f & f
		print (t_f)

		products = products.filter( t_f )	

	prod_filters = ['ORIENTATION', 'ARTIST', 'IMAGE-TYPE']	
	prod_filter_values ={}
	orientation_values = products.values('orientation').distinct()

	or_arr = []
	for v in orientation_values:
		if v['orientation'] not in or_arr:
			or_arr.append ( v['orientation'] )
	prod_filter_values['ORIENTATION'] = or_arr 
	
	artist_values = products.values('artist').distinct().order_by('artist')
	ar_arr = []
	for a in artist_values:
		if a['artist'] not in ar_arr:
			ar_arr.append(a['artist'] )
	prod_filter_values['ARTIST'] = ar_arr 
	
	image_type_values = products.values('image_type').distinct()
	im_arr = []
	for i in image_type_values:
		if i['image_type'] not in im_arr:
			im_arr.append(i['image_type'] )
	prod_filter_values['IMAGE-TYPE'] = im_arr

	if show == None or show == '50':
		perpage = 50 #default
		show = '50'
	else:
		if show == '100':
			perpage = 100
		else:
			if show == 'ALL':
				perpage = 999999
				
	paginator = Paginator(products, perpage) 
	page = request.GET.get('page')
	prods = paginator.get_page(page)

	if request.is_ajax():

		template = "artevenue/prod_display_include.html"
	else :
		template = "artevenue/products_by_keywords.html"

	return render(request, template, {'prod_categories':prod_categories, 
		'products':products, 'prods':prods, 'sortOrder':sortOrder, 'show':show, 'prod_filters':prod_filters,
		'prod_filter_values':prod_filter_values, 'ikeywords':ikeywords,
		'width':width, 'height':height} )
	
def stock_image_detail(request, prod_id = ''):
	cart_item_id = request.GET.get("cart_item_id", "")
	wishlist_item_id = request.GET.get("wishlist_item_id", "")
	if not prod_id or prod_id == '' :
		prod_id = request.GET.get("product_id", "")
	
	if prod_id == None:
		return

	iuser_width = request.GET.get('iuser_width','0')
	iuser_height = request.GET.get('iuser_height','0')

	# get the product
	#product = Stock_image.objects.get(product_id = prod_id, is_published = True)
	product = get_object_or_404(Stock_image, is_published = True, pk=prod_id)
		
	product_category = Stock_image_stock_image_category.objects.get(stock_image = product) 
	
	prod_categories = Stock_image_category.objects.filter(store_id=settings.STORE_ID)
	
	printmedium = Print_medium.objects.all()

	
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
	# get mounts
	mounts = get_mounts(request)

	# get arylics
	acrylics = get_acrylics(request)
	
	# get boards
	boards = get_boards(request)

	# get Stretches
	stretches = get_stretches(request)

	# get the images with all mouldings
	###############img_with_all_mouldings = get_ImagesWithAllFrames(request, prod_id, 16)
	
	# Check if request contains any components, if it does send those to the front end
	cart_item_view = {}
	if cart_item_id != '':
		cart_item_view = Cart_item_view.objects.filter(cart_item_id = cart_item_id).first()
	wishlist_item_view = {}
	if wishlist_item_id != '':
		wishlist_item_view = Wishlist_item_view.objects.filter(wishlist_item_id = wishlist_item_id).first()
	'''
	return render(request, "artevenue/stock_image_detail.html", {'product':product,
		'prod_categories':prod_categories, 'printmedium':printmedium, 'product_category':product_category,
		'mouldings_appply':paper_mouldings_apply, 'mouldings_show':paper_mouldings_show, 'mounts':mounts,
		'per_sqinch_paper':per_sqinch_paper, 'per_sqinch_canvas':per_sqinch_canvas, 'acrylics':acrylics,
		'boards':boards, 'moulding_diagrams':moulding_diagrams,
		#######'img_with_all_mouldings':img_with_all_mouldings, 
		'stretches':stretches,
		'cart_item':cart_item_view, 'wishlist_item':wishlist_item_view, 'iuser_width':iuser_width, 
		'iuser_height':iuser_height} )	
	'''
	return render(request, "artevenue/stock_image_detail_with_var.html", {'product':product,
		'prod_categories':prod_categories, 'printmedium':printmedium, 'product_category':product_category,
		'mouldings_apply':paper_mouldings_apply, 'mouldings_show':paper_mouldings_show, 'mounts':mounts,
		'per_sqinch_paper':per_sqinch_paper, 'per_sqinch_canvas':per_sqinch_canvas, 'acrylics':acrylics,
		'boards':boards, 
		#######'img_with_all_mouldings':img_with_all_mouldings, 
		'stretches':stretches,
		'cart_item':cart_item_view, 'iuser_width':iuser_width, 'iuser_height':iuser_height} )	



@csrf_exempt	
def get_item_price (request):

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


					
	#####################################
	#         Get the item price
	#####################################
	price = get_prod_price(prod_id, 
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
	item_price_withoutdisc = price['item_unit_price']
	disc_amt = price['disc_amt']
	disc_applied = price['disc_applied']
	promotion_id = price['promotion_id']
	
	'''
	# Get image price on paper and canvas
	per_sqinch_price = get_per_sqinch_price(prod_id, prod_type)
	per_sqinch_paper = per_sqinch_price['per_sqin_paper']
	per_sqinch_canvas = per_sqinch_price['per_sqin_canvas']
					
	# Image Price
	if img_width > 0 and img_height > 0:
		msg = ""
	else :
		msg = "ERROR-Image size missing"

	# Get the Item Price
	if print_medium_id == "PAPER":
		# Image price
		if img_width > 0 and img_height > 0:
			image_price = img_width * img_height * per_sqinch_paper
			item_price = item_price + image_price
		else:
			image_price = 0
			item_price = 0

		print( "Width: " + str(img_width) )
		print( "height: " + str(img_height) )
		print( "Image Price: " + str(image_price) )
		
		# Acrylic Price		
		acrylic_price = img_width * img_height * get_acrylic_price_by_id(acrylic_id)
		item_price = item_price + acrylic_price
		item_price = item_price + acrylic_price
		print( "Acrylic Price: " + str(acrylic_price))
		
		# Moulding price
		moulding_price = (img_width + img_height) * 2 * get_moulding_price_by_id(moulding_id)
		item_price = item_price + moulding_price
		print( "Moulding Price: " + str(moulding_price))

		# Mount price
		mount_price = ((img_width + img_height) * 2 * mount_size)  * get_mount_price_by_id(mount_id)
		item_price = item_price + mount_price
		print( "Mount Price: " + str(mount_price))
		
		# Board price
		board_price = img_width * img_height * get_board_price_by_id(board_id)
		item_price = item_price + board_price
		print( "Board Price: " + str(board_price))

		print( "======================")
		print( "Total Item Price: " + str(item_price))
		
		
	elif print_medium_id == "CANVAS":

		# Image price
		image_price = img_width * img_height * per_sqinch_canvas
		item_price = item_price + image_price
		print( "Image Price: " + str(image_price))

		# Moulding price
		moulding_price = (img_width + img_height) * 2 * get_moulding_price_by_id(moulding_id)
		item_price = item_price + moulding_price
		print( "Moulding Price: " + str(moulding_price))
		
		# Stretch price
		stretch_price = img_width * img_height * get_stretch_price_by_id(stretch_id)
		item_price = item_price + stretch_price
		print( "Stretch Price: " + str(stretch_price))

		print( "======================")
		print( "Total Item Price: " + str(item_price))

	
	item_price_withoutdisc = round(item_price)
	
	disc_applied = False
	promo = get_product_promotion(prod_id)
	print(promo)
		
	disc_amt = 0
	cash_disc = 0
	if promo:
		cash_disc = round(promo['cash_disc'])
		percent_disc = promo['percent_disc']	
		promotion_id = promo['promotion_id']
	else:
		cash_disc = 0
		percent_disc = 0	
		promotion_id = ''
	
	if cash_disc > 0:
		item_price = item_price - cash_disc
		disc_applied = True
		disc_amt = round(cash_disc)
	elif percent_disc > 0:
		disc_amt = round(item_price * percent_disc / 100)
		item_price = item_price - disc_amt
		disc_applied = True	
	
	print("Price before = ")
	print(item_price)
	#item_price = round(item_price)
	item_price = Decimal(round(float(item_price),-1))
	print("Price after = ")
	print(item_price)

	
	print( "======================")
	print( "Disc Amt: " + str(disc_amt))
	print( "Item Price: " + str(item_price))
	'''
	print( "Item Price FROM new=======================: " + str(item_price))

	return JsonResponse({"msg":msg, "item_price" : item_price, 'cash_disc':cash_disc,
				'percent_disc':percent_disc, 'item_unit_price':item_price_withoutdisc,
				'disc_amt':disc_amt, 'disc_applied':disc_applied, 'promotion_id':promotion_id})
	

@csrf_exempt	
def get_item_price_by_cart_item (cart_item_id):

	item_price = 0
	img_height = 0
	img_width = 0
	stretch_id = 0
	image_price = 0
	moulding_price = 0
	acrylic_price = 0
	mount_price = 0
	stretch_price = 0
	board_price = 0
	
	msg = ""
	
	# Get prod data.
	cart_item = Cart_item_view.objects.filter(cart_item_id = cart_item_id).first()


	#####################################
	#         Get the item price
	#####################################
	price = get_prod_price(cart_item.product_id, 
			prod_type=cart_item.product_type_id,
			image_width=cart_item.image_width, 
			image_height=cart_item.image_height,
			print_medium_id = cart_item.print_medium_id,
			acrylic_id = cart_item.acrylic_id,
			moulding_id = cart_item.moulding_id,
			mount_size = cart_item.mount_size,
			mount_id = cart_item.mount_id,
			board_id = cart_item.board_id,
			stretch_id = cart_item.stretch_id)
	total_price = price['item_price']
	item_price = price['item_price']
	msg = price['msg']
	cash_disc = price['cash_disc']
	percent_disc = price['percent_disc']
	item_unit_price = price['item_unit_price']
	disc_amt = price['disc_amt']
	disc_applied = price['disc_applied']
	promotion_id = price['promotion_id']
	#####################################
	# END::::    Get the item price
	#####################################	

	#item_price = round(item_price, -1)
	item_price = Decimal(round(float(item_price),-1))

	print( "======================")
	print( "Disc Amt: " + str(disc_amt))
	print( "Item Price: " + str(item_price))


	return ({"msg":msg, "item_price" : item_price, 'cash_disc':cash_disc,
				'percent_disc':percent_disc, 'item_unit_price':item_unit_price,
				'disc_amt':disc_amt, 'disc_applied':disc_applied, 'promotion_id':promotion_id})

			
def get_product_promotion(prod_id):

	# Product promotions #	
	promo_prod = Promotion_product_view.objects.filter(product_id = prod_id,
			promotion__effective_from__lte = today, 
			promotion__effective_to__gte = today).select_related('promotion').first()

	cash_disc = 0
	percent_disc = 0
	promo_id = None
		
	
	if promo_prod:
		if promo_prod.promotion.discount_type == "CASH":
			cash_disc = promo_prod.promotion.discount_value
		if promo_prod.promotion.discount_type == "PERCENTAGE":
			percent_disc = promo_prod.promotion.discount_value
		promo_id = promo_prod.promotion_id
		
		
	return ({'promotion_id':promo_id, 'cash_disc':cash_disc, 'percent_disc':percent_disc})



def show_mouldings(request):

	print_medium = request.GET.get('print_medium', '')
	main_img = request.GET.get('main_img', '')

	if print_medium == '':
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
		
	return render(request, "artevenue/mouldings_include.html", {
		'mouldings_apply':mouldings_apply, 'mouldings_show':mouldings_show,
		'main_img':main_img} )

@csrf_exempt		
def all_stock_images(request):	
	
	ikeywords = request.GET.get('keywords', '')
	keywords = ikeywords.split()
	keyword_filter = False # Turned on only if a keyword filter is present (through the AJAX call)
	sortOrder = request.GET.get("sort")
	show = request.GET.get("show", '50')
	
	page = 1 # default
	
	prod_categories = Stock_image_category.objects.filter(store_id=settings.STORE_ID, trending = True )
	
	category_prods = Stock_image_stock_image_category.objects.values('stock_image_id')
	
	product_cate = {}

	products = Stock_image.objects.filter(product_id__in = category_prods, 
		is_published = True)
			
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
			
				if majorkey == 'IMAGE-TYPE':
					f = f | Q(image_type = s)
				if majorkey == 'ORIENTATION':
					f = f | Q(orientation = s)
				#if majorkey == 'SIZE':
					#f = f | ( (Q(max_width__gte = width) & Q(max_height__gte = height) ) &  Q(aspect_ratio = ratio) )
				if majorkey == 'ARTIST':
					f = f | Q(artist = s)
				if majorkey == 'COLORS':
					#f = f | Q(colors__icontains = s)
					f = f | Q(key_words__icontains = s)
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
		products = products.filter( t_f )	
						
	# Apply keyword filter (through ajax or search)
	for word in keywords:
		products = products.filter( key_words__icontains = word )

	dt =  today.day
	if dt >= 1 and dt <= 5:
		products = Stock_image.objects.filter(product_id__in = category_prods, 
			is_published = True).order_by('?')
	elif dt > 5 and dt <= 10:
		products = Stock_image.objects.filter(product_id__in = category_prods, 
			is_published = True).order_by('product_id')
	elif dt > 10 and dt <= 20:
		products = Stock_image.objects.filter(product_id__in = category_prods, 
			is_published = True).order_by('name')
	else:
		products = Stock_image.objects.filter(product_id__in = category_prods, 
		is_published = True).order_by('part_number')

	
	prod_filters = ['ORIENTATION', 'ARTIST', 'IMAGE-TYPE', 'COLORS']	
	prod_filter_values ={}
	orientation_values = products.values('orientation').distinct()
	
	or_arr = []
	for v in orientation_values:
		if v['orientation'] not in or_arr:
			or_arr.append ( v['orientation'] )
	prod_filter_values['ORIENTATION'] = or_arr 
	
	artist_values = products.values('artist').distinct().order_by('artist')
	ar_arr = []
	for a in artist_values:
		if a['artist'] not in ar_arr:
			ar_arr.append(a['artist'] )
	prod_filter_values['ARTIST'] = ar_arr 
	
	image_type_values = products.values('image_type').distinct()
	im_arr = []
	for i in image_type_values:
		if i['image_type'] not in im_arr:
			im_arr.append(i['image_type'] )
	prod_filter_values['IMAGE-TYPE'] = im_arr


	#image_type_values = products.values('colors').distinct()
	im_arr = ['Red', 'Orange',  'Yellow', 'Green', 'Blue', 'Purple', 'Pink', 'Brown', 'black', 'White']
	prod_filter_values['COLORS'] = im_arr
	
	price = Publisher_price.objects.filter(print_medium_id = 'PAPER') 

	if show == None :
		show = 50
	
	if show == '50':
		perpage = 50 #default
		show = '50'
	else:
		if show == '100':
			perpage = 100
			show = '100'
		else:
			if show == 'ALL':
				perpage = 999999
				show = 'ALL'
			else:
				show = '50' # default
				perpage = 50
				
	paginator = Paginator(products, perpage) 
	if not page:
		page = request.GET.get('page')
	prods = paginator.get_page(page)		
	
	if request.is_ajax():

		template = "artevenue/prod_display_include.html"
	else :
		template = "artevenue/category_products.html"

	return render(request, template, {'prod_categories':prod_categories, 
		'category_prods': category_prods, 'product_category':product_cate, 
		'products':products, 'prods':prods, 'sortOrder':sortOrder, 'show':show,'prod_filters':prod_filters,
		'prod_filter_values':prod_filter_values, 'price':price,
		'width':width, 'height':height} )

		
		
@csrf_exempt		
def curated_collections(request, cat_id):
	if cat_id == None:
		return

	ikeywords = request.GET.get('keywords', '')
	keywords = ikeywords.split()
	keyword_filter = False # Turned on only if a keyword filter is present (through the AJAX call)
	page = 1 # default

	sortOrder = request.GET.get("sort")
	show = request.GET.get("show")
	
	prod_categories = Stock_image_category.objects.filter(store_id=settings.STORE_ID, trending = True )
	
	#category_prods = Stock_image_stock_image_category.objects.filter(
	#		stock_image_category_id = cat_id).values('stock_image_id')
				
	dt =  today.day
	curated_coll = Curated_collection.objects.filter(curated_category_id = cat_id,
			product_type_id = 'STOCK-IMAGE').values('product_id')
	try:
		product_cate = Curated_category.objects.get(category_id = cat_id);
	except Curated_category.DoesNotExist:
		product_cate = {}
	products = Stock_image.objects.filter(product_id__in = curated_coll)
	
	if dt >= 1 and dt <= 5:
		products = products.order_by('key_words')
	elif dt > 5 and dt <= 10:
		products = products.order_by('product_id')
	elif dt > 10 and dt <= 20:
		products = products.order_by('name')
	else:
		products = products.order_by('part_number')
	
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
			
				if majorkey == 'IMAGE-TYPE':
					f = f | Q(image_type = s)
				if majorkey == 'ORIENTATION':
					f = f | Q(orientation = s)
				if majorkey == 'ARTIST':
					f = f | Q(artist = s)
				if majorkey == 'COLORS':
					#f = f | Q(colors__icontains = s)
					f = f | Q(key_words__icontains = s)
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
		products = products.filter( t_f )	

	# Apply keyword filter (through ajax or search)
	for word in keywords:
		products = products.filter( key_words__icontains = word )						

	prod_filters = ['ORIENTATION', 'ARTIST', 'IMAGE-TYPE', 'COLORS']	
	prod_filter_values ={}
	orientation_values = products.values('orientation').distinct()
	
	or_arr = []
	for v in orientation_values:
		if v['orientation'] not in or_arr:
			or_arr.append ( v['orientation'] )
	prod_filter_values['ORIENTATION'] = or_arr 
	
	artist_values = products.values('artist').distinct().order_by('artist')
	ar_arr = []
	for a in artist_values:
		if a['artist'] not in ar_arr:
			ar_arr.append(a['artist'] )
	prod_filter_values['ARTIST'] = ar_arr 
	
	image_type_values = products.values('image_type').distinct()
	im_arr = []
	for i in image_type_values:
		if i['image_type'] not in im_arr:
			im_arr.append(i['image_type'] )
	prod_filter_values['IMAGE-TYPE'] = im_arr


	#image_type_values = products.values('colors').distinct()
	im_arr = ['Red', 'Orange',  'Yellow', 'Green', 'Blue', 'Purple', 'Pink', 'Brown', 'black', 'White']
	prod_filter_values['COLORS'] = im_arr
	
	price = Publisher_price.objects.filter(print_medium_id = 'PAPER') 

	if show == None :
		show = 50
	
	if show == '50':
		perpage = 50 #default
		show = '50'
	else:
		if show == '100':
			perpage = 100
			show = '100'
		else:
			if show == 'ALL':
				perpage = 999999
				show = 'ALL'
			else:
				show = '50' # default
				perpage = 50
				
	paginator = Paginator(products, perpage) 
	if not page:
		page = request.GET.get('page')

	prods = paginator.get_page(page)
	
	if request.is_ajax():

		template = "artevenue/prod_display_include.html"
	else :
		template = "artevenue/curated_products.html"

	return render(request, template, {'prod_categories':prod_categories, 
		'product_category':product_cate, 
		'products':products, 'prods':prods, 'sortOrder':sortOrder, 'show':show,'prod_filters':prod_filters,
		'prod_filter_values':prod_filter_values, 'price':price, 'show_artist':True,
		'width':width, 'height':height} )		

@staff_member_required
@csrf_exempt
def image_by_image_code(request):
	products = {}
	show = None
	page=1

	code = request.POST.get("code", '')
	codel = code.split(',')
	code_list = []
	for i in codel:
		j = i.strip()
		code_list.append(j)	
	
	number = request.POST.get("number", '')
	numberl = number.split(',')
	number_list = []
	for i in numberl:
		j = i.strip()
		number_list.append(j)	

	if request.is_ajax():
		template = 'artevenue/prod_display_include.html'
		products = Stock_image.objects.filter(is_published = True)
		if code != '' :
			products = products.filter(product_id__in = code_list)
		if number != '' :
			products = products.filter(part_number__in = number_list)
	else :
		template = 'artevenue/image_by_image_code.html'
	
	if show == None :
		show = 50
	
	if show == '50':
		perpage = 50 #default
		show = '50'
	else:
		if show == '100':
			perpage = 100
			show = '100'
		else:
			if show == 'ALL':
				perpage = 999999
				show = 'ALL'
			else:
				show = '50' # default
				perpage = 50
	
	if request.is_ajax():
		paginator = Paginator(products, perpage) 
		
		if not page:
			page = request.POST.get('page')

		prods = paginator.get_page(page)
	else :
		prods = {}

	return render(request, template,
			{'prods':prods, 'show':show, 'perpage':perpage, 'width':16})

		