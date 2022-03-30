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

from artevenue.models import Ecom_site, Stock_image, Stock_image_category
from artevenue.models import Stock_collage, Print_medium, Publisher_price
from artevenue.models import Wishlist, Wishlist_item_view, Collage_stock_image, Cart_item_view

from .frame_views import *
from .image_views import *
from .price_views import *

today = datetime.date.today()
env = settings.EXEC_ENV


@csrf_exempt		
def stock_collage_products(request,):
	
	ikeywords = request.GET.get('keywords', '')
	keywords = ikeywords.split()
	keyword_filter = False # Turned on only if a keyword filter is present (through the AJAX call)
	sortOrder = request.GET.get("sort")
	show = request.GET.get("show", '100')
	page = request.GET.get("page", '')
	set_of = request.GET.get("set_of", '')

	if page is None or page == 0:
		page = 1 #default

	collages = Stock_collage.objects.filter(is_published = True, set_of__gt = 1).order_by('category_disp_priority')
	
	if set_of :
		if set_of > 0 :
			collages = collages.filter(set_of = set_of)

	cate = Stock_collage.objects.filter(
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
		
	'''
	dt =  today.day
	if dt >= 1 and dt <= 5:
		collages = collages.order_by('category_disp_priority', '?')
	elif dt > 5 and dt <= 10:
		collages = collages.order_by('category_disp_priority', 'product_id')
	elif dt > 10 and dt <= 20:
		collages = collages.order_by('category_disp_priority', '?')
	else:
		collages = collages.order_by('category_disp_priority', 'product_id')
	'''

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
def get_framed_collage(request, coll_id=None, m_id=None, mount_color='', 
		mount_size=0, user_width=0, prod_type='STOCK-IMAGE' ):	
	
	coll_id = request.POST.get('coll_id', '')
	m_id = request.POST.get('moulding_id', 18) 
	mount_color = request.POST.get('mount_color', '#fff') 
	mount_size = float(request.POST.get('mount_size', '1'))
	user_width = float(request.POST.get('image_width', 10))
	
	coll = Collage_stock_image.objects.filter(stock_collage_id = coll_id)

	img = []
	for c in coll:
		img.append( get_FramedImage_by_id(request, c.stock_image_id, m_id, mount_color, 
						mount_size, user_width, prod_type, 'NO', 'NO') )

	if len(img) == 2 :
		framed_coll = Image.new("RGB", (420, 200), (255,255,255))
	elif len(img) == 3:
		framed_coll = Image.new("RGB", (640, 200), (255,255,255))
	else :
		framed_coll = Image.new("RGB", (860, 200), (255,255,255))
	
	x=0
	y=0
	coord = (x, y)
	ratio_lt_1 = False
	total_w = 0
	for m in img:
		ratio = m.width / m.height
		wd = 200
		ht = round(200 / ratio)
		if ht > 200:
			ratio_lt_1 = True
			ht = 200
			wd = round(ht * ratio)
			x = x + wd + 20
		else:
			x = x + 220
			
		total_w = total_w + wd + 20
		m = m.resize( (wd, ht) )
		framed_coll.paste(m, coord)
		coord = (x, y)
	
	if ratio_lt_1:
		framed_coll = framed_coll.crop( (0,0,( total_w - 20), 200 ) )

		
	buffered = BytesIO()
	framed_coll.save(buffered, format='JPEG')
	img_data = buffered.getvalue()
	img_str = base64.b64encode(img_data)

	return HttpResponse(img_str)
		
@csrf_exempt
def get_collage_price(request):

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
	
	
	
def stock_collage_detail(request, prod_id = '', iuser_width='', iuser_height=''):
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
	product = get_object_or_404(Stock_collage, is_published = True, pk=prod_id)
			
	printmedium = Print_medium.objects.all()

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

	prod_data = get_artset_price_for_6_prods(prod_id, product.aspect_ratio)
	ready_prod_data_paper = prod_data['size_price_paper']
	ready_prod_data_canvas = prod_data['size_price_canvas']

	wall_colors = ['255,255,255', '255,255,224', '242,242,242', '230,242,255', '65,182,230', '64,224,208', '204,255,204', '128,128,0', '255,255,179', '255,205,72', '255,215,0', '255,230,230', '137,46,58', '255,0,0']

	return render(request, "artevenue/stock_collage_detail.html", {'collage':product,
		'printmedium':printmedium,
		'mouldings_apply':paper_mouldings_apply, 'mouldings_show':paper_mouldings_show, 'mounts':mounts,
		'acrylics':acrylics,
		'boards':boards,'stretches':stretches, 'ENV':settings.EXEC_ENV,
		'cart_item':cart_item_view, 'iuser_width':iuser_width, 'iuser_height':iuser_height,
		'price':price, 'wishlist_prods':wishlist_prods,
		'paper_mouldings_corner':paper_mouldings_corner, 'canvas_mouldings_corner':canvas_mouldings_corner,
		'ready_prod_data_paper':ready_prod_data_paper, 'ready_prod_data_canvas':ready_prod_data_canvas,
		'wishlist_item':wishlist_item_view, 'env': env, 'wall_colors': wall_colors,
		'is_set': 'TRUE'} )
	


def set_detail(request, prod_id = '', iuser_width='', iuser_height=''):
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
	product = get_object_or_404(Stock_collage, is_published = True, pk=prod_id)
	stock_images = Collage_stock_image.objects.filter( stock_collage = product )
	
	if not iuser_width or iuser_width == '0':
		if product.stock_collage_specs:
			iwidth = str(product.stock_collage_specs.image_width)
			if iwidth in ['10', '14', '18', '24', '30', '36']:
				iuser_width = iwidth
				
	print_medium_id = None
	moulding = None
	moulding_id = None
	mount_id = None
	mount = None
	mount_size = 0
	mount_color = ''
	board_id = None
	acrylic_id = None 
	stretch_id = None
	
	if product.stock_collage_specs.print_medium_id:
		print_medium_id = product.stock_collage_specs.print_medium_id
	if product.stock_collage_specs.moulding:
		moulding_id = product.stock_collage_specs.moulding_id
		moulding = Moulding.objects.filter(moulding_id = product.stock_collage_specs.moulding_id).first()
	if product.stock_collage_specs.mount:
		mount_id = product.stock_collage_specs.mount_id
		mount_color = product.stock_collage_specs.mount.color
		mount = Mount.objects.filter(mount_id = product.stock_collage_specs.mount_id).first()
	if product.stock_collage_specs.mount_size:
		mount_size = product.stock_collage_specs.mount_size
	if product.stock_collage_specs.board:
		board_id = product.stock_collage_specs.board_id
	if product.stock_collage_specs.acrylic:
		acrylic_id = product.stock_collage_specs.acrylic_id
	if product.stock_collage_specs.stretch:
		stretch_id = product.stock_collage_specs.stretch_id
			
	printmedium_list = Print_medium.objects.all()
	all_mouldings = Moulding.objects.all()
	all_mounts = Mount.objects.all()
	
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

	prod_data = get_wall_art_set_sizes_prices(prod_id, product.aspect_ratio)
	ready_prod_data_paper = prod_data['size_price_paper']
	ready_prod_data_canvas = prod_data['size_price_canvas']

	wall_colors = ['255,255,255', '255,255,224', '242,242,242', '230,242,255', '65,182,230', '64,224,208', '204,255,204', '128,128,0', '255,255,179', '255,205,72', '255,215,0', '255,230,230', '137,46,58', '255,0,0']

	return render(request, "artevenue/wall_art_set_detail.html", {'product':product, 'stock_images': stock_images,
		'printmedium':printmedium_list, 'print_medium_id': print_medium_id, 'moulding_id': moulding_id,
		'mount_id': mount_id, 'mount_size': mount_size, 'board_id': board_id, 'acrylic_id': acrylic_id, 
		'stretch_id': stretch_id, 'moulding': moulding, 'mount_color': mount_color, 'mount': mount,
		'ENV':settings.EXEC_ENV, 'is_set': 'TRUE', 'all_mouldings': all_mouldings, 'all_mounts': all_mounts,
		'cart_item':cart_item_view, 'iuser_width':iuser_width, 'iuser_height':iuser_height,
		'wishlist_prods':wishlist_prods,
		'ready_prod_data_paper':ready_prod_data_paper, 'ready_prod_data_canvas':ready_prod_data_canvas,
		'wishlist_item':wishlist_item_view, 'env': env, 'wall_colors': wall_colors } )
	
	
def createInitialData(request):

	err_cd = '00'
	msg = ''
	from_product_id = request.GET.get('from_product_id', '')

	collages = Stock_collage.objects.filter(is_published = True)
	
	if from_product_id:
		collages = collages.filter(product_id__gte = from_product_id)

	for i in collages:
		try:
			if not i.stock_collage_specs:
				pass
		except ObjectDoesNotExist:	
			continue
		coll = Collage_stock_image.objects.filter(stock_collage = i)	
		t_price = 0
		img = []
		aspect_ratio = 1
		key_words = ''
		colors = ''
		max_height = 40
		max_width = 40
		min_width = 8
		orientation = 'Square'
		
		for c in coll:
			aspect_ratio = c.stock_image.aspect_ratio
			key_words = key_words + '|' + c.stock_image.key_words
			colors = ''
			max_height = c.stock_image.max_height
			max_width = c.stock_image.max_width
			min_width = 8
			orientation = c.stock_image.orientation
			
			image_width = 10
			image_height = round(image_width / aspect_ratio)


			## Common pricing components
			print_medium_id = None
			moulding = None
			moulding_id = '0'
			moulding_id = None
			mount_id = None
			mount_size = 0
			board_id = None
			acrylic_id = None 
			stretch_id = None
			
			product = c.stock_collage
		

			if product.stock_collage_specs.print_medium_id:
				print_medium_id = product.stock_collage_specs.print_medium_id
			if product.stock_collage_specs.moulding:
				moulding_id = product.stock_collage_specs.moulding_id
				moulding = product.stock_collage_specs.moulding
			if product.stock_collage_specs.mount:
				mount_id = product.stock_collage_specs.mount_id
			if product.stock_collage_specs.mount_size:
				mount_size = 1
			if product.stock_collage_specs.board:
				board_id = product.stock_collage_specs.board_id
			if product.stock_collage_specs.acrylic:
				acrylic_id = product.stock_collage_specs.acrylic_id
			if product.stock_collage_specs.stretch:
				stretch_id = product.stock_collage_specs.stretch_id
			
			## Add the stretch by default is it's a framed canvas
			if product.stock_collage_specs.print_medium_id == 'CANVAS':
				if product.stock_collage_specs.moulding:
					stretch_id = '1'
			
			try:
				price = get_prod_price(c.stock_image_id, 
						prod_type='STOCK-IMAGE',
						image_width=image_width, 
						image_height=image_height,
						print_medium_id = print_medium_id,
						acrylic_id = acrylic_id,
						moulding_id = moulding_id,
						mount_size = mount_size,
						mount_id = mount_id,
						board_id = board_id,
						stretch_id = stretch_id)
				
							
				request = HttpRequest()
				img.append( get_FramedImage_by_id(request, c.stock_image_id, 18, '#fff', 
									1, 10, 'STOCK-IMAGE') )

				t_price = t_price + price['item_price']
				
			except Error as e:
				err_cd = '01'
				msg = "Error encountered while calculating the price."
				return( JsonResponse({'err_cd': err_cd, 'msg': msg }, safe=False) )					


		try:
			if len(img) == 2 :
				framed_coll = Image.new("RGB", (420, 200), (255,255,255))
			elif len(img) == 3:
				framed_coll = Image.new("RGB", (640, 200), (255,255,255))
			else :
				framed_coll = Image.new("RGB", (860, 200), (255,255,255))
			
			x=0
			y=0
			coord = (x, y)

			ratio_lt_1 = False
			total_w = 0
			for m in img:
				ratio = m.width / m.height
				wd = 200
				ht = round(200 / ratio)
				if ht > 200:
					ratio_lt_1 = True
					ht = 200
					wd = round(ht * ratio)
					x = x + wd + 20
				else:
					x = x + 220
					
				total_w = total_w + wd + 20
				m = m.resize( (wd, ht) )
				framed_coll.paste(m, coord)
				coord = (x, y)
			
			if ratio_lt_1:
				framed_coll = framed_coll.crop( (0,0,( total_w - 20), 200 ) )
			
			if env == 'DEV' or env == 'TESTING':
				img_file = settings.STATIC_URL + 'img/collage/img/' + str(i.product_id) + '.jpg'
				img_thumbnail_file = settings.STATIC_URL + 'img/collage/img/' + str(i.product_id) + '_thumbnail.jpg'
				img_file_s = settings.BASE_DIR + '/artevenue'  + settings.STATIC_URL + 'img/collage/img/' + str(i.product_id) + '.jpg'
				img_thumbnail_file_s = settings.BASE_DIR + '/artevenue' + settings.STATIC_URL + 'img/collage/img/' + str(i.product_id) + '_thumbnail.jpg'
			else:
				img_file = 'img/collage/img/'  + str(i.product_id) + '.jpg'
				img_file_s = '/home/artevenue/website/estore/static/' + img_file
				img_thumbnail_file = 'img/collage/img/'  + str(i.product_id) + '_thumbnail.jpg'
				img_thumbnail_file_s = '/home/artevenue/website/estore/static/' + img_thumbnail_file

			ratio = framed_coll.width / framed_coll.height
			framed_coll.save(img_file_s, "JPEG")
			framed_coll.thumbnail((200, round(200/ratio)) )
			framed_coll.save(img_thumbnail_file_s, "JPEG")
		except Error as e:
			err_cd = '02'
			msg = "Error encountered while generating a thumbnail."
			return( JsonResponse({'err_cd': err_cd, 'msg': msg }, safe=False) )					

		try:
			#####Update the uprice & rls in Stock_collage
			stk = Stock_collage.objects.filter(product_id = i.product_id).update( price = t_price,
				url = img_file, thumbnail_url = img_thumbnail_file,
						aspect_ratio = aspect_ratio,
						key_words = key_words, colors = colors,  max_height = max_height,
						max_width = max_width, min_width = min_width, orientation = orientation,
						set_of = len(img)
					)
		except Error as e:
			err_cd = '01'
			msg = "Error encountered while saving the price in database."
			return( JsonResponse({'err_cd': err_cd, 'msg': msg }, safe=False) )
	
	return( JsonResponse({'err_cd': err_cd, 'msg': msg }, safe=False) )
		
def updateAR(product_id=None):

	collages = Stock_collage.objects.filter(product_id__gt = 52)
	if product_id:
		collages = collages.filter(product_id = product_id)

	na = [12, 62, 64, 74, 76, 77]  #Set of 4

	for i in collages:
		print("Processing Collage ID: " + str(i.product_id))
		coll = Collage_stock_image.objects.filter(stock_collage = i).exclude(stock_collage_id__in = na).first()
		if coll:
			ar = coll.stock_image.aspect_ratio
		
		#####Update the uprice & rls in Stock_collage
		stk = Stock_collage.objects.filter(product_id = i.product_id).update(
					aspect_ratio = ar
		)



def get_wall_art_set_sizes_prices(prod_id, aspect_ratio, prod_type='STOCK-IMAGE'):

	product = Stock_collage.objects.filter(product_id = prod_id).first();
	collages = Collage_stock_image.objects.filter( stock_collage_id = prod_id )
	
	STANDARD_PROD_WIDTHS = [10, 14, 18, 24, 30, 36]
		
	## Common pricing components
	print_medium_id = None
	moulding = None
	moulding_id = '0'
	mount_id = None
	mount_size = 0
	board_id = None
	acrylic_id = None 
	stretch_id = None

	if product.stock_collage_specs.print_medium_id:
		print_medium_id = product.stock_collage_specs.print_medium_id
	if product.stock_collage_specs.moulding:
		moulding_id = product.stock_collage_specs.moulding_id
		moulding = product.stock_collage_specs.moulding
	if product.stock_collage_specs.mount:
		mount_id = product.stock_collage_specs.mount_id
	if product.stock_collage_specs.mount_size:
		mount_size = product.stock_collage_specs.mount_size
	if product.stock_collage_specs.board:
		board_id = product.stock_collage_specs.board_id
	if product.stock_collage_specs.acrylic:
		acrylic_id = product.stock_collage_specs.acrylic_id
	if product.stock_collage_specs.stretch:
		stretch_id = product.stock_collage_specs.stretch_id
	
	## Add the stretch by default is it's a framed canvas
	if product.stock_collage_specs.print_medium_id == 'CANVAS':
		if product.stock_collage_specs.moulding:
			stretch_id = '1'
			
	size_price_paper = {}
	size_price_canvas = {}

	
	## Six prods with PAPER medium
	for i in STANDARD_PROD_WIDTHS:
		p_data_paper = {}
		p_data_canvas = {}
		image_width = i
		image_height = round(image_width / aspect_ratio)

		moulding = Moulding.objects.filter(pk = moulding_id).first()
		width_inner_inches = 0
		if moulding:
			width_inner_inches = moulding.width_inner_inches
		# For width add all the product widths + 2 inch gap
		#i_width_p = round((image_width + moulding.width_inner_inches * 2 + mount_size * 2 ) * product.set_of + (product.set_of -1)*2)
		#i_width_c = round((image_width + moulding.width_inner_inches * 2)  * product.set_of + (product.set_of -1)*2)
		
		total_price_paper = 0
		total_cash_disc_paper = 0
		total_percent_disc_paper = 0
		total_item_unit_price_paper = 0
		total_item_price_withoutdisc_paper = 0
		total_disc_amt_paper = 0

		total_price_canvas = 0		
		total_cash_disc_canvas = 0
		total_percent_disc_canvas = 0
		total_item_unit_price_canvas = 0
		total_item_price_withoutdisc_canvas = 0
		total_disc_amt_canvas = 0

		skip_it = False
		for c in collages:
			if i > c.stock_image.max_width:
				skip_it = True
				break

			##If the default print surface for this set is CANVAS and if it's stretched canvas, then if users
			## selects PAPER, we use the default frame and mount.
			## If its' CANVAS and the moulding is also present, then we remove the mount to keep it consistent with
			## the way it looks in the room view.
			if product.stock_collage_specs.print_medium_id == 'CANVAS' and product.stock_collage_specs.stretch_id :
				side = image_width if aspect_ratio > 1 else image_height
				if side <= 18:
					if product.stock_collage_specs.print_medium_id == 'CANVAS' and product.stock_collage_specs.stretch_id and product.stock_collage_specs.moulding_id:
						p_mount_size = 0
					else:
						p_mount_size = 1
					p_moulding_id = 18
				elif side <= 26:
					if product.stock_collage_specs.print_medium_id == 'CANVAS' and product.stock_collage_specs.stretch_id and product.stock_collage_specs.moulding_id:
						p_mount_size = 0
					else:
						p_mount_size = 2
					p_moulding_id = 24
				elif side <= 34:
					if product.stock_collage_specs.print_medium_id == 'CANVAS' and product.stock_collage_specs.stretch_id and product.stock_collage_specs.moulding_id:
						p_mount_size = 0
					else:
						p_mount_size = 3
					p_moulding_id = 24
				else:
					if product.stock_collage_specs.print_medium_id == 'CANVAS' and product.stock_collage_specs.stretch_id and product.stock_collage_specs.moulding_id:
						p_mount_size = 0
					else:
						p_mount_size = 4
					p_moulding_id = 24				
				p_mount_id = 3
				p_board_id = 1
				p_acrylic_id = 1
				p_stretch_id = None

				p_moulding = Moulding.objects.filter(pk = moulding_id).first()
				p_width_inner_inches = 0
				if p_moulding:
					p_width_inner_inches = moulding.width_inner_inches
				
			else: 
				if aspect_ratio > 1:
					#p_mount_size = 1 if image_width <= 18 else 2 if image_width <= 26 else 3 if image_width <= 34 else 4
					p_mount_size = 1 if image_width <= 18 else 2
				else:
					#p_mount_size = 1 if image_height <= 18 else 2 if image_height <= 26 else 3 if image_height <= 34 else 4
					p_mount_size = 1 if image_height <= 18 else 2 
				
				p_moulding_id = moulding_id
				p_mount_id = mount_id
				p_board_id = board_id
				p_acrylic_id = acrylic_id
				p_stretch_id = None
				p_width_inner_inches = width_inner_inches
			
			###########################
			### PAPER SIZE & PRICE
			###########################			
			i_width_p = round(image_width + p_width_inner_inches * 2 + p_mount_size * 2 )
			i_height_p = round(image_height + p_width_inner_inches * 2 + p_mount_size * 2)
			p_data_paper['PAPER_WIDTH'] = i_width_p
			p_data_paper['PAPER_HEIGHT'] = i_height_p
			p_data_paper['PAPER_WIDTH_UNFRAMED'] = image_width
			p_data_paper['PAPER_HEIGHT_UNFRAMED'] = image_height
			
			price = get_prod_price(c.stock_image_id, 
					prod_type='STOCK-IMAGE',
					image_width=image_width, 
					image_height=image_height,
					print_medium_id = 'PAPER',
					acrylic_id = p_acrylic_id,
					moulding_id = p_moulding_id,
					mount_size = p_mount_size,
					mount_id = p_mount_id,
					board_id = p_board_id,
					stretch_id = p_stretch_id)					

			item_price_paper = price['item_price']
			msg_paper = price['msg']
			cash_disc_paper = price['cash_disc']
			percent_disc_paper = price['percent_disc']
			item_unit_price_paper = price['item_unit_price']
			item_price_withoutdisc_paper = price['item_price_without_disc']
			disc_amt_paper = price['disc_amt']
			disc_applied_paper = price['disc_applied']
			promotion_id_paper = price['promotion_id']
			
			total_price_paper = total_price_paper + item_price_paper
			total_cash_disc_paper = total_cash_disc_paper + cash_disc_paper
			total_percent_disc_paper = statistics.mean([total_percent_disc_paper, percent_disc_paper])
			total_item_unit_price_paper = total_item_unit_price_paper + item_unit_price_paper
			total_item_price_withoutdisc_paper = total_item_price_withoutdisc_paper + item_price_withoutdisc_paper
			total_disc_amt_paper = total_disc_amt_paper + disc_amt_paper


			###########################
			### CANVAS SIZE & PRICE
			###########################			
			i_width_c = round(image_width + width_inner_inches * 2)
			i_height_c = round(image_height + width_inner_inches * 2)
			p_data_canvas['CANVAS_WIDTH'] = i_width_c
			p_data_canvas['CANVAS_HEIGHT'] = i_height_c
			p_data_canvas['CANVAS_WIDTH_UNFRAMED'] = image_width
			p_data_canvas['CANVAS_HEIGHT_UNFRAMED'] = image_height

			price = get_prod_price(c.stock_image_id, 
					prod_type='STOCK-IMAGE',
					image_width=image_width, 
					image_height=image_height,
					print_medium_id = 'CANVAS',
					acrylic_id = acrylic_id,
					moulding_id = moulding_id,
					mount_size = mount_size,
					mount_id = mount_id,
					board_id = board_id,
					stretch_id = stretch_id)					

			item_price_canvas = price['item_price']
			msg_canvas = price['msg']
			cash_disc_canvas = price['cash_disc']
			percent_disc_canvas = price['percent_disc']
			item_unit_price_canvas = price['item_unit_price']
			item_price_withoutdisc_canvas = price['item_price_without_disc']
			disc_amt_canvas = price['disc_amt']
			disc_applied_canvas = price['disc_applied']
			promotion_id_canvas = price['promotion_id']
			
			total_price_canvas = total_price_canvas + item_price_canvas
			total_cash_disc_canvas = total_cash_disc_canvas + cash_disc_canvas
			total_percent_disc_canvas = statistics.mean([total_percent_disc_canvas, percent_disc_canvas])
			total_item_unit_price_canvas = total_item_unit_price_canvas + item_unit_price_canvas
			total_item_price_withoutdisc_canvas = total_item_price_withoutdisc_canvas + item_price_withoutdisc_canvas
			total_disc_amt_canvas = total_disc_amt_canvas + disc_amt_canvas
			
		if not skip_it:
			skip_it = False
			p_data_paper['PAPER_PRICE'] = total_price_paper
			p_data_canvas['CANVAS_PRICE'] = total_price_canvas
			
			size_price_paper[str(i)] = p_data_paper
			size_price_canvas[str(i)] = p_data_canvas

		
	return ({'size_price_paper':size_price_paper, 'size_price_canvas':size_price_canvas})
	


@csrf_exempt		
def wall_art_set_products(request, set_of=None, page = 1, print_medium=None):	

	singles = request.GET.get("singles", 'NO')
	show  = request.GET.get("show", 0)
	sortOrder = request.GET.get("sort", '')
	if not print_medium :
		print_medium = request.GET.get("print_medium", "")
	else:
		print_medium = print_medium.upper()
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
		sets = Stock_collage.objects.filter(is_published = True, set_of__gt = 1).order_by('category_disp_priority', 
				'-stock_collage_specs__updated_date')
	else:
		sets = Stock_collage.objects.filter(is_published = True, set_of = 1).order_by('category_disp_priority', 
				'-stock_collage_specs__updated_date')
		
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

	if print_medium != '':
		sets = sets.filter(stock_collage_specs__print_medium = print_medium)
		filt_applied = True

	if singles == 'NO':
		cate = Stock_collage.objects.filter(
			is_published = True, set_of__gt = 1).values_list('stock_image_category__name', flat=True).distinct()
	else:
		cate = Stock_collage.objects.filter(
			is_published = True, set_of = 1).values_list('stock_image_category__name', flat=True).distinct()
		
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

		template = "artevenue/collage_display_include.html"
	else :
		template = "artevenue/wall_art_set_products.html"
		
	return render(request, template,
			{'coll':coll, 'wishlist_prods':wishlist_prods, 
			'page':page, 'wishlistitems':wishlistitems,
			'sortOrder':sortOrder, 'show':show, 'filt_applied': filt_applied,
			'colors_list': colors_list, 'categories_list': categories_list, 'print_medium': print_medium,
			'sets_of_list': sets_of_list, 'ikeywords':ikeywords, 'page':page, 'env': env,
			'f_set_of': f_set_of, 'f_category': f_category, 'f_color': f_color,
			'is_set': 'TRUE', 'singles': singles})

def generate_set_prices(request):
	return render(request, 'artevenue/generate_set_prices.html',{})
	