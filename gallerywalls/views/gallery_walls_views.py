from django.shortcuts import render, get_object_or_404
from django.conf import settings
from django.core.paginator import EmptyPage, PageNotAnInteger, Paginator
from artevenue.decorators import is_manager
from django.views.decorators.csrf import csrf_exempt
from django.db.models import Count, Q, F, When, Case
from django.contrib.admin.views.decorators import staff_member_required
from django.http import JsonResponse
from django.contrib.auth.models import User
from django.db import IntegrityError, DatabaseError, Error

from datetime import datetime
import datetime
import json
from decimal import Decimal
from PIL import Image
import random
import string

from gallerywalls.models import Gallery, Gallery_variation, Room, Placement, Gallery_item
from artevenue.models import Business_profile, Order, UserProfile, Moulding
from artevenue.views import price_views, cart_views, Ecom_site

env = settings.EXEC_ENV
ecom_site = get_object_or_404 (Ecom_site, store_id=settings.STORE_ID )
def get_gallery_walls(request, gallery_id=None, category_id = None, page = None, room_name=None, f_placement_name=None, f_color=None):
	
	sortOrder = request.GET.get("sort")
	f_color = request.GET.get("color", "")	
	f_room_name = request.GET.get("room_name", "")
	f_placement_name = request.GET.get("placement_name", "")
	f_set_of = request.GET.get("set_of", "")
	page = request.GET.get("page", 1)
	ikeywords = request.GET.get('keywords', '')	
	keywords = ikeywords.split()
	keyword_filter = False # Turned on only if a keyword filter is present (through the AJAX call)

	if page is None or page == 0:
		page = 1 # default

	gallery_parent = Gallery_variation.objects.filter(is_parent = True, gallery__is_published = True, gallery__set_of__gte = 2)
	total_galleries = gallery_parent.count()	

	gallery_variation = Gallery_variation.objects.filter(is_parent = False, gallery__is_published = True, gallery__set_of__gte = 2).order_by('-gallery_id')

	filt_msg = ''
	if gallery_id:
		gallery_parent = gallery_parent.filter(gallery_id = gallery_id)
	if category_id:
		gallery_parent = gallery_parent.filter(gallery__stock_image_category_id = category_id)
	if f_room_name:
		gallery_parent = gallery_parent.filter(gallery__room__name = f_room_name)
		filt_msg = 'Showing ' + str(gallery_parent.count()) + ' gallery walls for ' + f_room_name
	if f_placement_name:
		gallery_parent = gallery_parent.filter(gallery__placement__name = f_placement_name)
		filt_msg = 'Showing ' + str(gallery_parent.count()) + ' gallery walls for ' + f_placement_name
	if f_color:
		gallery_parent = gallery_parent.filter(gallery__colors__icontains = f_color)
		filt_msg = 'Showing ' + str(gallery_parent.count()) + ' gallery walls in ' + f_color + ' colored theme'
	if f_set_of:
		gallery_parent = gallery_parent.filter(gallery__set_of__icontains = f_set_of)
		filt_msg = 'Showing ' + str(gallery_parent.count()) + ' gallery walls with set of ' + f_set_of + ' artworks'

	t_f = Q()
	f = Q()
	for w in keywords:
		if w == '':
			continue
		f = f | Q(key_words__icontains = w)
	t_f = t_f & f 

	gallery_parent = gallery_parent.filter( t_f )

	gallery_parent = gallery_parent.order_by('gallery__category_disp_priority', '-gallery_id')		
	gallery_filters = ['ROOM', 'PLACEMENT', 'COLORS', 'KEY_WORDS' ]

	rooms = Room.objects.all().values('name').distinct()	
	placements = Placement.objects.all().values('name').distinct()
	set_of = Gallery.objects.all().values('set_of').distinct().order_by('set_of')
	
	colors = ['Red', 'Orange',  'Yellow', 'Green', 'LightBlue', 'MediumPurple', 'Pink', 'Brown', 'black', 'White']
	key_words = Gallery.objects.all().values('colors').distinct()

	show = request.GET.get("show", "50")
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
			if show == '500':
				perpage = 500
				show = '500'
			else:
				show = '50' # default
				perpage = 50

	paginator = Paginator(gallery_parent, perpage) 
	if not page:
		page = request.GET.get('page')
	
	galleries = paginator.get_page(page)			
	
	#=====================
	index = galleries.number - 1 
	max_index = len(paginator.page_range)
	start_index = index - 5 if index >= 5 else 0
	end_index = index + 5 if index <= max_index - 5 else max_index
	page_range = list(paginator.page_range)[start_index:end_index]
	#=====================

	template = "gallerywalls/gallery_walls_list.html"

	env = settings.EXEC_ENV
	
	return render(request, template, {
		'galleries':galleries, 'gallery_variation': gallery_variation,
		'sortOrder':sortOrder, 'rooms': rooms, 'placements': placements, 'set_of': set_of,
		'keywords':key_words, 'page':page, 'colors':colors,'env':env, 'filt_msg': filt_msg,
		'total_galleries': total_galleries, 'env':settings.EXEC_ENV,
		'f_room': room_name, 'f_color': f_color, 'f_placement_name':f_placement_name, 
		'f_set_of': f_set_of})

def gallery_wall_detail(request, gallery_id):

	g = Gallery.objects.filter(gallery_id = gallery_id, is_published = True).first()

	gallery_parent = Gallery_variation.objects.get(gallery_id = gallery_id, is_parent = True)
	gallery_variations = Gallery_variation.objects.filter(gallery_id = gallery_id)
	gallery_items = Gallery_item.objects.filter(gallery_id = gallery_id, gallery_variation = gallery_parent)

	gallery_items_all = Gallery_item.objects.filter(gallery_id = gallery_id)
	prices = {}
	for v in gallery_variations:
		v_price = 0
		for i in gallery_items_all:
			if i.gallery_variation_id == v.id and i.gallery_id == v.gallery_id:
				i_price = get_variation_item_price(i.item_id)				
				v_price = v_price + i_price

		prices[v.id] = v_price

	
	## Get frames in the gallerywall
	mouldings = []
	mediums = []
	stretched_canv = False
	for i in gallery_items_all:
		if i.moulding_id:
			mouldings.append(i.moulding_id)
		if i.print_medium_id:
			mediums.append(i.print_medium_id)	
		if i.stretch_id and not i.moulding_id:
			stretched_canv = True
	
	frames = Moulding.objects.filter(moulding_id__in = mouldings)


	livuser = False
	bus_user = False
	user = None
	if request.user.is_authenticated:
		user = User.objects.filter(username = request.user).first()

	if user:
		try:
			livprofile = UserProfile.objects.get(user = user)
		except UserProfile.DoesNotExist:
			livprofile = None
		if livprofile:
			if livprofile.business_profile_id:
				if livprofile.business_profile_id == 17:
					livuser = True	
				else:
					bus_user = True
		bus_profile = Business_profile.objects.filter(user = user)
		if bus_profile:
			bus_user = True

	v15off = False
	if user and not livuser and not bus_user:
		orders = Order.objects.filter(user = user).exclude(order_status = 'PP')
		if not orders:
			v15off = True
	
	if g:
		#if g.set_of > 1:
		#	template = "gallerywalls/gallery_wall_detail.html"
		#else:
		template = "gallerywalls/gallery_wall_detail_new.html"
	else:
		template = "gallerywalls/gallery_not_published.html"
		
	return render(request, template, {
		'gal':gallery_parent, 'gallery_variations': gallery_variations,
		'gallery_items': gallery_items, 'prices': prices, 'v15off': v15off,
		'env':settings.EXEC_ENV, 'frames': frames, 'mediums': mediums, 'stretched_canv': stretched_canv})

@csrf_exempt
def gallery_wall_detail_items(request):
	gallery_id = request.GET.get('gallery_id', '')
	gallery_variation_id = request.GET.get('gallery_variation_id', '')
	gallery_items = Gallery_item.objects.filter(gallery_id = gallery_id, gallery_variation_id = gallery_variation_id)

	g = gallery_items.first()
	if g.set_of > 1:
		template = "gallerywalls/gallery_wall_detail.html"
	else:
		template = "gallerywalls/gallery_wall_detail_new.html"
	
	return render(request, template, {'gallery_items': gallery_items})

@csrf_exempt	
def get_gallery_variation_and_price(request):

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

	# Get prod items data.
	gallery_id = int(request.POST.get('gallery_id', '0'))
	gallery_variation_id = int(request.POST.get('gallery_variation_id', '0'))
	exclude_items = request.POST.getlist('exclude_items[]')

	gallery_items = Gallery_item.objects.filter(gallery_id = gallery_id, 
		gallery_variation_id = gallery_variation_id)
	
	if exclude_items:
		gallery_items = gallery_items.exclude(product_id__in = exclude_items)
		
	gallery_items = gallery_items.values(
			'item_id', 'gallery_id', 'gallery_variation_id', 'product_id', 'product_name', 'product_type_id',
			'moulding_id', 'moulding__name', 'moulding__width_inches', 'print_medium_id', 'mount_id',
			'mount__name', 'mount__color', 'mount_size', 'board_id', 'acrylic_id', 'stretch_id', 'image_width', 
			'image_height', 'moulding__width_inner_inches')

	gallery_variation_price = 0	
	for gal_item in gallery_items:
		item_price = get_variation_item_price(gal_item['item_id'])
		gallery_variation_price = gallery_variation_price + item_price

	return JsonResponse({"msg":msg, "gallery_variation_price": gallery_variation_price, 'gallery_items': list(gallery_items)})	

@csrf_exempt	
def get_variation_item_price(item_id):

	gal_item = Gallery_item.objects.filter(item_id = item_id).first()	
	item_price = 0
	
	if gal_item:
		#####################################
		#         Get the item price
		#####################################
		price = price_views.get_prod_price(gal_item.product_id,
				prod_type=gal_item.product_type_id,
				image_width=gal_item.image_width, 
				image_height=gal_item.image_height,
				print_medium_id = gal_item.print_medium_id,
				acrylic_id = gal_item.acrylic_id,
				moulding_id = gal_item.moulding_id,
				mount_size = gal_item.mount_size,
				mount_id = gal_item.mount_id,
				board_id = gal_item.board_id,
				stretch_id = gal_item.stretch_id)
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

	return item_price

@csrf_exempt
def add_gallery_wall_to_cart(request):
	msg = ''

	gallery_id = int(request.POST.get('gallery_id', '0'))
	gallery_variation_id = int(request.POST.get('gallery_variation_id', '0'))
	exclude_items = request.POST.getlist('exclude_items[]')

	gallery_items = Gallery_item.objects.filter(gallery_id = gallery_id, 
		gallery_variation_id = gallery_variation_id)
	
	if exclude_items:
		gallery_items = gallery_items.exclude(product_id__in = exclude_items)
	
	total_cart_qty = 0
	for i in gallery_items:
		#from django.http import HttpRequest
		#req = HttpRequest()
		#req.method = 'POST'
		sqin = i.image_width * i.image_height;
		print_medium_size = sqin
		acrylic_size = sqin
		stretch_size = sqin
		
		if i.mount_size == '' or i.mount_size == None:
			mnt_size = '0'
		else:
			mnt_size = i.mount_size
		
		request.POST = {'prod_id':i.product_id, 'qty':1, 'moulding_id': i.moulding_id,
							'width':i.image_width, 'height': i.image_height,
							'moulding_size' : i.moulding_size,
							'print_medium_id':i.print_medium_id, 'print_medium_size': print_medium_size, 
							'mount_id':i.mount_id, 'mount_size': mnt_size,
							'mount_w_left' : 0, 'mount_w_right': 0, 
							'mount_w_top': 0, 'mount_w_bottom' : 0, 
							'acrylic_id': i.acrylic_id, 'acrylic_size':sqin,
							'board_id': i.board_id, 'board_size': sqin, 'stretch_id': i.stretch_id,
							'stretch_size': sqin, 
							'total_price': 0, 'image_width': i.image_width, 'image_height': i.image_height,
							'discount':0, 'promotion_id':None, 'disc_amt':0,
							'item_unit_price':0, 'prod_type': i.product_type_id
		}
		
		resp = cart_views.add_to_cart_new(request)
		result = json.loads(resp.content)	
		if 'status' in result:
			status = result['status']
		else:
			status = ''
		
		if 'cart_qty' in result:
			total_cart_qty = total_cart_qty + result['cart_qty']
			msg = 'SUCCESS'

	return JsonResponse({'status': status, 'msg': msg, 'cart_qty': total_cart_qty})
	
	
def update_gallery_prices(g_id=None):

	gallery_variation = Gallery_variation.objects.filter(
		gallery__is_published = True).order_by('gallery_id')
	
	if g_id:
		gallery_variation = gallery_variation.filter(gallery_id__gte = g_id)
	
	for g in gallery_variation:
		gallery_items = Gallery_item.objects.filter(gallery_id = g.gallery_id, gallery_variation = g)
				
		gallery_items = gallery_items.values(
				'item_id', 'gallery_id', 'gallery_variation_id', 'product_id', 'product_name', 'product_type_id',
				'moulding_id', 'moulding__name', 'moulding__width_inches', 'print_medium_id', 'mount_id',
				'mount__name', 'mount__color', 'mount_size', 'board_id', 'acrylic_id', 'stretch_id', 'image_width', 
				'image_height', 'moulding__width_inner_inches')

		gallery_variation_price = 0	
		for gal_item in gallery_items:
			item_price = get_variation_item_price(gal_item['item_id'])
			gallery_variation_price = gallery_variation_price + item_price

		## Update variation price
		gallery_variation = Gallery_variation.objects.filter(
			gallery_id = g.gallery_id, id = g.id
			).update(price = gallery_variation_price)
			

@csrf_exempt
@is_manager	
def create_gallery_wall(request):
	rooms = Room.objects.all().distinct()	
	placements = Placement.objects.all().distinct()

	return render(request, "gallerywalls/create_gallery_wall.html", {'rooms': rooms, 'placements': placements})	
	
@csrf_exempt
@is_manager	
def create_gw_data(request):
	from artevenue.models import Print_medium, Publisher_price, Moulding, Mount, Acrylic, Board, Stretch
	from artevenue.views import frame_views
	
	title = request.GET.get("title", '')
	desc = request.GET.get("description", '')
	set_of = request.GET.get("set_of", '')
	room_id = request.GET.get("room", '')
	placement_id = request.GET.get("placement", '')
	colors = request.GET.get("colors", '')
	key_words = request.GET.get("key_words", '')
	
	
	room = Room.objects.filter(room_id = room_id).first()
	placement = Placement.objects.filter(placement_id = placement_id).first()
	
	printmedium = Print_medium.objects.all()
	price = Publisher_price.objects.filter(print_medium_id = 'PAPER') 

	# get mouldings
	mouldings = Moulding.objects.filter(is_published = True)
	
	# get mounts
	mounts = Mount.objects.all()

	# get arylics
	acrylics = Acrylic.objects.all()
	
	# get boards
	boards = Board.objects.all()

	# get Stretches
	stretches = Stretch.objects.all()
	
	
	# get mouldings
	mouldings_d = frame_views.get_mouldings(request)
	# defaul we send is for PAPER
	paper_mouldings_apply = mouldings_d['paper_mouldings_apply']
	paper_mouldings_show = mouldings_d['paper_mouldings_show']
	moulding_diagrams = mouldings_d['moulding_diagrams']
	canvas_mouldings_show = mouldings_d['canvas_mouldings_show']
	
	
	return render(request, "gallerywalls/create_gw_data.html", {
		'title': title, 'desc': title, 'set_of':set_of, 'set_range': range(int(set_of)),
		'room': room, 'placement': placement, 'colors': colors, 'key_words': key_words,
		'mouldings_apply':paper_mouldings_apply, 'paper_mouldings_show':paper_mouldings_show, 
		'canvas_mouldings_show':canvas_mouldings_show, 
		'printmedium':printmedium, 'mouldings': mouldings, 'mounts':mounts, 
		'acrylics':acrylics, 'boards':boards,'stretches':stretches, 'env':settings.EXEC_ENV})

@csrf_exempt
@is_manager	
def save_gw(request):
	err_cd = '00'
	msg = ''

	room_id = request.POST.get("room_id", '')
	placement_id = request.POST.get("placement_id", '')
	placement_id
	set_of = int(request.POST.get('set_of', '0'))
	title = request.POST.get('title', '')
	desc = request.POST.get('desc', '')
	colors = request.POST.get('colors', '')
	key_words = request.POST.get('key_words', '')
	num_of_variations = int(request.POST.get('num_of_variations', '0'))
	duplicate_image = request.POST.get('duplicate_image', 'NO')
	
	try:
		existing_gal = Gallery.objects.filter(title = title).first()
		if existing_gal:
			err_cd = '99'
			msg = "A Gallery Wall with this title has already been created. Cannot proceed."
			return JsonResponse({"err_cd":err_cd, 'msg': msg})		

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
					img_loc = settings.BASE_DIR + "/artevenue" + settings.STATIC_URL + 'img/creatives/' + file_nm
					thumb_img_loc = settings.BASE_DIR + "/artevenue" + settings.STATIC_URL + 'img/creatives/' + file_nm_thumb
					
				else:
					img_loc = settings.PROJECT_DIR + '/' + settings.STATIC_URL  + 'img/creatives/' + file_nm
					thumb_img_loc = settings.PROJECT_DIR + '/' + settings.STATIC_URL  + 'img/creatives/' + file_nm_thumb
				
				img.save(img_loc)
				img_thumb.save(thumb_img_loc)
				
		except Error as e:
			err_cd = "99"
			msg = "System error has occured while saving roomview file. Can't proceed."
			return( JsonResponse({'err_cd': err_cd, 'msg': msg }, safe=False) )					
					
		url = 'img/creatives/' + file_nm
		thumbnail_url = 'img/creatives/' + file_nm_thumb
	
		## Create Gallery Wall Main Record
		gal = Gallery(
			title = title,
			description = desc,
			room_id = room_id,
			placement_id = placement_id,
			room_view_url = url,
			room_view_thumbnail_url = thumbnail_url,
			set_of = set_of,
			stock_image_category = None,
			category_disp_priority = None,
			is_published = False,
			colors = colors,
			key_words = key_words
		)
		gal.save()
		
		for n in range(num_of_variations):
			wall_area_width = int(request.POST.get('wall_area_width_'+str(n+1), '0'))
			wall_area_height = int(request.POST.get('wall_area_height_'+str(n+1), '0'))
			
			## Create Variation
			gal_variation = Gallery_variation(
				gallery = gal,
				price = 0,
				is_parent = True if n==0 else False,
				wall_area_width = wall_area_width,
				wall_area_height = wall_area_height
			)
			gal_variation.save()
			for i in range(set_of):
				product_id = int(request.POST.get('product_id_' +str(i), '0'))
				print_medium_id = request.POST.get('print_medium_id_' +str(i), '')
				moulding_id = int(request.POST.get('moulding_id_' +str(i), '0'))
				if moulding_id == 0:
					mould_id = None
				mount_id = int(request.POST.get('mount_id_' +str(i), '0'))
				if mount_id == 0:
					mount_id = None
				mount_color = request.POST.get('mount_color_' +str(i), '')
				mount_size = int(request.POST.get('mount_size_' +str(i), '0'))
				stretch_id = int(request.POST.get('stretch_id_' +str(i), '0')) if print_medium_id == 'CANVAS' else None
				if stretch_id == 0:
					stretch_id = None
				board_id = 1 if print_medium_id == 'PAPER' else None
				if board_id == 0:
					board_id = None
				acrylic_id = 1 if print_medium_id == 'PAPER' else None
				if acrylic_id == 0:
					acrylic_id = None

				image_width = int(request.POST.get('image_width_' +str(n+1) + "_" +str(i), '0'))
				image_height = int(request.POST.get('image_height_'+str(n+1) + "_" +str(i), '0'))

				## Create products under the variation
				gal_items = Gallery_item(
					gallery = gal,
					gallery_variation = gal_variation,
					product_id = product_id,
					product_name = '',
					product_type_id = 'STOCK-IMAGE',
					moulding_id = moulding_id,
					moulding_size = None,
					print_medium_id = print_medium_id,
					mount_id = mount_id,
					mount_size = mount_size,
					board_id = board_id,
					acrylic_id = acrylic_id,
					stretch_id = stretch_id,
					image_width = image_width,
					image_height = image_height
				)
				gal_items.save()
		
	except DatabaseError as e:
		err_cd = '99', 
		msg = 'System Error while creating the gallery wall'
		return JsonResponse({"err_cd":err_cd, 'msg': msg})

	## Publish the Gallery Wall
	g = Gallery.objects.filter(gallery_id = gal.gallery_id).update(
		is_published = True)
	
	## Update price
	try:
		update_gallery_prices(gal.gallery_id)
	except DatabaseError as e:
		err_cd = '99', 
		msg = 'System Error while updating the gallery prices'
		return JsonResponse({"err_cd":err_cd, 'msg': msg})		
		
	return JsonResponse({"err_cd":err_cd, 'msg': msg})		
