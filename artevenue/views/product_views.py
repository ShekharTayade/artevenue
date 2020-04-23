from django.shortcuts import render, get_object_or_404
from django.conf import settings
from django.core.paginator import EmptyPage, PageNotAnInteger, Paginator
from django.views.decorators.csrf import csrf_protect, csrf_exempt
from django.db.models import Count, Q, F
from django.contrib.admin.views.decorators import staff_member_required

from datetime import datetime
import datetime
import json

from artevenue.models import Ecom_site, Stock_image, Stock_image_category
from artevenue.models import Publisher_price, Original_art_original_art_category, Original_art
from artevenue.models import Stock_image_stock_image_category, Cart_stock_image, Cart_item_view
from artevenue.models import Print_medium, Publisher_price, Promotion_stock_image, Promotion_product_view
from artevenue.models import Curated_collection, Curated_category, Promotion
from artevenue.models import Wishlist, Wishlist_item_view, Homelane_data

from .frame_views import *
from .image_views import *
from .price_views import *

today = datetime.date.today()
		
@csrf_exempt		
def category_stock_images(request, cat_id = '', page = 1):
	if cat_id is None or cat_id == '':
		return

	ikeywords = request.GET.get('keywords', '')
	keywords = ikeywords.split()
	keyword_filter = False # Turned on only if a keyword filter is present (through the AJAX call)
	sortOrder = request.GET.get("sort")
	show = request.GET.get("show", '100')
	
	if page is None or page == 0:
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
		products = products.filter( 
			Q(key_words__icontains = word) |
			Q(artist__icontains = word)
			)
		
	dt =  today.day
	if dt >= 1 and dt <= 5:
		products = products.order_by('category_disp_priority', '?')
	elif dt > 5 and dt <= 10:
		products = products.order_by('category_disp_priority', 'product_id')
	elif dt > 10 and dt <= 20:
		products = products.order_by('category_disp_priority', 'name')
	else:
		products = products.order_by('category_disp_priority', 'part_number')


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
				
	paginator = Paginator(products, perpage) 
	if not page:
		page = request.GET.get('page')
	
	prods = paginator.get_page(page)			
	
	#=====================
	index = prods.number - 1 
	max_index = len(paginator.page_range)
	start_index = index - 5 if index >= 5 else 0
	end_index = index + 5 if index <= max_index - 5 else max_index
	page_range = list(paginator.page_range)[start_index:end_index]
	#=====================
	
	if request.is_ajax():

		template = "artevenue/prod_display_include.html"
	else :
		template = "artevenue/category_products.html"
		#template = "artevenue/art_by_category.html"

	return render(request, template, {'prod_categories':prod_categories, 
		'category_prods': category_prods, 'product_category':product_cate, 
		'products':products, 'prods':prods, 'sortOrder':sortOrder, 'show':show,'prod_filters':prod_filters,
		'prod_filter_values':prod_filter_values, 'price':price, 'ikeywords':ikeywords,
		'page':page, 'wishlistitems':wishlistitems, 'wishlist_prods':wishlist_prods,
		'width':width, 'height':height, 'page_range':page_range} )

def show_categories(request):

	sortOrder = request.GET.get("sort")
	show = request.GET.get("show")
	# Get all the categories along with count of images in each
	categories_list = Stock_image_category.objects.annotate(Count(
		'stock_image_stock_image_category')).filter(
		stock_image_stock_image_category__count__gt = 0).exclude(name = '').exclude(
		name = '#N/A').order_by('name')

	all_cnt = Stock_image.objects.filter(is_published = True).count()

	'''
	if show == None or show == '50':
		perpage = 50 #default
		show = '50'
	else:
		if show == '100':
			perpage = 100
		else:
			if show == '1000':
				perpage = 10000
				
	paginator = Paginator(categories_list, perpage) 
	page = request.GET.get('page')
	categories = paginator.get_page(page)

	#=====================
	index = categories.number - 1 
	max_index = len(paginator.page_range)
	start_index = index - 5 if index >= 5 else 0
	end_index = index + 5 if index <= max_index - 5 else max_index
	page_range = list(paginator.page_range)[start_index:end_index]
	#=====================
	'''

	return render(request, "artevenue/show_all_categories.html", {'categories':categories_list,
	'cnt': categories_list.count(), 'all_cnt':all_cnt})
				
@csrf_exempt	
def search_products_by_keywords(request):
		
	ikeywords = request.GET.get('keywords', '')
	keywords = ikeywords.split()		
	sortOrder = request.GET.get("sort")
	show = request.GET.get("show")
	
	prod_categories = Stock_image_category.objects.filter(store_id=settings.STORE_ID, trending = True )
	
	for word in keywords:
		products = Stock_image.objects.filter(
			Q(is_published = True) &
			(Q(key_words__icontains = word) | Q(artist__icontains = word))
		)

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
			if show == '1000':
				perpage = 1000
				
	paginator = Paginator(products, perpage) 
	page = request.GET.get('page')
	prods = paginator.get_page(page)

	#=====================
	index = prods.number - 1 
	max_index = len(paginator.page_range)
	start_index = index - 5 if index >= 5 else 0
	end_index = index + 5 if index <= max_index - 5 else max_index
	page_range = list(paginator.page_range)[start_index:end_index]
	#=====================

	if request.is_ajax():

		template = "artevenue/prod_display_include.html"
	else :
		template = "artevenue/products_by_keywords.html"

	return render(request, template, {'prod_categories':prod_categories, 
		'products':products, 'prods':prods, 'sortOrder':sortOrder, 'show':show, 'prod_filters':prod_filters,
		'prod_filter_values':prod_filter_values, 'ikeywords':ikeywords,
		'width':width, 'height':height, 'page_range':page_range} )
	
def stock_image_detail(request, prod_id = '', iuser_width='', iuser_height=''):
	cart_item_id = request.GET.get("cart_item_id", "")
	wishlist_item_id = request.GET.get("wishlist_item_id", "")
	if not prod_id or prod_id == '' :
		prod_id = request.GET.get("product_id", "")
	
	if prod_id == None:
		return
	
	if not iuser_width or iuser_width == '':
		iuser_width = request.GET.get('iuser_width','0')
	if not iuser_height or iuser_height == '' :
		iuser_height = request.GET.get('iuser_height','0')

	# get the product
	#product = Stock_image.objects.get(product_id = prod_id, is_published = True)
	product = get_object_or_404(Stock_image, is_published = True, pk=prod_id)
		
	product_category = Stock_image_stock_image_category.objects.get(stock_image = product)
	
	prod_categories = Stock_image_category.objects.filter(store_id=settings.STORE_ID)
	
	printmedium = Print_medium.objects.all()

	##############################################
	## Get the similar products
	##############################################
	similar_products = {}
	## First get rpoducts by same artist
	similar_products_artist = Stock_image.objects.filter(  
			artist = product.artist).exclude(product_id = prod_id)
	## If same artist has more than 8 products, then filter further
	if similar_products_artist:
		if similar_products_artist.count() > 8 :
			## Filter for the same artist and same category
			prods_in_cat = Stock_image_stock_image_category.objects.filter(
				stock_image_category_id = product_category.stock_image_category).values('stock_image_id')
			similar_products_cat = similar_products_artist.filter(
				product_id__in = prods_in_cat)
			## Same artist has more than 8 products in same category, filter further
			if similar_products_cat: 
				if similar_products_cat.count() > 8 :
					## Filter for having same key words
					similar_products_kw = similar_products_cat.filter( key_words__in = product.key_words )
					if similar_products_kw :
						if similar_products_kw.count() > 8:
							similar_products = similar_products_kw
						else :
							similar_products = similar_products_cat.filter(
								product_id__in = prods_in_cat)
					else:
						similar_products = similar_products_cat.filter(
							product_id__in = prods_in_cat)
						
				## if the filter causes the result to be empty, revert to earlier filter
				else:
					similar_products = Stock_image.objects.filter(  
							artist = product.artist)
			else :
					similar_products = Stock_image.objects.filter(  
						artist = product.artist)
		else:
			similar_products = Stock_image.objects.filter(  
					artist = product.artist)

	## Restrict the result to 10 products
	if similar_products:
		if similar_products.count() > 8:
			similar_products = similar_products[:8]

	price = Publisher_price.objects.filter(print_medium_id = 'PAPER') 


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
	paper_mouldings_corner = mouldings['paper_mouldings_corner']
	canvas_mouldings_corner = mouldings['canvas_mouldings_corner']
	# get mounts
	mounts = get_mounts(request)

	# get arylics
	acrylics = get_acrylics(request)
	
	# get boards
	boards = get_boards(request)

	# get Stretches
	stretches = get_stretches(request)
	
	# Check if request contains any components, if it does send those to the front end
	cart_item_view = {}
	if cart_item_id != '':
		cart_item_view = Cart_item_view.objects.filter(cart_item_id = cart_item_id).first()
	wishlist_item_view = {}
	if wishlist_item_id != '':
		wishlist_item_view = Wishlist_item_view.objects.filter(wishlist_item_id = wishlist_item_id).first()

	prod_data = get_price_for_6_prods(prod_id, product.aspect_ratio)
	ready_prod_data_paper = prod_data['size_price_paper']
	ready_prod_data_canvas = prod_data['size_price_canvas']

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
	
	#wall_colors = ['255,255,224', '255,255,204', '152,251,152', '0,100,0', '128,128,0', '255,255,0', '173,216,230',
	#		'65,182,230', '255,205,72', '244,164,96', '255,99,71', '243,100,162', '255,20,147', '137,46,58']
	
	wall_colors = ['255,255,255', '255,255,224', '242,242,242', '230,242,255', '65,182,230', '64,224,208', '204,255,204', '128,128,0', '255,255,179', '255,205,72', '255,215,0', '255,230,230', '137,46,58', '255,0,0']
	request.session.set_test_cookie()   ## To test if cookie is enabled on the browser. If not display message in Size and Color Tool.

	return render(request, "artevenue/stock_image_detail_new.html", {'product':product,
		'prod_categories':prod_categories, 'printmedium':printmedium, 'product_category':product_category,
		'mouldings_apply':paper_mouldings_apply, 'mouldings_show':paper_mouldings_show, 'mounts':mounts,
		'per_sqinch_paper':per_sqinch_paper, 'per_sqinch_canvas':per_sqinch_canvas, 'acrylics':acrylics,
		'boards':boards,'stretches':stretches, 'ENV':settings.EXEC_ENV,
		'cart_item':cart_item_view, 'iuser_width':iuser_width, 'iuser_height':iuser_height,
		'prods':similar_products, 'price':price, 'wishlist_prods':wishlist_prods,
		'paper_mouldings_corner':paper_mouldings_corner, 'canvas_mouldings_corner':canvas_mouldings_corner,
		'ready_prod_data_paper':ready_prod_data_paper, 'ready_prod_data_canvas':ready_prod_data_canvas,
		'wishlist_item':wishlist_item_view, 'wall_colors': wall_colors} )

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
	#item_price_withoutdisc = price['item_unit_price']
	item_price_withoutdisc = price['item_price_without_disc']
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


	return ({"msg":msg, "item_price" : item_price, 'cash_disc':cash_disc,
				'percent_disc':percent_disc, 'item_unit_price':item_unit_price,
				'disc_amt':disc_amt, 'disc_applied':disc_applied, 'promotion_id':promotion_id})
		
def get_product_promotion(prod_id, prod_type = None):
	cash_disc = 0
	percent_disc = 0
	promo_id = None
	if prod_type == None:
		prod_type = 'STOCK-IMAGE'
			
	## Check for store wide promotion
	promo = Promotion.objects.filter(effective_from__lte = today, 
			effective_to__gte = today, promotion_type = 'A').first()
	
	if promo:
		if promo.discount_type == "CASH":
			cash_disc =promo.discount_value
		if promo.discount_type == "PERCENTAGE":
			percent_disc = promo.discount_value
		promo_id = promo.promotion_id
				
	else:
		# Product promotions #	
		promo_prod = Promotion_product_view.objects.filter(product_id = prod_id,
				product_type_id = prod_type,
				promotion__effective_from__lte = today, 
				promotion__effective_to__gte = today).select_related('promotion').first()

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
	show = request.GET.get("show", '100')
	result_limit = request.GET.get("result_limit", '0-50')
	
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
		result_limit = '0-50'
		
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
				if majorkey == 'RESULT-LIMIT':									
					result_limit = s_keys[s]
				if majorkey == 'SORT':
					sortOrder =  s_keys[s]
				if majorkey == 'SHOW':
					show =  str(s_keys[s])
			
			t_f = t_f & f
		products = products.filter( t_f )	
						
	# Apply keyword filter (through ajax or search)
	for word in keywords:
		products = products.filter( 
			Q(key_words__icontains = word) |
			Q(artist__icontains = word)
		)

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


	slab_0_50 = 'NO'
	slab_50_100 = 'NO'
	slab_100_150 = 'NO'
	slab_150_200 = 'NO'
	slab_200_plus = 'NO'
	
	sliced_count = 0
	total_count = products.count()
	if total_count > 50000 and result_limit != '0-50':		
		slab_0_50 = 'YES'
	if total_count > 50000 and result_limit != '50-100':		
		slab_50_100 = 'YES'
	if total_count > 100000 and result_limit != '100-150':
		slab_100_150 = 'YES'
	if total_count > 150000  and result_limit != '150-200':		
		slab_150_100 = 'YES'
	if total_count > 200000  and result_limit != '200+':
		slab_200_plus = 'YES'


	if result_limit == '0-50':
		products = products[:50000]
	elif result_limit == '50-100':
		products = products[50001:100000]
	elif result_limit == '100-150':
		products = products[100001:150000]
	elif result_limit == '150-200':
		products = products[150001:200000]
	elif result_limit == '200+':
		products = products[200001:]

	sliced_count = products.count()
	print(result_limit)




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
				
	paginator = Paginator(products, perpage) 
	if not page:
		page = request.GET.get('page')
	prods = paginator.get_page(page)		

	#=====================
	index = prods.number - 1 
	max_index = len(paginator.page_range)
	start_index = index - 5 if index >= 5 else 0
	end_index = index + 5 if index <= max_index - 5 else max_index
	page_range = list(paginator.page_range)[start_index:end_index]
	#=====================
		
	if request.is_ajax():

		template = "artevenue/prod_display_include.html"
	else :
		template = "artevenue/category_products.html"

	return render(request, template, {'prod_categories':prod_categories, 
		'category_prods': category_prods, 'product_category':product_cate, 
		'products':products, 'prods':prods, 'sortOrder':sortOrder, 'show':show,'prod_filters':prod_filters,
		'prod_filter_values':prod_filter_values, 'price':price,
		'width':width, 'height':height, 'page_range':page_range, 'total_count':total_count,
		'sliced_count':sliced_count, 'result_limit':result_limit, 'slab_0_50':slab_0_50,
		'slab_50_100':slab_50_100, 'slab_100_150':slab_100_150, 'slab_150_200':slab_150_200,
		'slab_200_plus':slab_200_plus} )
		
@csrf_exempt		
def curated_collections(request, cat_nm=None, page = None,  prod_id=None, ):
	cat_nm = cat_nm.replace("-", " ")

	if page is None:
		page = request.GET.get("page_num", 1)

	if page is None or page == 0:
		page = 1 # default

	sortOrder = request.GET.get("sort")
	show = request.GET.get("show", "100")
	result_limit = request.GET.get("result_limit", "0-50")
	filt_colors = request.GET.get("filt_colors", "")
	colors = filt_colors.split('|')
	
	filt_size = request.GET.get("filt_size", "")
	filt_width = request.GET.get("filt_width", "")
	filt_height = request.GET.get("filt_height", "")
	filt_artist = request.GET.get("filt_artist", "")
	artists = filt_artist.split('|')
	
	filt_orientation = request.GET.get("filt_orientation", "")
	orientation = filt_orientation.split('|')

	filt_image_type = request.GET.get("filt_image_type", "")
	image_type = filt_image_type.split('|')

	if cat_nm:
		try:
			product_cate = Curated_category.objects.get(name = cat_nm);
			cat_id = product_cate.category_id
		except Curated_category.DoesNotExist:
			product_cate = {}
			cat_id = 0
		except Curated_category.MultipleObjectsReturned:
			product_cate = {}
			cat_id = 0

		try:
			cat_p = Stock_image_category.objects.get(name = cat_nm);
			cat_id_p = cat_p.category_id	## Only used for setting category display priority
		except Stock_image_category.DoesNotExist:
			cat_id_p = 0
		except Stock_image_category.MultipleObjectsReturned:
			cat_id_p = 0
		
	else:
		cat_id = 0
		product_cate = None

	if cat_id == None:
		return
	ikeywords = request.GET.get('keywords', '')
	keywords = ikeywords.split()
	keyword_filter = False # Turned on only if a keyword filter is present (through the AJAX call)

	sortOrder = request.GET.get("sort")
	show = request.GET.get("show")
	
	if prod_id:
		## remove earlier priority, if any
		p_c = Stock_image_stock_image_category.objects.filter(
			stock_image_category_id = cat_id_p,
			stock_image__category_disp_priority = -2).values_list('stock_image_id', flat=True)
			
		prod_u = Stock_image.objects.filter(category_disp_priority = -2, 
			product_id__in = p_c).update(category_disp_priority = None)

		## set priority for current product
		prod_ups = Stock_image.objects.filter(product_id = prod_id).update(
			category_disp_priority = -2)
	
	prod_categories = Stock_image_category.objects.filter(store_id=settings.STORE_ID, trending = True )
	
	curated_coll = Curated_collection.objects.filter(curated_category_id = cat_id,
			product_type_id = 'STOCK-IMAGE', product__is_published = True).values('product_id')

	products = Stock_image.objects.filter(product_id__in = curated_coll).order_by('category_disp_priority')
	
	'''
	dt =  today.day
	if dt >= 1 and dt <= 5:
		products = products.order_by('category_disp_priority', 'key_words')
	elif dt > 5 and dt <= 10:
		products = products.order_by('category_disp_priority', 'product_id')
	elif dt > 10 and dt <= 20:
		products = products.order_by('category_disp_priority', 'name')
	else:
		products = products.order_by('category_disp_priority', 'part_number')
	'''

	
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
		products = products.filter( 
			Q(key_words__icontains = word) |
			Q(artist__icontains = word)
		)

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
				
	paginator = Paginator(products, perpage) 
	if not page:
		page = request.GET.get('page')

	prods = paginator.get_page(page)

	#=====================
	index = prods.number - 1 
	max_index = len(paginator.page_range)
	start_index = index - 5 if index >= 5 else 0
	end_index = index + 5 if index <= max_index - 5 else max_index
	page_range = list(paginator.page_range)[start_index:end_index]
	#=====================
		
	if request.is_ajax():

		template = "artevenue/prod_display_include.html"
	else :
		template = "artevenue/curated_products.html"

	env = settings.EXEC_ENV
	return render(request, template, {'prod_categories':prod_categories, 
		'product_category':product_cate, 
		'products':products, 'prods':prods, 'sortOrder':sortOrder, 'show':show,'prod_filters':prod_filters,
		'prod_filter_values':prod_filter_values, 'price':price, 'show_artist':True,
		'width':width, 'height':height, 'page_range':page_range, 'env':env,
		'page': page,
		'filt_width':filt_width, 'filt_height':filt_height, 'page_range':page_range,
		'filt_colors':filt_colors, 'filt_size':filt_size, 'filt_artist':filt_artist,
		'filt_orientation':filt_orientation, 'filt_image_type':filt_image_type,
		} )		

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
			if show == '1000':
				perpage = 1000
				show = '1000'
			else:
				show = '50' # default
				perpage = 50
	
	if request.is_ajax():
		paginator = Paginator(products, perpage) 
		
		if not page:
			page = request.POST.get('page')

		prods = paginator.get_page(page)
		#=====================
		index = prods.number - 1 
		max_index = len(paginator.page_range)
		start_index = index - 5 if index >= 5 else 0
		end_index = index + 5 if index <= max_index - 5 else max_index
		page_range = list(paginator.page_range)[start_index:end_index]
		#=====================
	else :
		prods = {}
		page_range = []
	
	return render(request, template,
			{'prods':prods, 'show':show, 'perpage':perpage, 'width':16,
			'page_range':page_range})

def get_stock_images(request, cat_nm = None, page = None, curated_coll_id = None):
	if cat_nm:
		cat_nm = cat_nm.replace("-", " ")
		try:
			product_cate = Stock_image_category.objects.filter(name = cat_nm).first()
			cat_id = product_cate.category_id
		except Stock_image_category.DoesNotExist:
			cat_id = 0
			product_cate = None
		except Stock_image_category.MultipleObjectsReturned:
			cat_id = 0
			product_cate = None		
	else:
		cat_id = 0
		product_cate = None
		
	if page is None:
		page = request.GET.get("page_num", 1)

	sortOrder = request.GET.get("sort")
	show = request.GET.get("show", "100")
	result_limit = request.GET.get("result_limit", "0-50")
	filt_colors = request.GET.get("filt_colors", "")
	colors = filt_colors.split('|')
	
	filt_size = request.GET.get("filt_size", "")
	filt_width = request.GET.get("filt_width", "")
	filt_height = request.GET.get("filt_height", "")
	filt_artist = request.GET.get("filt_artist", "")
	artists = filt_artist.split('|')
	
	filt_orientation = request.GET.get("filt_orientation", "")
	orientation = filt_orientation.split('|')

	filt_image_type = request.GET.get("filt_image_type", "")
	image_type = filt_image_type.split('|')

	ikeywords = request.GET.get('keywords', '')	
	keywords = ikeywords.split()
	keyword_filter = False # Turned on only if a keyword filter is present (through the AJAX call)

	if page is None or page == 0:
		page = 1 # default

	prod_categories = Stock_image_category.objects.filter(store_id=settings.STORE_ID, trending = True )

	if cat_id:
		category_prods = Stock_image_stock_image_category.objects.filter(
				stock_image_category_id = cat_id).values('stock_image_id')
		products = Stock_image.objects.filter(product_id__in = category_prods, 
				is_published = True)
	elif curated_coll_id:
		curated_coll = Curated_collection.objects.filter(curated_category_id = curated_coll_id,
				product_type_id = 'STOCK-IMAGE').values('product_id')
		try:
			product_cate = Curated_category.objects.get(category_id = curated_coll_id);
		except Curated_category.DoesNotExist:
			product_cate = {}
		products = Stock_image.objects.filter(product_id__in = curated_coll, 
			is_published = True)
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
			wishlist_id__in = wishlist, product_type_id = 'STOCK-IMAGE')
	else:
		session_id = request.session.session_key
		wishlist = Wishlist.objects.filter(
			session_id = session_id).values('wishlist_id')
		wishlistitems = Wishlist_item_view.objects.filter(
			wishlist_id__in = wishlist, product_type_id = 'STOCK-IMAGE')

	wishlist_prods = []
	if wishlistitems:
		for w in wishlistitems:
			wishlist_prods.append(w.product_id)
		
	
	###### Apply the user selected filters
	t_f = Q()
	f = Q()

	if filt_size:
		# Get the size
		idx = filt_size.find("_")
		filt_width = int(filt_size[:idx])
		filt_height = int(filt_size[(idx+1):])
		ratio = round(Decimal(filt_width)/Decimal(filt_height), 18)
		#f = f | Q( aspect_ratio = ratio) & Q(max_width__gte = filt_width) & Q(max_height__gte = filt_height)
		products = products.filter(aspect_ratio = ratio, max_width__gte = filt_width, max_height__gte = filt_height)

	t_f = t_f & f 
	
	f = Q()
	for i in image_type :
		if i == '':
			continue
		f = f | Q(image_type = i)

	t_f = t_f & f 
		
	f = Q()
	for o in orientation:
		if o == '':
			continue
		f = f | Q(orientation = o)
	t_f = t_f & f 
	
	f = Q()
	for a in artists:
		if a == '':
			continue	
		f = f | Q(artist = a)
	t_f = t_f & f 
	
	f = Q()
	for c in colors:
		if c == '':
			continue
		f = f | Q(key_words__icontains = c)
	t_f = t_f & f 
	
	print (t_f)
	products = products.filter( t_f )

	# Apply keyword filter (through ajax or search)
	for word in keywords:
		if word == '':
			continue
		products = products.filter( 
			Q(key_words__icontains = word) |
			Q(artist__icontains = word) |
			Q(name__icontains = word) |
			Q(part_number__icontains = word)
			)
		
	'''
	dt =  today.day
	if dt >= 1 and dt <= 5:
		products = products.order_by('category_disp_priority', '?')
	elif dt > 5 and dt <= 10:
		products = products.order_by('category_disp_priority', 'product_id')
	elif dt > 10 and dt <= 20:
		products = products.order_by('category_disp_priority', 'name')
	else:
		products = products.order_by('category_disp_priority', 'part_number')
	'''
	
	products = products.order_by('category_disp_priority')
	
	price = Publisher_price.objects.filter(print_medium_id = 'PAPER') 
	
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
	

	####################################
	####### Limiting the result set
	####################################
	slab_0_50 = 'NO'
	slab_50_100 = 'NO'
	slab_100_150 = 'NO'
	slab_150_200 = 'NO'
	slab_200_plus = 'NO'
	
	sliced_count = 0
	total_count = products.count()
	if total_count > 50000 and result_limit != '0-50':		
		slab_0_50 = 'YES'
	if total_count > 50000 and result_limit != '50-100':		
		slab_50_100 = 'YES'
	if total_count > 100000 and result_limit != '100-150':
		slab_100_150 = 'YES'
	if total_count > 150000  and result_limit != '150-200':		
		slab_150_100 = 'YES'
	if total_count > 200000  and result_limit != '200+':
		slab_200_plus = 'YES'


	if result_limit == '0-50':
		products = products[:50000]
	elif result_limit == '50-100':
		products = products[50001:100000]
	elif result_limit == '100-150':
		products = products[100001:150000]
	elif result_limit == '150-200':
		products = products[150001:200000]
	elif result_limit == '200+':
		products = products[200001:]

	sliced_count = products.count()
	####################################
	####### END: Limiting the result set
	####################################



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
				
	paginator = Paginator(products, perpage) 
	if not page:
		page = request.GET.get('page')
	
	prods = paginator.get_page(page)			
	
	#=====================
	index = prods.number - 1 
	max_index = len(paginator.page_range)
	start_index = index - 5 if index >= 5 else 0
	end_index = index + 5 if index <= max_index - 5 else max_index
	page_range = list(paginator.page_range)[start_index:end_index]
	#=====================
	
	template = "artevenue/art_by_category.html"

	env = settings.EXEC_ENV
	
	return render(request, template, {'prod_categories':prod_categories, 
		'category_prods': category_prods, 'product_category':product_cate, 
		'products':products, 'prods':prods, 'sortOrder':sortOrder, 'show':show,'prod_filters':prod_filters,
		'prod_filter_values':prod_filter_values, 'price':price, 'ikeywords':ikeywords,
		'page':page, 'wishlistitems':wishlistitems, 'wishlist_prods':wishlist_prods,
		'filt_width':filt_width, 'filt_height':filt_height, 'page_range':page_range, 'result_limit':result_limit,
		'filt_colors':filt_colors, 'filt_size':filt_size, 'filt_artist':filt_artist,
		'filt_orientation':filt_orientation, 'filt_image_type':filt_image_type,
		'total_count':total_count, 'sliced_count':sliced_count, 'result_limit':result_limit,
		'slab_0_50':slab_0_50, 'slab_50_100':slab_50_100, 'slab_100_150':slab_100_150, 
		'slab_150_200':slab_150_200, 'slab_200_plus':slab_200_plus, 'env':env} )

@csrf_exempt		
def original_art_by_category(request, cat_id = '', page = 1):
	ikeywords = request.GET.get('keywords', '')
	keywords = ikeywords.split()
	keyword_filter = False # Turned on only if a keyword filter is present (through the AJAX call)
	sortOrder = request.GET.get("sort")
	show = request.GET.get("show", '50')
	
	if page is None or page == 0:
		page = 1 # default

	prod_categories = Original_art_original_art_category.objects.filter(
		stock_image_category__store_id=settings.STORE_ID, 
		stock_image_category__trending = True )

	if cat_id:
		category_prods = Original_art_original_art_category.objects.filter(
				stock_image_category_id = cat_id).values('original_art_id')
		
		product_cate = get_object_or_404 (Stock_image_category, category_id = cat_id)
	else :
		category_prods = Original_art_original_art_category.objects.values('original_art_id')		
		product_cate = {}
		
	products = Original_art.objects.filter(product_id__in = category_prods, 
				is_published = True)

	if request.user.is_authenticated:
		user = User.objects.get(username = request.user)
		wishlist = Wishlist.objects.filter(
			user = user).values('wishlist_id')
		wishlistitems = Wishlist_item_view.objects.filter(
			wishlist_id__in = wishlist, product_type_id = 'ORIGINAL-ART')
	else:
		session_id = request.session.session_key
		wishlist = Wishlist.objects.filter(
			session_id = session_id).values('wishlist_id')
		wishlistitems = Wishlist_item_view.objects.filter(
			wishlist_id__in = wishlist, product_type_id = 'ORIGINAL-ART')

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
		products = products.filter( 
			Q(key_words__icontains = word) |
			Q(artist__icontains = word)
			)
		
	dt =  today.day
	if dt >= 1 and dt <= 5:
		products = products.order_by('?')
	elif dt > 5 and dt <= 10:
		products = products.order_by('product_id')
	elif dt > 10 and dt <= 20:
		products = products.order_by('name')
	else:
		products = products.order_by('part_number')


	prod_filters = ['ORIENTATION', 'ARTIST', 'COLORS']	
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
			if show == '1000':
				perpage = 1000
				show = '1000'
			else:
				show = '50' # default
				perpage = 50
				
	paginator = Paginator(products, perpage) 
	if not page:
		page = request.GET.get('page')
	
	prods = paginator.get_page(page)			
	
	#=====================
	index = prods.number - 1 
	max_index = len(paginator.page_range)
	start_index = index - 5 if index >= 5 else 0
	end_index = index + 5 if index <= max_index - 5 else max_index
	page_range = list(paginator.page_range)[start_index:end_index]
	#=====================
	
	if request.is_ajax():

		template = "artevenue/prod_display_include_orginal_art.html"
	else :
		template = "artevenue/original_art_by_category.html"
		#template = "artevenue/art_by_category.html"

	return render(request, template, {'prod_categories':prod_categories, 
		'category_prods': category_prods, 'product_category':product_cate, 
		'products':products, 'prods':prods, 'sortOrder':sortOrder, 'show':show,'prod_filters':prod_filters,
		'prod_filter_values':prod_filter_values, 'price':price, 'ikeywords':ikeywords,
		'page':page, 'wishlistitems':wishlistitems, 'wishlist_prods':wishlist_prods,
		'width':width, 'height':height, 'page_range':page_range} )

def original_art_detail(request, prod_id = ''):
	cart_item_id = request.GET.get("cart_item_id", "")
	wishlist_item_id = request.GET.get("wishlist_item_id", "")
	if not prod_id or prod_id == '' :
		prod_id = request.GET.get("product_id", "")
	
	if prod_id == None:
		return
	

	# get the product
	product = get_object_or_404(Original_art, is_published = True, pk=prod_id)
		
	product_category = Original_art_original_art_category.objects.get(original_art = product)
	
	prod_categories = Original_art_original_art_category.objects.filter(
		stock_image_category__store_id=settings.STORE_ID)
	
	printmedium = Print_medium.objects.all()

	##############################################
	## Get the similar products
	##############################################
	similar_products = {}
	## First get rpoducts by same artist
	similar_products_artist = Original_art.objects.filter(  
			artist = product.artist).exclude(product_id = prod_id)
	## If same artist has more than 8 products, then filter further
	if similar_products_artist:
		if similar_products_artist.count() > 8 :
			## Filter for the same artist and same category
			prods_in_cat = Original_art_original_art_category.objects.filter(
				stock_image_category_id = product_category.stock_image_category).values('stock_image_id')
				
			similar_products_cat = similar_products_artist.filter(
				product_id__in = prods_in_cat)
			## Same artist has more than 8 products in same category, filter further
			if similar_products_cat: 
				if similar_products_cat.count() > 8 :
					## Filter for having same key words
					similar_products_kw = similar_products_cat.filter( key_words__in = product.key_words )
					if similar_products_kw :
						if similar_products_kw.count() > 8:
							similar_products = similar_products_kw
						else :
							similar_products = similar_products_cat.filter(
								product_id__in = prods_in_cat)
					else:
						similar_products = similar_products_cat.filter(
							product_id__in = prods_in_cat)
						
				## if the filter causes the result to be empty, revert to earlier filter
				else:
					similar_products = Original_art.objects.filter(  
							artist = product.artist)
			else :
					similar_products = Original_art.objects.filter(  
						artist = product.artist)
		else:
			similar_products = Original_art.objects.filter(  
					artist = product.artist)

	## Restrict the result to 10 products
	if similar_products:
		if similar_products.count() > 8:
			similar_products = similar_products[:8]

	price = Publisher_price.objects.filter(print_medium_id = 'PAPER') 


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

	art_width = product.art_width
	art_height = product.art_height
	return render(request, "artevenue/original_art_detail.html", {'product':product,
		'prod_categories':prod_categories, 'printmedium':printmedium, 'product_category':product_category,
		'mouldings_apply':paper_mouldings_apply, 'mouldings_show':paper_mouldings_show, 'mounts':mounts,
		'per_sqinch_paper':per_sqinch_paper, 'per_sqinch_canvas':per_sqinch_canvas, 'acrylics':acrylics,
		'boards':boards, 
		#######'img_with_all_mouldings':img_with_all_mouldings, 
		'stretches':stretches,
		'cart_item':cart_item_view, 'art_width':art_width, 'art_height':art_height,
		'prods':similar_products, 'price':price, 'wishlist_prods':wishlist_prods} )

@csrf_exempt
def get_ready_products(request, prod_id=None, prod_width=None, print_medium=None):
	
	if prod_id == None:
		prod_id = int(request.POST.get('prod_id', '0'))
		
	if prod_width == None:
		prod_width = Decimal(request.POST.get('prod_width', '0'))
	
	if print_medium == None:
		print_medium = request.POST.get('print_medium', 'PAPER')
			
	
	## Common components
	acrylic_id = 1
	moulding_id = 18  # Simple Black
	if print_medium == 'PAPER':
		mount_id = 3 # Offwhite
		mount_color = '#fffff0'  # Offwhite
		mount_size = 1 if prod_width <= 24 else 2 if prod_width <= 42 else 3
		moulding_id = 18 if prod_width <= 24 else 24 
		board_id = 1
	else:
		mount_id = 0
		mount_color = ''  
		mount_size = 0
		board_id = 0
		
	stretch_id = 1
	
	# Get Product
	product = Stock_image.objects.get( product_id = prod_id )
	env = settings.EXEC_ENV

	if env == 'DEV' or env == 'TESTING':	
		response = requests.get(product.url)
		img_source = Image.open(BytesIO(response.content))
	else:
		img_source = Image.open(settings.PROJECT_DIR + '/' + settings.STATIC_URL + product.url)			
	
	# Get moulding
	moulding = Moulding_image.objects.filter(moulding_id = moulding_id, image_type = "APPLY").values(
				'url', 'moulding__width_inches', 'border_slice').first()
	
	if moulding:	
		m_width_inch = float(moulding['moulding__width_inches'])
		
		# Image width displayed in browser in inches
		disp_inch = 450//96
		
		ratio = float(disp_inch / prod_width)
		
		border = int(m_width_inch * ratio* 96)		
		#border = int(m_width_inch * 96/ user_width)
		
		m_size = int(mount_size * 96 * ratio)
		#m_size = int(mount_size * 960 / user_width)
		
		if m_size > 0 and mount_color != '' and mount_color != '0' and mount_color != 'None':

			img_with_mount = addMount(img_source, mount_color, m_size, m_size, m_size, m_size)
			
			framed_img = applyBorder( request, img_with_mount, moulding['url'], border, border, border, border,
							float(moulding['border_slice']), float(moulding['border_slice']), 
							float(moulding['border_slice']), float(moulding['border_slice']) )
		else:
			framed_img = applyBorder( request, img_source, moulding['url'], border, border, border, border,
							float(moulding['border_slice']), float(moulding['border_slice']), 
							float(moulding['border_slice']), float(moulding['border_slice']) )
	else :
		# No moulding, returing the image as it is.
		framed_img = Image.new("RGB", (img_source.width, img_source.height), 0)
		framed_img.paste(img_source, (0,0))		
	'''
	response = HttpResponse(content_type="image/png")
	framed_img.save(response, "PNG")
	return response
	#return framed_img
	'''
	
	##framed_img = dropShadow(framed_img)

	buffered = BytesIO()
	framed_img.save(buffered, format='JPEG')
	img_data = buffered.getvalue()
	img_str = base64.b64encode(img_data)


	return HttpResponse(img_str)