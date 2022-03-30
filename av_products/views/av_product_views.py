from django.shortcuts import render, get_object_or_404
from django.conf import settings
from django.core.paginator import EmptyPage, PageNotAnInteger, Paginator
from django.views.decorators.csrf import csrf_protect, csrf_exempt
from django.db.models import Count, Q, F
from django.contrib.auth.decorators import login_required
from artevenue.decorators import is_manager, has_accounts_access	
from django.views.decorators.csrf import csrf_exempt
from django.db import IntegrityError, DatabaseError, Error
from django.contrib.admin.views.decorators import staff_member_required
from django.http import HttpRequest
from django.core.exceptions import ObjectDoesNotExist
from django.http import JsonResponse

from django.contrib.auth.models import User

from datetime import datetime
import datetime
from decimal import Decimal
import json
import statistics
from PIL import Image
import random
import string

from artevenue.views import frame_views, price_views, tax_views

from av_products.models import Av_product, Av_product_varient, Av_product_varient_image, Av_product_varient_article, Av_product_varient_article_image
from artevenue.models import Ecom_site, Stock_image, Stock_image_category
from artevenue.models import Print_medium, Publisher_price, Stretch
from artevenue.models import Wishlist, Wishlist_item_view, Collage_stock_image, Cart_item_view

today = datetime.date.today()
env = settings.EXEC_ENV


@csrf_exempt		
def show_av_products(request, set_of=None, page = 1):	

	singles = request.GET.get("singles", 'NO')
	show  = request.GET.get("show", 0)
	sortOrder = request.GET.get("sort", '')
	i_color = request.GET.get("color", "").split(',')	
	i_category = request.GET.get("category", "").split(',')
	if not set_of:
		i_set_of = request.GET.get("set_of", '').split(',')
	page = request.GET.get("page", 1)
	ikeywords = request.GET.get('keywords', '')	
	keywords = ikeywords.split()
	keyword_filter = False # Turned on only if a keyword filter is present (through the AJAX call)

	filt_applied = False
	f_color = []
	for c in i_color:
		if c != '':
			f_color.append(c)
			filt_applied = True
	f_category = []
	for c in i_category:
		if c != '':
			f_category.append(c)
			filt_applied = True
	
	f_set_of = []
	if not set_of:		
		for s in i_set_of:
			if s != '':
				f_set_of.append(s)
				filt_applied = True
	else:
		f_set_of.append(set_of)
		filt_applied = True


	if page is None or page == 0:
		page = 1 #default

	if singles == 'NO':
		sets = Av_product_varient.objects.filter(product__is_published = True, is_parent=True, product__set_of__gte = 1).order_by('product__category_disp_priority', 
				'-product__updated_date')
	else:
		sets = Av_product_varient.objects.filter(product__is_published = True, is_parent=True, product__set_of = 1).order_by('product__category_disp_priority', 
				'-product__updated_date')
				
	## Get Prices
	prices = {}
	for s in sets:
		price = get_varient_price_stretched_canvas(s.product_varient_id)
		prices[s.product_varient_id] = price['item_price']
    
	if f_set_of :
		if len(f_set_of) > 0 :
			sets = sets.filter(set_of__in = f_set_of)
	if f_color :
		if len(f_color) > 0 :
			fc = Q()
			for c in f_color:
				fc = fc | Q(colors__icontains = c)				
			sets = sets.filter(fc)
	if f_category :
		if len(f_category) > 0 :
			sets = sets.filter(stock_image_category__name__in = f_category)

	if singles == 'NO':
		cate = Av_product_varient.objects.filter(
			product__is_published = True, is_parent=True, product__set_of__gt = 1).values_list('product__stock_image_category__name', flat=True).distinct()
	else:
		cate = Av_product_varient.objects.filter(
			product__is_published = True, is_parent=True, product__set_of = 1).values_list('product__stock_image_category__name', flat=True).distinct()
		
	categories_list = []
	for c in cate:
		categories_list.append( c )

	# Apply keyword filter (through ajax or search)
	for word in keywords:
		sets = sets.filter( key_words__icontains = word )
		
	if sortOrder == "L2H":
		sets = sets.order_by('price')
	elif sortOrder == "H2L":
		sets = sets.order_by('-price')
		
	shape_list = ['Vertical', 'Horizontal', 'Square']
	
	colors_list = ['Red', 'Gold', 'Orange',  'Yellow', 'Green', 'Blue', 'Purple', 'Pink', 'Brown', 'black', 'grey', 'White']



	sets_of_list = [2, 3]


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
				
	paginator = Paginator(sets, perpage) 
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

		template = "av_products/av_products_display_include.html"
	else :
		template = "av_products/av_products_list.html"
		
	return render(request, template,
			{'prods':coll, 'wishlist_prods':wishlist_prods, 'prices': prices,
			'page':page, 'wishlistitems':wishlistitems,
			'sortOrder':sortOrder, 'show':show, 'filt_applied': filt_applied,
			'colors_list': colors_list, 'categories_list': categories_list,
			'sets_of_list': sets_of_list, 'ikeywords':ikeywords, 'page':page, 'env': env,
			'f_set_of': f_set_of, 'f_category': f_category, 'f_color': f_color,
			'is_set': 'TRUE', 'singles': singles})


@csrf_exempt
def get_av_prod_price(request):

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
	
	
	
def av_product_page(request, varient_id=''):

	cart_item_id = request.GET.get("cart_item_id", "")
	wishlist_item_id = request.GET.get("wishlist_item_id", "")
	
	if varient_id == '':
		varient_id = request.GET.get('varient_id','')

	if varient_id:
		selected_product_varient = Av_product_varient.objects.filter(product_varient_id = varient_id).first()     
		product_id = selected_product_varient.product_id
		if not selected_product_varient:
			return render(request, "av_products/av_curve_wallart_product_page.html", {'product':{}, "product_varients" : {},
				'parent_varient':{}, 'varient_id' : '', 'cart_item':{}, 'prices':{}, 
				'wishlist_prods':{}, 'wishlist_item':{}, 'ENV':settings.EXEC_ENV,} )
	else:
		return render(request, "av_products/av_curve_wallart_product_page.html", {'product':{}, "product_varients" : {},
			'parent_varient':{}, 'varient_id' : '', 'cart_item':{}, 'prices':{}, 
			'wishlist_prods':{}, 'wishlist_item':{}, 'ENV':settings.EXEC_ENV,} )

	## Get all varients
	product_varients = Av_product_varient.objects.filter(product_id = product_id)
	
	if not product_id:	
		product_id = request.GET.get("product_id", "")
		
	# get the product
	product = Av_product.objects.filter(is_published = True, pk=product_id).first()	
	
	if not product:
		return render(request, "av_products/av_curve_wallart_product_page.html", {'product':{}, "product_varients" : {},
			'parent_varient':{}, 'varient_id' : '', 'cart_item':{}, 'prices':{}, 
			'wishlist_prods':{}, 'wishlist_item':{}, 'ENV':settings.EXEC_ENV,} )
	
	
	parent_varient = Av_product_varient.objects.filter(product_id = product_id, is_parent=True).first()
	
	parent_varient_image_ls = Av_product_varient_image.objects.filter(product_varient_id = parent_varient.product_varient_id,
		image_type = 'LS').first()
		
	product_varient_images = Av_product_varient_image.objects.filter(product_varient__product_id = product)
	
	product_varient_articles = Av_product_varient_article.objects.filter(product = product, product_varient = parent_varient)
	
	product_varient_article_images = Av_product_varient_article_image.objects.filter(product_varient_article__in = product_varient_articles,
		image_type = 'PR')
	
	prices = {}
	for v in product_varients:
		price = 0
		if v.product_varient_id:
			price = get_varient_price_stretched_canvas(v.product_varient_id)
			item_price = price['item_price']
			msg = price['msg']
			cash_disc = price['cash_disc']
			percent_disc = price['percent_disc']
			item_price_withoutdisc = price['item_price_without_disc']
			disc_amt = price['disc_amt']
			disc_applied = price['disc_applied']
			promotion_id = price['promotion_id']			
			
		if price == 0:
			continue
		prices[v.image_width] = price
		
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

	return render(request, "av_products/av_curve_wallart_product_page.html", {'product':product, "product_varients" : product_varients,
		'parent_varient':parent_varient, 'varient_id' : varient_id, 'cart_item':cart_item_view, 'prices':prices,
		'parent_varient_image_ls': parent_varient_image_ls, 'product_varient_images': product_varient_images,
		'product_varient_articles': product_varient_articles,
		'product_varient_article_images': product_varient_article_images, 'cart_item': cart_item_view,
		'wishlist_prods':wishlist_prods, 'wishlist_item':wishlist_item_view, 'ENV':settings.EXEC_ENV,} )
	


def get_varient_price_stretched_canvas(product_varient_id=None):
	product_varient = Av_product_varient.objects.filter(product_varient_id = product_varient_id).first()

	if product_varient:
		prod_type = 'STOCK-IMAGE'
		image_price = 0
		item_price = 0
		articles = Av_product_varient_article.objects.filter(product_varient = product_varient)

		for s in articles:
			i_price = 0            
			per_sqinch_price = price_views.get_per_sqinch_price(s.stock_image_id, prod_type)
			per_sqinch_canvas = per_sqinch_price['per_sqin_canvas']	
			
			# Image Price			
			if product_varient.image_width:
				if product_varient.image_width > 0 and product_varient.image_height > 0:
					msg = "SUCCESS"
				else :
					msg = "ERROR-Image size missing"

			i_price = price_views.get_price_reduction_by_size(per_sqinch_canvas, product_varient.image_width * product_varient.image_height)
			## Apply any special prices
			if prod_type == 'STOCK-IMAGE':
				prod = Stock_image.objects.filter(product_id = s.stock_image_id).first()
				i_price = price_views.apply_special_price(prod, i_price)

			## Price for round shaped is stretch price with width taken 2 times.
			str_price = (product_varient.image_width*2 + product_varient.image_height) * 2 * frame_views.get_stretch_price_by_id(product_varient.product.stretch_id)
			i_price = Decimal(i_price + str_price)
			item_price = item_price + i_price
		
	image_price = Decimal(round(float(item_price),-1))
	item_price_without_disc = image_price
	
	disc_applied = False
	promo = {}
		
	disc_amt = 0
	cash_disc = 0
	percent_disc = 0
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


	###############################
	## Unit price (without tax)
	###############################
	# Get Tax
	item_tax = 0
	taxes = tax_views.get_taxes()

	if prod_type == 'STOCK-IMAGE':
		tax_rate = taxes['stock_image_tax_rate']
	if prod_type == 'ORIGINAL-ART':
		tax_rate = taxes['original_art_tax_rate']
	if prod_type == 'USER-IMAGE':
		tax_rate = taxes['user_image_tax_rate']
	if prod_type == 'STOCK-COLLAGE':
		tax_rate = taxes['stock_image_tax_rate']
	if prod_type == 'FRAME':
		tax_rate = taxes['frame_tax_rate']
	
	item_unit_price = round( item_price / (1 + (tax_rate/100)), 2 )

	return ({"msg":msg, "item_price" : item_price, 'cash_disc':cash_disc,
				'percent_disc':percent_disc, 'item_unit_price':item_unit_price,
				'disc_amt':disc_amt, 'disc_applied':disc_applied, 'promotion_id':promotion_id,
				'item_price_without_disc':item_price_without_disc})		
				
				
				

@csrf_exempt
@is_manager	
def create_set_single_round_artwork(request):
	return render(request, "av_products/create_set_single_round_artwork.html", {})

@csrf_exempt
@is_manager	
def set_single_data_round_artwork(request):
	set_of = request.GET.get("set_of", '')
	
	printmedium = ['CANVAS']
	price = Publisher_price.objects.filter(print_medium_id = 'CANVAS') 


	# get Stretches
	stretches = Stretch.objects.all()
	
	return render(request, "av_products/set_single_data_round_artwork.html", {'set_of':set_of, 'set_range': range(int(set_of)), 
		'printmedium':printmedium, 'stretches':stretches, 'env':settings.EXEC_ENV})

@csrf_exempt
@is_manager	
def save_set_single_round_artwork(request):
	err_cd = '00'
	msg = ''
	
	set_of = int(request.POST.get('set_of', '0'))
	prod_name = request.POST.get('name', '')
	desc = request.POST.get('desc', '')

	prod_arr = request.POST.get('prod_arr', '').split(',')
	image_width = request.POST.get('image_width', )
	image_height = request.POST.get('image_height', )
	category_id_str = request.POST.get('category_id_str', '').split(',')
	print_medium = request.POST.get('print_surface', '')
	stretch_id = request.POST.get('stretch_id', '')
	aspect_ratio =  Decimal(request.POST.get('aspect_ratio', '0'))
	duplicate_image = request.POST.get('duplicate_image', 'NO')
	
	max_width = 0
	for p in prod_arr:
		if p:
			prd = Av_product_varient_article.objects.filter(stock_image_id = int(p), 
				product__is_published = True).first()
			if prd:
				pmax_width = prd.stock_image.max_width
			else :
				pmax_width = 10
			if max_width == 0:
				max_width = pmax_width
			elif max_width > pmax_width:
				max_width = pmax_width
			if duplicate_image == 'NO':
				if prd:
					err_cd = '01'
					msg = "A set/single # " + str(prd.stock_collage.product_id) + " has already been created with image ID: " + str(prd.stock_image_id) + ". Do you wish to still proceed?"
					return( JsonResponse({'err_cd': err_cd, 'msg': msg }, safe=False) )					

	if print_medium == 'PAPER':
		stretch_id = None
	elif print_medium == 'CANVAS':
		stretch_id = 1

	orientation = ''
	if aspect_ratio != 0:
		if aspect_ratio > 1:
			orientation = 'Horizontal'
		elif aspect_ratio < 1:
			orientation = 'Vertical'
		else:
			orientation = 'Square'

	name = request.POST.get('name', '')
	colors = request.POST.get('colors', '')
	keywords = request.POST.get('keywords', '')

	try:
		im = request.FILES.get('file1', None)
		if im:
			img = Image.open(im)
			img = img.resize( (1000, 1000) )
			img_thumb = img.resize( (350, 350) )
			r = ''.join(random.choice(string.ascii_uppercase + string.digits) for _ in range(6))
			file_nm =  r + '.jpg'
			file_nm_thumb =  r + '_thumb.jpg'
			env = settings.EXEC_ENV
			if env == 'DEV' or env == 'TESTING':
				img_loc = settings.BASE_DIR + "/artevenue" + settings.STATIC_URL + 'img/round_artworks/' + file_nm
				thumb_img_loc = settings.BASE_DIR + "/artevenue" + settings.STATIC_URL + 'img/round_artworks/' + file_nm_thumb
				
			else:
				img_loc = settings.PROJECT_DIR + '/' + settings.STATIC_URL  + 'img/round_artworks/' + file_nm
				thumb_img_loc = settings.PROJECT_DIR + '/' + settings.STATIC_URL  + 'img/round_artworks/' + file_nm_thumb
			
			img.save(img_loc)
			img_thumb.save(thumb_img_loc)
			
	except Error as e:
		err_cd = "99"
		msg = "System error has occured while saving roomview file. Can't proceed."
		return( JsonResponse({'err_cd': err_cd, 'msg': msg }, safe=False) )					
				
	url = 'img/round_artworks/' + file_nm
	thumbnail_url = 'img/round_artworks/' + file_nm_thumb
	display_url = 'img/round_artworks/' + file_nm
	display_thumbnail_url = 'img/round_artworks/' + file_nm_thumb
	price = 0

	
	for i in category_id_str:
		category_id = i

	prod_type = 'NON-RECTANGULAR'

	try:
		avp = Av_product(
			product_type_id = prod_type,
			shape = 'RD',
			title = prod_name,
			desc = desc,
			is_published = True,
			category_disp_priority = None,
			is_set = True,
			set_of = set_of,
			is_same_size = True,
			is_same_shape = True,
			stock_image_category_id = category_id,
			featured = False,
			aspect_ratio = aspect_ratio,
			image_type =  None,
			orientation = orientation,
			max_width = max_width,
			max_height = round(max_width / aspect_ratio),
			min_width = 8,
			min_height = 8,
			publisher = None,
			artist = None,
			colors = colors,
			key_words = keywords,
			print_medium_id = print_medium,
			moulding = None,
			mount = None,
			mount_size = 0,
			acrylic = None,
			board = None,
			stretch_id = stretch_id,
			display_url = display_url
		)
		avp.save()
	except Error as e:
		err_cd = "99"
		msg = "System error has occured while saving product data. Can't proceed. \n" + e.message
		return( JsonResponse({'err_cd':err_cd, 'msg': msg }, safe=False) )


	## Create image for shoing in cart, order
	cart_img = Image.new("RGBA", (350 * len(prod_arr) + (len(prod_arr)-1)*20, 350), (255, 0, 0, 0))
	i = 0
	x = 0
	p_img_loc_arr = []
	p_img_thumb_loc_arr = []
	for p in prod_arr:
		i = i + 1        
		try:
			im = request.FILES.get('img_'+str(i), None)
			if im:
				img = Image.open(im)
				img = img.resize( (1000, 1000) )
				img_thumb = img.resize( (350, 350) )
				#r = ''.join(random.choice(string.ascii_uppercase + string.digits) for _ in range(6))
				file_nm =  str(p) + '_img_'+str(i) + '.png'
				file_nm_thumb =  str(p) + '_img_'+str(i) + '_thumb.png'
				env = settings.EXEC_ENV
				if env == 'DEV' or env == 'TESTING':
					img_loc = settings.BASE_DIR + "/artevenue" + settings.STATIC_URL + 'img/round_artworks/' + file_nm
					thumb_img_loc = settings.BASE_DIR + "/artevenue" + settings.STATIC_URL + 'img/round_artworks/' + file_nm_thumb
					img.save(img_loc, "PNG")
					img_thumb.save(thumb_img_loc, "PNG")					
				else:
					img_loc = 'img/round_artworks/' + file_nm
					thumb_img_loc = 'img/round_artworks/' + file_nm_thumb
					img.save(settings.PROJECT_DIR + settings.STATIC_URL  + img_loc, "PNG")
					img_thumb.save(settings.PROJECT_DIR + settings.STATIC_URL  + thumb_img_loc, "PNG")					
				

				p_img_loc_arr.append(img_loc)
				p_img_thumb_loc_arr.append(thumb_img_loc)
				cart_img.paste(img_thumb, (x, 0))
				first = False
				x = x + 370
			
			cart_file_nm = 'p_'+str(avp.product_id) + '.png'
			if env == 'DEV' or env == 'TESTING':
				cart_img_loc = settings.BASE_DIR + "/artevenue" + settings.STATIC_URL + 'img/round_artworks/' + cart_file_nm
				cart_img.save(cart_img_loc, "PNG")
			else:
				cart_img_loc = 'img/round_artworks/' + cart_file_nm			
				cart_img.save(settings.PROJECT_DIR + settings.STATIC_URL  + cart_img_loc, "PNG")
			
				
		except Error as e:
			err_cd = "99"
			msg = "System error has occured while saving individual product image. Can't proceed. \n" + e.message
			return( JsonResponse({'err_cd': err_cd, 'msg': msg }, safe=False) )			


	sizes = [12, 18, 24, 30, 36]

	## Create variants
	for s in sizes:
		if s==12:
			is_parent = True
		else:
			is_parent = False

		try:
			variant = Av_product_varient (
				product = avp,
				is_parent = is_parent,
				mount_size = 0,
				image_width = s,
				image_height = s,
				product_varient_size_uom = 'DIAMETER',
				product_varient_size = str(s),
				price = None,
				url = cart_img_loc,
				thumbnail_url = cart_img_loc,
			)
			variant.save()
		except Error as e:
			err_cd = "99"
			msg = "System error has occured while saving variant data. Can't proceed. \n" + e.message	
			return( JsonResponse({'err_cd':err_cd, 'msg': msg }, safe=False) )

		## Variant Images
		try:
			v_img = Av_product_varient_image(
				product_varient = variant,
				image_type = 'LS',
				image_url = display_url,
				image_thumbnail_url = display_thumbnail_url,
			)
			v_img.save()
		except Error as e:
			err_cd = "99"
			msg = "System error has occured while saving variant image data. Can't proceed. \n" + e.message	
			return( JsonResponse({'err_cd':err_cd, 'msg': msg }, safe=False) )

		## Create articles in each variant
		cnt=0
		for p in prod_arr:
			try:
				article = Av_product_varient_article(
					product = avp,
					product_varient = variant,
					aspect_ratio = aspect_ratio,
					image_width = s,
					image_height = s,
					size_uom = 'DIAMETER',
					size = str(s),
					colors = colors,
					key_words = keywords,
					print_medium_id = print_medium,
					moulding = None, 
					mount = None, 
					mount_size = 0,
					acrylic = None, 
					board = None, 
					stretch_id = stretch_id,
					stock_image_id = p
				)
				article.save()
				
			except Error as e:
				err_cd = "99"
				msg = "System error has occured while saving article data. Can't proceed. \n" + e.message
			
			cnt = cnt+1
			
			## Artcile Images
			try:
				avpi = Av_product_varient_article_image(
					product_varient_article = article,
					image_type = 'PR',
					image_url = p_img_loc_arr[cnt-1],
					image_thumbnail_url = p_img_thumb_loc_arr[cnt-1],
					)
				avpi.save()
			except Error as e:
				err_cd = "99"
				msg = "System error has occured while saving individual product data. Can't proceed. \n" + e.message
				return( JsonResponse({'err_cd': err_cd, 'msg': msg }, safe=False) )			
		   
	return( JsonResponse({'err_cd':err_cd, 'msg': msg }, safe=False) )
	