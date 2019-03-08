from django.shortcuts import render, get_object_or_404
from django.conf import settings
from django.core.paginator import EmptyPage, PageNotAnInteger, Paginator
from django.views.decorators.csrf import csrf_protect, csrf_exempt
from django.db.models import Count, Q

from datetime import datetime
import datetime
import json

from artevenue.models import Ecom_site, Stock_image, Stock_image_category
from artevenue.models import Stock_image_stock_image_category, Cart_stock_image, Cart_item_view
from artevenue.models import Print_medium, Publisher_price, Promotion_stock_image, Promotion_product_view

from .frame_views import *
from .image_views import *

today = datetime.date.today()
		
@csrf_exempt		
def category_stock_images(request, cat_id):

	if cat_id == None:
		return

	sortOrder = request.GET.get("sort")
	show = request.GET.get("show")
		
	prod_categories = Stock_image_category.objects.filter(store_id=settings.STORE_ID, trending = True )
	
	category_prods = Stock_image_stock_image_category.objects.filter(
			stock_image_category_id = cat_id).values('stock_image_id')
	
	product_cate = get_object_or_404 (Stock_image_category, category_id = cat_id)

	
	if sortOrder == None:
		None
	else:
		if sortOrder == "PRICEUP":
			products = Stock_image.objects.filter(product_id__in = category_prods, is_published = True).order_by('price')
		else:
			products = Stock_image.objects.filter(product_id__in = category_prods, is_published = True).order_by('-price')
			
	if request.is_ajax():
		#Apply the user selected filters -

		# Get data from the request.
		json_data = json.loads(request.body.decode("utf-8"))

		major_array = []
		sub_array = []
		size_key = None
		size_val = None
		width = 0
		products = Stock_image.objects.filter(product_id__in = category_prods, is_published = True)
	
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
					ratio = width/height
			
				if majorkey == 'IMAGE-TYPE':
					f = f | Q(image_type = s)
				if majorkey == 'ORIENTATION':
					f = f | Q(orientation = s)
				if majorkey == 'SIZE':
					f = f | ( (Q(max_width__gte = width) & Q(max_height__gte = height) ) &  Q(aspect_ratio = ratio) )
				if majorkey == 'ARTIST':
					f = f | Q(artist = s)
				if majorkey == 'COLORS':
					f = f | Q(colors__icontains = s)
				if majorkey == 'KEY-WORDS':
					f = f | Q(key_words__icontains = s)
			
			t_f = t_f & f
		print (t_f)
		products = products.filter( t_f )	
						
					
	else :
	
		products = Stock_image.objects.filter(product_id__in = category_prods, is_published = True)


	prod_filters = ['ORIENTATION', 'ARTIST', 'IMAGE-TYPE']	
	prod_filter_values ={}
	orientation_values = Stock_image.objects.values('orientation').distinct()
	or_arr = []
	for v in orientation_values:
		 or_arr.append ( v['orientation'] )
	prod_filter_values['ORIENTATION'] = or_arr 
		 
	artist_values = Stock_image.objects.values('artist').distinct()
	ar_arr = []
	for a in artist_values:
		ar_arr.append(a['artist'] )
	prod_filter_values['ARTIST'] = ar_arr 
	
	image_type_values = Stock_image.objects.values('image_type').distinct()
	im_arr = []
	for i in image_type_values:
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
		template = "artevenue/category_products.html"

	return render(request, template, {'prod_categories':prod_categories, 
		'category_prods': category_prods, 'product_category':product_cate, 
		'products':products, 'prods':prods, 'sortOrder':sortOrder, 'show':show,'prod_filters':prod_filters,
		'prod_filter_values':prod_filter_values
		} )

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

	if request.is_ajax():

		# Get data from the request.
		json_data = json.loads(request.body.decode("utf-8"))

		major_array = []
		sub_array = []
		size_key = None
		size_val = None
		width = 0
		for majorkey, subdict in json_data.items():

			for subkey, value in subdict.items():
				if majorkey == 'SIZE':
					# Get the size
					idx = subkey.find("_")
					width = int(subkey[:idx])
					height = int(subkey[(idx+1):])
					ratio = width/height
					size_key = "MAX-WIDTH"
					continue				

				if majorkey == 'SEARCH':
					# Get the size
					if subkey == 'KEYWORDS':
						search_keywords = value.split()					
					continue				

				if value.upper().strip() == "TRUE":
					print ( "Apply - " + majorkey + " : " + subkey)
					major_array.append(majorkey)
					sub_array.append(subkey) 

			
		# process the keywords that were passed back
		if search_keywords:
			for word in search_keywords:
				products = products.filter(kay_words__icontains = word)
				#q = Q(name = 'KEY-WORDS', value__icontains = word)
		
		# Process the SIZE filter
		if major_array :
			products = products.filter(product_attribute__name__in = major_array)
			if sub_array :
				products = products.filter(product_attribute__value__in = sub_array)		
		
		if size_key:
			if width:
				products = products.filter(product_attribute__name = size_key, 
					product_attribute__value__gte = width)
				if ratio :
					products = products.filter(product_attribute__name = 'ASPECT-RATIO', 
						product_attribute__value = ratio)
			#q_size = Q(name =  size_key, value__gte = width)
			

	prod_filters = ['ORIENTATION', 'ARTIST', 'IMAGE-TYPE']
	
	prod_filter_values = {}


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
		'prod_filter_values':prod_filter_values, 'ikeywords':ikeywords} )
	
def stock_image_detail(request, prod_id):
	if prod_id == None:
		return
	
	# get the product
	product = Stock_image.objects.get(product_id = prod_id, is_published = True)
	product_category = Stock_image_stock_image_category.objects.get(stock_image = product) 
	
	prod_categories = Stock_image_category.objects.filter(store_id=settings.STORE_ID)
	
	printmedium = Print_medium.objects.all()
			
	# Get image price on paper and canvas
	per_sqinch_price = get_per_sqinch_price(prod_id)
	per_sqinch_paper = per_sqinch_price['per_sqin_paper']
	per_sqinch_canvas = per_sqinch_price['per_sqin_canvas']

	# get mouldings
	mouldings = get_mouldings(request)
	# defaul we send is for PAPER
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
	
	# get the images with all mouldings
	img_with_all_mouldings = get_ImagesWithAllFrames(request, prod_id, 16)
	
	# Check if request contains any components, if it does send those to the front end
	cart_item_id = request.GET.get('cart_item_id', '')

	cart_item_view = {}
	if cart_item_id != '':
		cart_item_view = Cart_item_view.objects.filter(cart_item_id = cart_item_id).first()
	
	return render(request, "artevenue/stock_image_detail.html", {'product':product,
		'prod_categories':prod_categories, 'printmedium':printmedium, 'product_category':product_category,
		'mouldings_appply':paper_mouldings_apply, 'mouldings_show':paper_mouldings_show, 'mounts':mounts,
		'per_sqinch_paper':per_sqinch_paper, 'per_sqinch_canvas':per_sqinch_canvas, 'acrylics':acrylics,
		'boards':boards, 'img_with_all_mouldings':img_with_all_mouldings, 'stretches':stretches,
		'cart_item':cart_item_view} )	

	
def get_per_sqinch_price(prod_id):

	prod = Stock_image.objects.filter(product_id = prod_id).first()
	publisher_price = Publisher_price.objects.filter(publisher_id = prod.publisher )
	
	per_sqin_paper = 0
	per_sqin_canvas = 0
	for p in publisher_price:
		if p.print_medium_id == "PAPER" :
			per_sqin_paper = p.price
		if p.print_medium_id == "CANVAS" :
			per_sqin_canvas = p.price
	 
	return ({'per_sqin_paper':per_sqin_paper, 'per_sqin_canvas' : per_sqin_canvas})



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

					
	# Get image price on paper and canvas
	per_sqinch_price = get_per_sqinch_price(prod_id)
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
		image_price = img_width * img_height * per_sqinch_paper
		item_price = item_price + image_price

		print( "Width: " + str(img_width) )
		print( "height: " + str(img_height) )
		print( "Image Price: " + str(image_price) )
		
		# Acrylic Price		
		acrylic_price = img_width * img_height * get_acrylic_price_by_id(acrylic_id)
		item_price = item_price + acrylic_price
		print( "Acrylic Price: " + str(acrylic_price))
		
		# Moulding price
		moulding_price = (img_width + img_height) * 2 * get_moulding_price_by_id(moulding_id)
		item_price = item_price + moulding_price
		print( "Moulding Price: " + str(moulding_price))
		
		# Mount price
		mount_price = Decimal( ((img_width + img_height) * 2 * mount_size) ) * get_mount_price_by_id(mount_id)
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
		
	item_price = round(item_price)

	print( "======================")
	print( "Disc Amt: " + str(disc_amt))
	print( "Item Price: " + str(item_price))

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
	cart_item = Cart_stock_image.objects.filter(cart_item_id = cart_item_id).first()
	
					
	# Get image price on paper and canvas
	per_sqinch_price = get_per_sqinch_price(cart_item.product_id)
	per_sqinch_paper = per_sqinch_price['per_sqin_paper']
	per_sqinch_canvas = per_sqinch_price['per_sqin_canvas']
					
	# Image Price
	if cart_item.image_width > 0 and cart_item.image_height > 0:
		msg = ""
	else :
		msg = "ERROR-Image size missing"
	
	# Get the Item Price
	if cart_item.print_medium_id == "PAPER":
		# Image price
		image_price = cart_item.image_width * cart_item.image_height * per_sqinch_paper
		item_price = item_price + image_price
		print( "Width: " + str(cart_item.image_width) )
		print( "height: " + str(cart_item.image_height) )
		print( "Image Price: " + str(image_price) )
		
		# Acrylic Price		
		if cart_item.acrylic_id:
			acrylic_price = cart_item.image_width * cart_item.image_height * get_acrylic_price_by_id(cart_item.acrylic_id)
			item_price = item_price + acrylic_price
		print( "Acrylic Price: " + str(acrylic_price))
		
		# Moulding price
		if cart_item.moulding_id:
			moulding_price = (cart_item.image_width + cart_item.image_height) * 2 * get_moulding_price_by_id(cart_item.moulding_id)
			item_price = item_price + moulding_price
		print( "Moulding Price: " + str(moulding_price))
		
		# Mount price
		if cart_item.mount_id:
			mount_price = Decimal( ((cart_item.image_width + cart_item.image_height) * 2 * cart_item.mount_size) ) * get_mount_price_by_id(cart_item.mount_id)
			item_price = item_price + mount_price
		print( "Mount Price: " + str(mount_price))
		
		# Board price
		board_price = cart_item.image_width * cart_item.image_height * get_board_price_by_id(cart_item.board_id)
		item_price = item_price + board_price
		print( "Board Price: " + str(board_price))
		
		print( "======================")
		print( "Total Item Price: " + str(item_price))
		
		
		
	elif cart_item.print_medium_id == "CANVAS":

		# Image price
		image_price = cart_item.image_width * cart_item.image_height * per_sqinch_canvas
		item_price = item_price + image_price
		print( "Image Price: " + str(image_price))

		# Moulding price
		if cart_item.moulding_id:
			moulding_price = (cart_item.image_width + cart_item.image_height) * 2 * get_moulding_price_by_id(cart_item.moulding_id)
			item_price = item_price + moulding_price
		print( "Moulding Price: " + str(moulding_price))
		
		# Stretch price
		if cart_item.stretch_id:
			stretch_price = cart_item.image_width * cart_item.image_height * get_stretch_price_by_id(cart_item.stretch_id)
			item_price = item_price + stretch_price
	
		print( "Stretch Price: " + str(stretch_price))

		print( "======================")
		print( "Total Price: " + str(item_price))

	
	item_price_withoutdisc = item_price
	disc_applied = False
	promo = get_product_promotion(cart_item.product_id)
	print(promo)
		
	disc_amt = 0
	if promo:
		cash_disc = promo['cash_disc']
		percent_disc = promo['percent_disc']	
		promotion_id = promo['promotion_id']
	else:
		cash_disc = 0
		percent_disc = 0	
		promotion_id = ''
	
	if cash_disc > 0:
		item_price = item_price - cash_disc
		disc_applied = True
		disc_amt = cash_disc
	elif percent_disc > 0:
		disc_amt = item_price * percent_disc / 100
		item_price = item_price - ( disc_amt )
		disc_applied = True
		
	item_price = round(item_price)

	print( "======================")
	print( "Disc Amt: " + str(disc_amt))
	print( "Item Price: " + str(item_price))


	return ({"msg":msg, "item_price" : item_price, 'image_price':image_price, 'cash_disc':cash_disc,
				'percent_disc':percent_disc, 'item_unit_price':item_price_withoutdisc,
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
		
	