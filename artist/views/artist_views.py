from django.shortcuts import render, redirect
from django.conf import settings
from django.contrib.auth import login as auth_login
from django.contrib.auth.models import User
from django.core.paginator import EmptyPage, PageNotAnInteger, Paginator
from django.views.decorators.csrf import csrf_exempt
from django.db import IntegrityError, DatabaseError, Error
from django.contrib.auth.decorators import login_required
from django.contrib.admin.views.decorators import staff_member_required
from django.db.models import Count, Q, F
from django.http import HttpResponse, JsonResponse

from artist.models import Artist_group, Artist_sms_email, Artist, Artist_original_art, Artist_stock_image, Generate_art_number
from artevenue.models import Country, State, City, Pin_code, Ecom_site, Original_art
from artevenue.models import Original_art_original_art_category, Stock_image_category, Stock_image, Stock_image_stock_image_category
from artevenue.models import Wishlist, Wishlist_item_view, Publisher_price
from artevenue.models import Print_medium, Cart_item_view

from artist.forms import artistGroupForm, artistRegisterForm, artistUserForm, artistProfileForm
from artevenue.forms import registerForm

from artevenue.views import price_views, frame_views
from artevenue.decorators import is_artist

from django.contrib import messages
import datetime
import re
from decimal import Decimal


from PIL import Image

ecom = Ecom_site.objects.get(pk=settings.STORE_ID)
wall_colors = ['255,255,255', '255,255,224', '242,242,242', '230,242,255', '65,182,230', '64,224,208', '204,255,204', '128,128,0', '255,255,179', '255,205,72', '255,215,0', '255,230,230', '137,46,58', '255,0,0']
env = settings.EXEC_ENV

def register_as_artist(request, email=None):
	msg =''
	if request.method == 'POST':	
		next = request.POST['curr_pg']
		form = artistUserForm(request.POST)
		artistform = artistRegisterForm(request.POST)
		if form.is_valid():
			if artistform.is_valid():
				user = form.save()
				auth_login(request, user, backend='django.contrib.auth.backends.ModelBackend')
				
				artistf = artistform.save(commit=False)
				artistf.user = user
				artistf.save()

				# Update email, sms table				
				tday = datetime.datetime.today()
				a_email = Artist_sms_email(
					user = user,
					msg_type = 'NEW-ACCNT',
					email_sent = False,
					sms_sent = False,
					created_date = tday,	
					updated_date = tday
				)
				a_email.save()
				
				# After successful sign up redirect to cuurent page
				return redirect('artist_registration_confirmation', id=user.id)
	else:
		email = request.GET.get('email', '')
		if email:
			form = artistUserForm({'email':email})
			artistform = artistRegisterForm()
		else:
			form = artistUserForm()
			artistform = artistRegisterForm()


	country_list = Country.objects.all()
	country_arr = []
	for c in country_list:
		country_arr.append(c.country_name)
		
	state_list = State.objects.all()
	state_arr = []
	for s in state_list:
		state_arr.append(s.state_name)
		
	
	city_list = City.objects.all()
	city_arr = []
	for ct in city_list:
		city_arr.append(ct.city)
	
	pin_code_list = Pin_code.objects.all()
	pin_code_arr = []
	for p in pin_code_list:
		pin_code_arr.append(p.pin_code)
		
		
	return render(request, "artist/artist_registration.html", {'form':form, 
			'artistform':artistform, 'country_arr':country_arr, 'state_arr':state_arr,
			'city_arr':city_arr, 'pin_code_arr':pin_code_arr} )
	
@login_required
def artist_registration_confirmation(request, id):

	try:
		artist = Artist.objects.get(user_id=id)
	except Artist.DoesNotExist:
		artist = {}
	return render(request, "artist/artist_registration_confirmation.html", {'artist':artist} )


@is_artist
def create_artist_profile(request):
	a1 = a2 = a3 = a4 = a5 = ''	
	e1 = e2 = e3 = e4 = e5 = ''	
	try:
		userObj = User.objects.get(username = request.user)
		artist = Artist.objects.get(user = userObj)
		
	except Artist.DoesNotExist:
		artist = None
	except User.DoesNotExist:
		userObj = None
		artist = None
		
	if artist:
		if artist.artist_showcase1:
			achievements = artist.artist_showcase1.split('<br />')
			cnt = 0
			for s in achievements:
				cnt = cnt+1
				if cnt == 1:
					a1 = s
				if cnt == 2:
					a2 = s
				if cnt == 3:
					a3 = s
				if cnt == 4:
					a4 = s
				if cnt == 5:
					a5 = s

		if artist.artist_showcase2:
			events = artist.artist_showcase2.split('<br />')
			cnt = 0
			for e in events:
				cnt = cnt+1
				if cnt == 1:
					e1 = e
				if cnt == 2:
					e2 = e
				if cnt == 3:
					e3 = e
				if cnt == 4:
					e4 = e
				if cnt == 5:
					e5 = e
		
		
	return render(request, "artist/create_artist_profile.html", {'artist':artist,
		'e1': e1, 'e2': e2, 'e3': e3, 'e4': e4, 'e5': e5, 'a1': a1, 'a2': a2, 'a3': a3, 'a4': a4, 'a5': a5})

@login_required
def artist_webpage(request, url_name, cat_id = '', page = 1):
	ikeywords = request.GET.get('keywords', '')
	keywords = ikeywords.split()
	keyword_filter = False # Turned on only if a keyword filter is present (through the AJAX call)
	sortOrder = request.GET.get("sort")
	show = request.GET.get("show", '50')

	if page is None or page == 0:
		page = 1 # default

	try:
		artist = Artist.objects.get(url_name__iexact=url_name)
		form = artistProfileForm(instance=artist)
	except Artist.DoesNotExist:
		artist = {}

	a_prods = Artist_original_art.objects.filter(artist_id = artist.artist_id).values('product_id')
	products = Original_art.objects.filter(product_id__in = a_prods, 
				is_published = True)
				
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
				
	return render(request, "artist/artist_webpage.html", {'form':form,
		'artist':artist,'prods':prods} )


@staff_member_required
def create_artist_group(request):
	##curr_groups = Artist_group.objects.all()
	if request.method == 'POST':	
		next = request.POST['curr_pg']
		form = registerForm(request.POST)

		if form.is_valid():
			grp = form.save()

			# After successful sign up redirect to current page
			return redirect('index')
	else:
		form = artistGroupForm()
		
	return render(request, "artist/create_artist_group.html", {'form':form,
			##'curr_groups':curr_groups
			})
			
			
def get_original_arts(request, cat_nm = None, page = None, curated_coll_id = None):
	if cat_nm:
		#if cat_nm != 'Still-Life' and cat_nm != 'X-Ray':
		#	cat_nm = cat_nm.replace("-", " ")
		try:
			product_cate = Stock_image_category.objects.filter(url_suffix = cat_nm).first()
			if product_cate :				
				cat_id = product_cate.category_id
			else:
				cat_id = 0
				product_cate = None					
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

	#prod_categories = Stock_image_category.objects.filter(store_id=settings.STORE_ID, trending = True )
	prod_categories = Original_art_original_art_category.objects.all().select_related('stock_image_category').distinct()
	print(prod_categories)
	if cat_id:
		category_prods = Original_art_original_art_category.objects.filter(
				stock_image_category_id = cat_id).values('original_art_id')
		products = Original_art.objects.filter(product_id__in = category_prods, 
				is_published = True)
	elif curated_coll_id:
		curated_coll = Curated_collection.objects.filter(curated_category_id = curated_coll_id,
				product_type_id = 'ORIGINAL-ART').values('product_id')
		try:
			product_cate = Curated_category.objects.get(category_id = curated_coll_id);
		except Curated_category.DoesNotExist:
			product_cate = {}
		products = Original_art.objects.filter(product_id__in = curated_coll, 
			is_published = True)
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
		products = products.filter(aspect_ratio = ratio, art_width__gte = filt_width, art_height__gte = filt_height)

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
	
	products = products.order_by('category_disp_priority')
	
	price = Publisher_price.objects.filter(print_medium_id = 'PAPER') 
	
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
	
	template = "artevenue/original_art_by_category.html"

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


def original_art_detail(request, prod_id = ''):
	cart_item_id = request.GET.get("cart_item_id", "")
	wishlist_item_id = request.GET.get("wishlist_item_id", "")
	if not prod_id or prod_id == '' :
		prod_id = request.GET.get("product_id", "")
	
	if prod_id == None:
		render(request, "artevenue/original_art_detail.html", {} )
	
	# get the product
	try:
		product = Original_art.objects.get(is_published = True, pk=prod_id)
	except Original_art.DoesNotExist:
		render(request, "artevenue/original_art_detail.html", {} )
		
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
	per_sqinch_price = price_views.get_per_sqinch_price(prod_id, 'STOCK-IMAGE')
	per_sqinch_paper = per_sqinch_price['per_sqin_paper']
	per_sqinch_canvas = per_sqinch_price['per_sqin_canvas']

	# get mouldings
	mouldings = frame_views.get_mouldings(request)
	# defaul we send is for PAPER
	paper_mouldings_apply = mouldings['paper_mouldings_apply']
	paper_mouldings_show = mouldings['paper_mouldings_show']
	moulding_diagrams = mouldings['moulding_diagrams']
	# get mounts
	mounts = frame_views.get_mounts(request)

	# get arylics
	acrylics = frame_views.get_acrylics(request)
	
	# get boards
	boards = frame_views.get_boards(request)

	# get Stretches
	stretches = frame_views.get_stretches(request)

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

	request.session.set_test_cookie()   ## To test if cookie is enabled on the browser. If not display message in Size and Color Tool.

	return render(request, "artevenue/original_art_detail.html", {'product':product,
		'prod_categories':prod_categories, 'printmedium':printmedium, 'product_category':product_category,
		'mouldings_apply':paper_mouldings_apply, 'mouldings_show':paper_mouldings_show, 'mounts':mounts,
		'per_sqinch_paper':per_sqinch_paper, 'per_sqinch_canvas':per_sqinch_canvas, 'acrylics':acrylics,
		'boards':boards, 
		#######'img_with_all_mouldings':img_with_all_mouldings, 
		'stretches':stretches,
		'cart_item':cart_item_view, 'art_width':art_width, 'art_height':art_height,
		'prods':similar_products, 'price':price, 'wishlist_prods':wishlist_prods,
		'wall_colors':wall_colors} )

@csrf_exempt
def upload_artist_photo(request):
	today = datetime.date.today()
	img_str = ''
	if request.method == 'POST':
		from PIL import Image, ExifTags
		from io import BytesIO
		import base64

		file = request.FILES.get('file')
		session_id = request.session.session_key
		user = None
		
		if request.user.is_authenticated:
			try:
				user = User.objects.get(username = request.user)
				artist = Artist.objects.get(user = user)
			except User.DoesNotExist:
				user = None
			except Artist.DoesNotExist:
				artist = None
		else:
			HttpResponse(img_str)

		if artist :
			artist.profile_photo = file
			artist.updated_date = today
			artist.save()
			
			im=Image.open(artist.profile_photo)
			
			exifData = {}
			exif_data = im._getexif()
			if exif_data:
				for tag, value in exif_data.items():
					decodedTag = ExifTags.TAGS.get(tag, tag)
					exifData[decodedTag] = value		
			
				if exifData :
					if 'Orientation' in exifData:
						if exifData['Orientation'] == 6:
							im.rotate(90)
						if exifData['Orientation'] == 3:
							im.rotate(180)
						if exifData['Orientation'] == 8:
							im.rotate(270)
				
			buffered = BytesIO()
			im.save(buffered, format='JPEG')
			img_data = buffered.getvalue()
			img_str = base64.b64encode(img_data)						

	return HttpResponse(img_str)

@csrf_exempt
def validate_url_name(request):
	
	url = request.POST.get('url_name', '')
	artist_id = request.POST.get('artist_id', '')
	
	if url == '':
		return JsonResponse( {'ret_msg': "Url name can't be blank"})
		
	if url:		
		if re.search("^[a-zA-Z0-9_-]+$", url) is None:
			return JsonResponse( {'ret_msg': "The webpage URL you entered is invalid. It can only contain alphabets, number, '-' & '_' and no blanks spaces are allowed."})

	artist = Artist.objects.filter(url_name__iexact = url).exclude(artist_id = artist_id)
	
	if artist:
		return JsonResponse( {'ret_msg': "The webpage URL you entered is already taken. Please choose another webpage URL."})
	
	a = Artist.objects.filter(artist_id = artist_id).update(url_name = url)
	
	return JsonResponse({'ret_msg': "SUCCESS"})

@csrf_exempt
@is_artist
def save_artist_profile(request):
	if request.method == 'POST':
		artist_id = request.POST.get("artist_id", "")
		mode = request.POST.get("mode", "")
		profile_name = request.POST.get("profile_name", "").strip()
		url_name = request.POST.get("url_name", "").strip()
		tag_line = request.POST.get("tag_line", "").strip()
		profile = request.POST.get("profile", "")
		a1 = request.POST.get("a1", "").strip()
		a2 = request.POST.get("a2", "").strip()
		a3 = request.POST.get("a3", "").strip()
		a4 = request.POST.get("a4", "").strip()
		a5 = request.POST.get("a5", "").strip()

		e1 = request.POST.get("e1", "").strip()
		e2 = request.POST.get("e2", "").strip()
		e3 = request.POST.get("e3", "").strip()
		e4 = request.POST.get("e4", "").strip()
		e5 = request.POST.get("e5", "").strip()
		
		achievements = ''
		if a1:
			achievements = achievements + a1
		if a2:
			achievements = achievements + '<br />'+ a2
		if a3:
			achievements = achievements + '<br />'+ a3
		if a4:
			achievements = achievements + '<br />'+ a4
		if a5:
			achievements = achievements + '<br />'+ a5

		events = ''
		if e1:
			events = events + e1
		if e2:
			events = events + '<br />'+ e2
		if e3:
			events = events + '<br />'+ e3
		if e4:
			events = events + '<br />'+ e4
		if e5:
			events = events + '<br />'+ e5

		if request.user.is_authenticated:
			try:
				artist = Artist.objects.get(artist_id = artist_id)
			except Artist.DoesNotExist:
				artist = None

			if url_name:		
				if re.search("^[a-zA-Z0-9_-]+$", url_name) is None:
					return JsonResponse( {'ret_msg': "The webpage URL you entered is invalid. It can only contain alphabets, number, '-' & '_' and no blanks spaces are allowed."})
			
			oth_a = Artist.objects.filter(url_name__iexact = url_name).exclude(artist_id = artist_id)
			if oth_a:
				return JsonResponse( {'ret_msg': "The webpage URL you entered is already taken. Please choose another webpage URL."})

			if mode == 'NEXT':
				if not profile_name:
					return JsonResponse({'ret_msg': "Your display name can't be blank"})					
				if not url_name:
					return JsonResponse({'ret_msg': "Your url name can't be blank. this become part of the url of your webpage on our website."})
				if not profile:
					return JsonResponse({'ret_msg': "Please include a few words about yourself. This will be displayed on your webpage."})					

			
			artist.profile_name = profile_name
			artist.url_name = url_name
			artist.artist_profile = profile
			artist.profile_tagline = tag_line
			artist.artist_showcase1_name = 'ACHIEVEMENTS'
			artist.artist_showcase1 = achievements
			artist.artist_showcase2_name = 'EVENTS'
			artist.artist_showcase2 = events
			
			artist.save()
		else:
			return JsonResponse({'ret_msg': "FAILURE"})

		return JsonResponse({'ret_msg': "SUCCESS"})
	else:
		return JsonResponse({'ret_msg': "FAILURE"})		
	

@is_artist
def upload_art(request, part_number=None):
	today = datetime.date.today()
	artist = {}
	artwork = {}
	art_print = {}
	category = ''
	save_draft = False 
	submit_artwork = False
	art_print_width = None
	art_print_height = None
	sell_original = False
	sell_art_print = False
	saved_msg = False
	submitted_msg = False
	artist_approved = False
	artevenue_approved = False
	artevenue_disapproved = False
	disapprove_msg = ''
	a_orig_artwork = {}
	a_stk_image = {}
	
	if request.user.is_authenticated:
		try:
			user = User.objects.get(username = request.user)
			artist = Artist.objects.get(user = user)
		except User.DoesNotExist:
			user = None
		except Artist.DoesNotExist:
			artist = None
	if artist is None:
		return render(request, "artist/upload_artwork.html", {})

	medium_list = Original_art.MEDIUM
	surface_list = Original_art.SURFACE
	img_type_list = Original_art.IMAGE_TYPE
	category_list = Stock_image_category.objects.all().distinct('name').order_by('name')


	if part_number is None:
		part_number = request.POST.get("part_number", "")
		if part_number == '':
			part_number = request.GET.get("part_number", "")

	## If part number exists, then artwork has already been uploaded and this is either a save or a submit for review
	if part_number:
		artwork = Original_art.objects.filter(part_number = part_number).first()
		a_orig_artwork = Artist_original_art.objects.filter(product = artwork).first()
		orig_art_id = artwork.product_id
		art_print = Stock_image.objects.filter(part_number = part_number).first()
		a_stk_image = Artist_stock_image.objects.filter( product = art_print).first()
		stock_image_id = art_print.product_id
		
		## Get the category
		if artwork :
			#sell_original = artwork.is_published
			cate = Original_art_original_art_category.objects.filter(original_art = artwork).first()
			if cate:
				category = str(cate.stock_image_category_id)
		if art_print:
			art_print_width = art_print.max_width
			art_print_height = art_print.max_height 


	if request.POST:
		if "SAVE_DRAFT" in request.POST:
			save_draft = True
		else:
			save_draft = False
			
		if "SUBMIT_ARTWORK" in request.POST:
			submit_artwork = True
		else:
			submit_artwork = False
	else:
		submit_artwork = False
		save_draft = False
		
	if save_draft or submit_artwork :
		artwork_image = request.FILES.get('artwork_image')
		iart_type = request.POST.get("art_type", "")
		if iart_type == 'PAINTING':
			art_type = 0
		elif iart_type == 'PHOTOGRAPH':
			art_type = 1
		else:
			art_type = 0
		title = request.POST.get("title", "")
		category = request.POST.get("category", "")
		art_width = Decimal(request.POST.get("art_width", "0"))
		art_height = Decimal(request.POST.get("art_height", "0"))
		max_width = Decimal(request.POST.get("art_print_width", "0"))
		max_height = Decimal(request.POST.get("art_print_height", "0"))
		medium = request.POST.get("medium", "")
		surface = request.POST.get("surface", "")
		surface_description = request.POST.get("surface_description", "")
		art_print_option = request.POST.get("art_print_option", "")
		if max_width < 8:
			msg = "The minimum required art print width is 8 inch. The image you have uploaded doesn't have enough resolution and can't be printed with 8 inch width or more. Please upload another image of this artwork with better resolution."
			return render(request, "artist/upload_artwork.html", {'msg': msg, 'artist':artist, 'medium_list': medium_list, 'artwork': artwork,
				'surface_list': surface_list, 'img_type_list': img_type_list, 'part_number': part_number, 'category_list': category_list,
				'art_print_width':art_print_width
				, 'art_print_height':art_print_height, 'category': category , 'orig_artwork_sts': a_orig_artwork})
			
		if art_print_option == 'O':
			art_print_allowed = False
		else:
			art_print_allowed = True
		
		str_p = request.POST.get("original_art_price", "0")
		if str_p == '':
			str_p = '0'
		original_art_price = float(str_p)
		artist_price = original_art_price	## To store the original art price before tax
		
		if art_type == 0:
			if original_art_price < 5000:
				msg = "The minimum original artwork price required is Rs. 5,000."
				return render(request, "artist/upload_artwork.html", {'msg': msg, 'artist':artist, 'medium_list': medium_list, 'artwork': artwork,
					'surface_list': surface_list, 'img_type_list': img_type_list, 'part_number': part_number, 'category_list': category_list,
					'art_print_width':art_print_width
					, 'art_print_height':art_print_height, 'category': category , 'orig_artwork_sts': a_orig_artwork})
				
		original_art_price = Decimal( round(original_art_price + (original_art_price*0.12)) ) ## Add tax
		keywords = request.POST.get("keywords", "")
		colors = request.POST.get("colors", "")


		if art_type == 1:
			original_art_price = 0
			art_width = 0
			art_height = 0
			medium = ''
			surface = ''
			surface_description = ''
			art_print_option = 'A'
			art_print_allowed = True
			
		if not artwork:
			# Generate new part number & original art id
			part_number = get_next_part_number()			
			orig_art_id = get_next_orig_art_id()
			## Creat new artwork object`
			artwork = Original_art()
			
		if not art_print :
			stock_image_id = get_next_stock_image_id()
			## Creat new art print object
			art_print = Stock_image()
			
		if not artwork_image:
			if env == 'PROD':
				img_highres = Image.open('/home/artevenue/website/estore/static/' + artwork.high_resolution_url)
			else:			
				img_highres = Image.open('c:/artevenue/estore/artevenue/static/' + artwork.high_resolution_url)
		else:
			img_highres = Image.open(artwork_image)
		wd = img_highres.width
		ht = img_highres.height
		aspect_ratio = round(Decimal(wd)/Decimal(ht), 18)
		if wd > ht :
			orientation = 'horizontal'
		elif wd == ht:
			orientation = 'square'
		else:
			orientation = 'vertical'
							
		if env == 'PROD':
			lowres_name = 'image_data/artevenue/artprint/' + part_number + "_lowres.jpg"
			lowres_name_save = '/home/artevenue/website/estore/static/image_data/artevenue/artprint/' + part_number + "_lowres.jpg"
			highres_name = 'image_data/artevenue/original/' + part_number + "_highres.jpg"
			highres_name_save = '/home/artevenue/website/estore/static/image_data/artevenue/original/' + part_number + "_highres.jpg"
			thumbnail_name = 'image_data/artevenue/artprint/' + part_number + "_thumb.jpg"
			thumbnail_name_save = '/home/artevenue/website/estore/static/image_data/artevenue/artprint/' + part_number + "_thumb.jpg"
		else:
			lowres_name = 'image_data/artevenue/artprint/' + part_number + "_lowres.jpg"
			lowres_name_save = 'c:/artevenue/estore/artevenue/static/image_data/artevenue/artprint/' + part_number + "_lowres.jpg"
			highres_name = 'image_data/artevenue/original/' + part_number + "_highres.jpg"
			highres_name_save = 'c:/artevenue/estore/artevenue/static/image_data/artevenue/original/' + part_number + "_highres.jpg"
			thumbnail_name = 'image_data/artevenue/artprint/' + part_number + "_thumb.jpg"
			thumbnail_name_save = 'c:/artevenue/estore/artevenue/static/image_data/artevenue/artprint/' + part_number + "_thumb.jpg"
			
		if wd < 1000:
			w = wd
		else:
			w = 1000
		img_lowres = img_highres.resize((w, w/aspect_ratio))
		img_thumbnail = img_highres.resize((75, 75/aspect_ratio))
		
		img_lowres.save(lowres_name_save, 'JPEG')
		img_highres.save(highres_name_save, 'JPEG')
		img_thumbnail.save(thumbnail_name_save, 'JPEG')
					
		
		## Update/Insert Original Art
		artwork.product_id = orig_art_id
		artwork.product_type_id = 'ORIGINAL-ART'
		artwork.name = title
		artwork.description = ''
		artwork.price = 0
		artwork.available_on = None
		artwork.part_number = part_number
		artwork.is_published = False
		artwork.charge_taxes = True
		artwork.featured = False
		artwork.has_variants = False
		artwork.aspect_ratio = aspect_ratio
		artwork.image_type =  art_type
		artwork.orientation = orientation
		artwork.max_width = max_width
		artwork.max_height = max_height
		artwork.min_width = 8
		artwork.publisher = '01'
		artwork.artist = artist.profile_name
		artwork.colors = colors
		artwork.key_words = keywords
		artwork.url = lowres_name
		artwork.thumbnail_url = thumbnail_name
		artwork.high_resolution_url = highres_name
		artwork.art_width = art_width
		artwork.art_height = art_height
		artwork.art_medium = medium
		artwork.art_surface = surface
		artwork.art_surface_desc = surface_description
		artwork.category_disp_priority = None
		artwork.art_print_allowed = art_print_allowed
		artwork.original_art_price = original_art_price
		artwork.available_qty = 1	
		artwork.sold_qty = 0	
		artwork.stock_image = None

		artwork.save()

		if submit_artwork:
			artist_approved = True
		else:
			artist_approved = False

		if not a_orig_artwork:
			a_orig_artwork = Artist_original_art()			
			a_orig_artwork.artist = artist
			a_orig_artwork.product = artwork
			a_orig_artwork.uploaded_date = today
		a_orig_artwork.sell_mode = art_print_option
		a_orig_artwork.artist_listed = artist_approved
		a_orig_artwork.approved = False
		a_orig_artwork.approval_date = None
		a_orig_artwork.artist_price = artist_price	#store the original art price before tax
		a_orig_artwork.save()

		## Update/Insert Art Print
		art_print.store = ecom
		art_print.product_id = stock_image_id
		art_print.product_type_id = 'STOCK-IMAGE'
		art_print.name = title
		art_print.description = ''
		art_print.price = 0
		art_print.available_on = None
		art_print.part_number = part_number
		art_print.is_published = False
		art_print.charge_taxes = True
		art_print.featured = False
		art_print.has_variants = False
		art_print.aspect_ratio = aspect_ratio
		art_print.image_type =  art_type
		art_print.orientation = orientation
		art_print.max_width = max_width
		art_print.max_height = max_height
		art_print.min_width = 8
		art_print.publisher = '01'
		art_print.artist = artist.profile_name
		art_print.colors = colors
		art_print.key_words = keywords
		art_print.url = lowres_name
		art_print.thumbnail_url = thumbnail_name
		art_print.category_disp_priority = None

		art_print.save()

		artwork.stock_image = art_print
		artwork.save()


		if not a_stk_image:
			a_stk_image = Artist_stock_image()
			a_stk_image.artist = artist
			a_stk_image.product = art_print
			
		a_stk_image.artist_listed = artist_approved
		a_stk_image.approved = False
		a_stk_image.approval_date = None
		a_stk_image.save()
			
		
		oc = Original_art_original_art_category.objects.filter(
			original_art = artwork)
		if oc: 
			cate_orig = Original_art_original_art_category.objects.filter(
				original_art = artwork).update(stock_image_category_id = category)
		else:
			cate_orig = Original_art_original_art_category(
				original_art = artwork,
				stock_image_category_id = category
			)
			cate_orig.save()

		pc = Stock_image_stock_image_category.objects.filter(stock_image = art_print)
		if pc:
			cate_stki = Stock_image_stock_image_category.objects.filter(
				stock_image = art_print).update(stock_image_category_id = category)
		else:
			cate_stki = Stock_image_stock_image_category(
				stock_image = art_print,
				stock_image_category_id = category
			)		
			cate_stki.save()
		
		if save_draft :
			saved_msg = True
		if submit_artwork :
			submitted_msg = True
	
	else:
		if a_orig_artwork:
			if a_orig_artwork.approved:
				artevenue_approved = True
			if a_orig_artwork.artist_listed:
				artist_approved = True
			if a_orig_artwork.unapproved:
				artevenue_disapproved = True
				disapprove_msg = a_orig_artwork.unapproval_reason
				

	if submit_artwork:
		return render(request, "artist/confirm_artwork_submit.html", {'artist':artist, 'medium_list': medium_list, 'artwork': artwork,
			'surface_list': surface_list, 'img_type_list': img_type_list, 'part_number': part_number, 'category_list': category_list,
			'art_print_width':art_print_width,
			'art_print_height':art_print_height, 'category': category , 'saved_msg': saved_msg , 'orig_artwork': a_orig_artwork,
			'submitted_msg': submitted_msg, 'artist_approved': artist_approved, 'artevenue_approved': artevenue_approved})
	
	else:
		return render(request, "artist/upload_artwork.html", {'artist':artist, 'medium_list': medium_list, 'artwork': artwork,
			'surface_list': surface_list, 'img_type_list': img_type_list, 'part_number': part_number, 'category_list': category_list,
			'art_print_width':art_print_width,
			'art_print_height':art_print_height, 'category': category , 'saved_msg': saved_msg , 'orig_artwork': a_orig_artwork,
			'submitted_msg': submitted_msg, 'artist_approved': artist_approved, 'artevenue_approved': artevenue_approved,
			'disapprove_msg': disapprov_msg, 'artevenue_disapproved': artevenue_disapproved})
	


def get_next_part_number():

	num = 0

	prefix = 'AVP-'
	suffix = '-0920'
	typ = 'PART'
	
	rec = Generate_art_number.objects.filter(publisher = 'ARTEVENUE', prefix = 'AVP-', suffix = '-0920', type = 'PART').first()
	
	if rec :
		num = rec.current_number + 1
	else :
		num = 1
		
	# Update generated number in DB
	if rec :
		Generate_art_number.objects.filter(publisher = 'ARTEVENUE', prefix = 'AVP-', suffix = '-0920', type = 'PART').update(
			current_number = num)
	else:
		gen_num = Generate_art_number(
			publisher = 'ARTEVENUE', 
			prefix = 'AVP-', 
			suffix = '-0920', 
			type = 'PART',
			current_number = num
			)	
		gen_num.save()
		
	part_number = ''
	
	if prefix:
		part_number = prefix + str(num)
	if suffix:
		part_number = (part_number + suffix )
	else:
		part_number = (str(num))
		
	return part_number 	


def get_next_orig_art_id():
	num = 0
	typ = 'PROD'
	
	rec = Generate_art_number.objects.filter(publisher = 'ARTEVENUE', type = 'ORIG').first()
	
	if rec :
		num = rec.current_number + 1
	else :
		num = 1		
	# Update generated number in DB
	if rec :
		Generate_art_number.objects.filter(publisher = 'ARTEVENUE', type = 'ORIG').update(
			current_number = num)
	else:
		gen_num = Generate_art_number(
			publisher = 'ARTEVENUE', 
			type = 'ORIG',
			current_number = num
		)	
		gen_num.save()	
	
	prod_id = (str(num))
	
	return prod_id


def get_next_stock_image_id():
	num = 0
	typ = 'PROD'
	
	rec = Generate_art_number.objects.filter(publisher = 'ARTEVENUE', type = 'STKI').first()
	
	if rec :
		num = rec.current_number + 1
	else :
		num = 1		
	# Update generated number in DB
	if rec :
		Generate_art_number.objects.filter(publisher = 'ARTEVENUE', type = 'STKI').update(
			current_number = num)
	else:
		
		gen_num = Generate_art_number(
			publisher = 'ARTEVENUE', 
			type = 'STKI',
			current_number = num
		)	
		gen_num.save()	
		
	prod_id = (str(num))
	
	return prod_id

@staff_member_required
def original_artwork_approval(request):
	artworks = Artist_original_art.objects.filter(artist_listed = True, approved = False, unapproved = False)
	msg = ""
	return render(request, "artist/original_artwork_approval.html",
		{ 'msg': msg, 'env': env, 'artworks': artworks})
		

@staff_member_required
def set_original_artwork_approval(request):
	today = datetime.datetime.today()
	sts = 'SUCCESS'

	id = request.GET.get('id', '');
	if id != None and id != '' :
		try:
			artwork = Artist_original_art.objects.get(id = id, artist_listed = True, approved = False, unapproved = False)
			msg = ""
			action = request.GET.get('action', '').upper();
			# If approved for listing
			if action == 'A':
				artwork.approved = True
				artwork.unapproved = False
				artwork.approval_date = today
				artwork.save()
				## Publish the artwork
				try:
					orig_art = Original_art.objects.get(product_id = artwork.product_id)
					orig_art.is_published = True
					try:
						stk_img = Stock_image.objects.get(product_id = orig_art.stock_image_id)
						stk_img.is_published = True
						orig_art.save()
						stk_img.save()
					except Stock_image.DoesNotExist:
						sts = 'FAILURE'						
				except Original_art.DoesNotExist:
					sts = 'FAILURE'

			# If unapproved for listing
			if action == 'D':
				artwork.approved = False
				artwork.unapproved = True
				artwork.unapproval_date = today
				artwork.save()
				try:
					orig_art = Original_art.objects.get(product_id = artwork.product_id)
					orig_art.is_published = False
					try:
						stk_img = Stock_image.objects.get(product_id = orig_art.stock_image_id)
						stk_img.is_published = False
						orig_art.save()
						stk_img.save()
					except Stock_image.DoesNotExist:
						sts = 'FAILURE'						
				except Original_art.DoesNotExist:
					sts = 'FAILURE'
			
		except Artist_original_art.DoesNotExist:
			sts = 'FAILURE'
	else:
		sts = 'FAILURE'
	return JsonResponse({"status":sts})
	
	
@csrf_exempt
def show_all_original_art_categories(request, sortorder=None):
	if not sortorder:
		sort_order = request.GET.get("sortorder", '')
	# Get all the categories along with count of images in each

	all_cnt = Original_art.objects.filter(is_published = True).count()

	if sort_order:
		if sort_order == 'N':
			categories_list = Stock_image_category.objects.annotate(Count(
				'original_art_category')).filter(
				original_art_category__count__gt = 0).exclude(
				name = '').exclude(name = '#N/A').exclude(
				name = 'Passion').exclude(name = 'Nude').order_by('name')
		if sort_order == 'C':
			categories_list = Stock_image_category.objects.annotate(Count(
				'original_art_category')).filter(
				original_art_category__count__gt = 0).exclude(
				name = '').exclude(name = '#N/A').exclude(
				name = 'Passion').exclude(name = 'Nude').order_by('-original_art_category__count')
	else:
		categories_list = Stock_image_category.objects.annotate(Count(
			'original_art_category')).filter(
			original_art_category__count__gt = 0).exclude(
			name = '').exclude(name = '#N/A').exclude(
			name = 'Passion').exclude(name = 'Nude').order_by('name')

	if request.is_ajax():
		template = "artist/show_all_original_art_categories_include.html"
	else:
		template = "artist/show_all_original_art_categories.html"

	return render(request, template, {'categories':categories_list,
	'cnt': categories_list.count(), 'all_cnt':all_cnt, 'env': env})	
	
	
	
@is_artist
def get_my_artworks(request):
	try:
		userObj = User.objects.get(username = request.user)
		artist = Artist.objects.get(user = userObj)
		
	except Artist.DoesNotExist:
		artist = None
	except User.DoesNotExist:
		userObj = None
		artist = None
	
	startDt = None
	endDt = None	
	page = request.POST.get('page', 1)
	filter_applied = False

	from_date = request.POST.get("fromdate", '')
	if from_date != '' :
		startDt = datetime.datetime.strptime(from_date, "%Y-%m-%d")
		filter_applied = True
		
	to_date = request.POST.get("todate", '')
	if to_date != '' :
		endDt = datetime.datetime.strptime(to_date, "%Y-%m-%d")
		filter_applied = True

	part_number = request.POST.get('part_number', '')
	if part_number:
		filter_applied = True
	
	title = request.POST.get('title', '')
	if title:
		filter_applied = True
	
	artworks = Artist_original_art.objects.filter(artist = artist)
	
	if startDt:
		artworks = artworks.filter(uploaded_date__gte = startDt)
	if endDt:
		artworks = artworks.filter(uploaded_date__lte = endDt)
	if part_number:
		artworks = artworks.filter(product__part_number = part_number)
	if title:
		artworks = artworks.filter(product__name__icontains = title)
		
	
	msg = ""
	return render(request, "artist/artist_artworks.html",
		{ 'msg': msg, 'env': env, 'artworks': artworks, 'filter_applied': filter_applied,
			'startDt':startDt, 'endDt':endDt, 'part_number': part_number, 'title': title})

@is_artist
def delist_artwork(request, part_number=None):

	try:
		userObj = User.objects.get(username = request.user)
		artist = Artist.objects.get(user = userObj)
		
	except Artist.DoesNotExist:
		artist = None
	except User.DoesNotExist:
		userObj = None
		artist = None

	artwork = Original_art.objects.filter(part_number = part_number).first()
	a_orig_artwork = Artist_original_art.objects.filter(product = artwork).first()
	orig_art_id = artwork.product_id

	art_print = Stock_image.objects.filter(part_number = part_number).first()
	a_stk_image = Artist_stock_image.objects.filter(product = art_print).first()
	stock_image_id = art_print.product_id

	if artwork:
		artwork.is_published = False
		artwork.save()
		
	if art_print:
		art_print.is_published = False
		art_print.save()
		
	if a_orig_artwork:
		a_orig_artwork.artist_listed = False
		a_orig_artwork.approved = False
		a_orig_artwork.save()
		
	if a_stk_image:
		a_stk_image.artist_listed = False
		a_stk_image.approved = False
		a_stk_image.save()
	
	msg = ""
	medium_list = Original_art.MEDIUM
	surface_list = Original_art.SURFACE
	img_type_list = Original_art.IMAGE_TYPE
	category_list = Stock_image_category.objects.all().order_by('name')
	return render(request, "artist/delist_artwork.html",
		{ 'msg': msg, 'env': env, 'artwork': artwork, 'medium_list': medium_list, 'surface_list': surface_list,
		'img_type_list': img_type_list, 'category_list': category_list})

@is_artist
def artist_page(request):
	try:
		userObj = User.objects.get(username = request.user)
		artist = Artist.objects.get(user = userObj)
	except Artist.DoesNotExist:
		artist = None
	except User.DoesNotExist:
		userObj = None
		artist = None
	
	return render(request, "artist/artist_page.html", {'artist': artist})

def artist_terms(request):
	try:
		userObj = User.objects.get(username = request.user)
		artist = Artist.objects.get(user = userObj)
	except Artist.DoesNotExist:
		artist = None
	except User.DoesNotExist:
		userObj = None
		artist = None
	
	return render(request, "artist/artist_terms.html", {'artist': artist, 'ecom_site': ecom})

		