from django.shortcuts import render, get_object_or_404
from django.db.models import Count, Q, Max, Sum, F
from django.http import HttpResponse
from django.conf import settings
from django.http import JsonResponse
from django.contrib.auth.decorators import login_required
from django.contrib.admin.views.decorators import staff_member_required
from artevenue.decorators import is_manager, has_accounts_access	
from django.views.decorators.csrf import csrf_exempt
from django.db import IntegrityError, DatabaseError, Error
from django.contrib.auth.models import User
from django.core.paginator import EmptyPage, PageNotAnInteger, Paginator

from django.db.models import Count, Q, Max, Sum, F, Avg

from datetime import datetime, timedelta
import datetime
import csv
import random
import string

from PIL import Image

from artevenue.models import Cart, Stock_image, User_image, Stock_collage, Original_art, Cart_item
from artevenue.models import Product_view, Promotion, Order, Ecom_site, Stock_collage_specs, Collage_stock_image
from artevenue.models import Voucher, Voucher_user, Cart_item_view, Voucher_used
from artevenue.models import Print_medium, Publisher_price, Moulding, Mount, Acrylic, Board, Stretch
from artevenue.models import Order, Order_items_view

from .product_views import *
from .user_image_views import *
from .tax_views import *
from .price_views import *
from .cart_views import *

env = settings.EXEC_ENV
ecom_site = get_object_or_404 (Ecom_site, store_id=settings.STORE_ID )

@is_manager
def coupon_management(request):
	return render(request, 'artevenue/coupon_management.html')


@is_manager
def apply_coupon(request):
	today = datetime.datetime.today()
	msg = None

	if request.method == 'POST':		

		order_id = request.POST.get("order_id", "")
		cart_id = request.POST.get("cart_id", "")
		order = Order.objects.filter(order_id = order_id).first()
		
		if order:
			cart = Cart.objects.filter(cart_id = order.cart_id).first()
		else:	
			cart = None
			
		if order_id:
			order = Order.objects.filter(order_id = order_id).first()
			if order:
				cart = Cart.objects.filter(cart_id = order.cart_id).first()
			else:	
				cart = None
		else:
			order = None
			cart = None
		
		## Refetch order and cart to get updated status
		order = Order.objects.filter(order_id = order_id).first()
		if order:
			cart = Cart.objects.filter(cart_id = order.cart_id).first()
		else:	
			cart = None			
			
	## GET request
	else:
		order = None
		cart = None
		order_num = request.GET.get("order_num", "")
		cart_id = request.GET.get("cart_id", "")
		if order_num:
			order = Order.objects.filter(order_number = order_num).first()
			if order:
				cart = Cart.objects.filter(cart_id = order.cart_id).first()
		elif cart_id:
			cart = Cart.objects.filter(cart_id = cart_id).first()
			order = Order.objects.filter(cart = cart).first()

	coupons = Voucher.objects.filter(effective_from__lte = today,  effective_to__gte = today)
	
	cartitems = Cart_item_view.objects.select_related('product').filter(cart = cart,
				product__product_type_id = F('product_type_id') ).order_by('product_id')
	orderitems = Order_items_view.objects.select_related('product').filter(order = order,
				product__product_type_id = F('product_type_id') ).order_by('product_id')

			
	return render(request, "artevenue/apply_coupon.html",
		{ 'msg': msg, 'env': env,
		 'order': order, 'cart': cart, 'coupons': coupons,
		 'orderitems': orderitems, 'cartitems': cartitems})	

@csrf_exempt
@is_manager
def after_coupon_view(request):
	cart_id = request.POST.get('cart_id', '')
	voucher_code = request.POST.get('voucher_code', '')
	voucher_use_check = request.POST.get('voucher_use_check', 'TRUE')
	today = datetime.date.today()
	## If it's an egift, it's cash, so we just deduct the amount from cart total after
	## tax.
	## If it's a voucher, then we deduct it from cart sub total and then apply tax.

	##voucher_use_check is used to determine if a new product is being added on existing
	## cart with voucher. If so, call this method from add_to_cart_new with 
	## this argument as false, so this method won't check if the voucher is applied to the cart.
	status = "SUCCESS"	
	if voucher_code == '':
		return JsonResponse({"status":"INVALID-CODE"})
	try: 
		user = User.objects.get(username = request.user)
	except User.DoesNotExist:
		user = None	
		
	voucher = Voucher.objects.filter(voucher_code = voucher_code, effective_from__lte = today, 
			effective_to__gte = today, store_id = settings.STORE_ID).first()			
	if not voucher :
		return JsonResponse({"status":"INVALID-CODE"})

	if not user :
		return JsonResponse({"status":"NO-USER"})

	############################################
	## Get the active cart and any voucher disc 
	## already applied
	############################################	
	cart = Cart.objects.filter(cart_id = cart_id).first()
	#cart_items = Cart_item_view.objects.filter(cart_id = cart_id)
	# Check if voucher discount is already applied to cart
	if cart.voucher_disc_amount:
		applied_disc = cart.voucher_disc_amount
	else:
		applied_disc = 0
	#################################################
	## END:  Get the active cart and any voucher disc 
	## already applied
	#################################################

	#############################################
	## Check if voucher is already applied, 
	## if it's already used and then return
	############################################
	if voucher_use_check == 'FALSE':
		if cart.voucher:
			if cart.voucher.voucher_code == voucher_code:
				return JsonResponse({"status":"USED"})
			else:
				if cart.voucher:
					return JsonResponse({"status":"ONLY-ONE"})		
	#############################################
	## END: Check if voucher is already applied, 
	## if it's already used and then return
	############################################

	

	#############################################
	## Check if voucher applies to the user, 
	## if it's already used and the expiry date
	############################################	
	voucher_user = Voucher_user.objects.filter(voucher = voucher, effective_from__lte = today, 
			effective_to__gte = today).first()	
	if not voucher.all_applicability:
		if not voucher_user :
			return JsonResponse({"status":"INVALID-CODE"})
		if voucher_user.used_date != None :
			return JsonResponse({"status":"USED"})		
		if voucher_user.user != user:
			return JsonResponse({"status":"USER-MISMATCH"})
		if voucher.effective_to < today:
			return JsonResponse({"status":"EXPIRED"})
	#############################################
	## END: Check if voucher applies to the user, 
	## if it's already used and the expiry date
	############################################	


	#############################################
	## Variables 
	############################################	
	disc_type = voucher.discount_type
	disc_amount = 0
	cart_sub_total = 0
	cart_tax = 0
	new_cart_total = 0
	new_cart_sub_total = 0
	voucher_bal_amount = 0
	avl_disc_amount = 0
	total_disc_amount = 0
	#############################################
	## END: Variables 
	############################################	
	
	

	#############################################
	## Voucher transaction
	############################################	
	## All applicable voucher is allowed only with disc type as PERCENTAGE
	if voucher.all_applicability:
		# Check it it's alrady used
		#if cart.voucher_disc_amount > 0 :
		#	return JsonResponse({"status":"USED"})

		## Check one time use
		if voucher_use_check:
			used_voucher = Voucher_used.objects.filter( voucher = voucher,
				user = user)
			if used_voucher:
				return JsonResponse({"status":"USED"})
			
		## For all "applicable vouchers" only allowed disc type is %
		if disc_type == "PERCENTAGE":
			##if there is any voucher already in cart, remove the amount
			if cart.voucher_disc_amount > 0:
				cart_sub_total = round(cart.cart_sub_total + cart.voucher_disc_amount, 2)
			else:
				cart_sub_total = cart.cart_sub_total
			## Calculate discount amount and new cart total
			disc_amount = round(cart_sub_total * voucher.discount_value/100, 2)
			new_cart_sub_total = round(cart_sub_total - ( cart_sub_total * voucher.discount_value/100 ), 2)
			total_disc_amount =  disc_amount
			voucher_bal_amount =  0
		elif disc_type == "CASH":
			None
			######new_cart_sub_total = cart.cart_sub_total 
			######total_disc_amount =  disc_amount + applied_disc
		if new_cart_sub_total < 0:
			# Limit the discount to the total cart value
			new_cart_sub_total = 0
		
	else:
		return JsonResponse({"status":"DOESNOT-APPLY"})

	taxes = get_taxes()
	####################################################
	### How to apply tax if a cart contains different 
	### product types such as STOCK IMAGE and USER IMAGE,
	### both have different tax rates
	####################################################						
	tax_rate = taxes['stock_image_tax_rate']

	# Reclaculate tax & sub total after applying discount
	#cart_sub_total = round( new_cart_total / (1 + (tax_rate/100)), 2 )
	#cart_tax = new_cart_total - cart_sub_total
	cart_tax =  round((new_cart_sub_total * tax_rate)/100 ,2)
	new_cart_total = round(new_cart_sub_total + cart_tax)

	#############################################
	## END:
	############################################	
	return JsonResponse({"status":status, 'disc_amount': total_disc_amount, 
				'cart_total':new_cart_total, 'disc_type':disc_type, 
				'voucher_bal_amount': voucher_bal_amount})
	
@csrf_exempt
@is_manager
def apply_coupon_code(request):
	cart_id = request.POST.get('cart_id', '')
	voucher_code = request.POST.get('voucher_code', '')
	voucher_use_check = request.POST.get('voucher_use_check', 'FALSE')
	today = datetime.date.today()
	status = 'SUCCESS'
	try :
		cart = Cart.objects.get(cart_id = cart_id)
	except Cart.DoesNotExist:
		cart = None
		status = "Cart Id: " + cart_id + " not found"
		return JsonResponse({"status":status})

	if voucher_code == '':
		return JsonResponse({"status":"Coupon Code not found"})

	voucher = Voucher.objects.filter(voucher_code = voucher_code, effective_from__lte = today, 
			effective_to__gte = today, store_id = settings.STORE_ID).first()
			
	if not voucher :
		return JsonResponse({"status":"Coupon Code is invalid"})
		
	if cart:
		if not cart.user:
			status = "User for cart id " + str(cart.cart_id) + " not found"
			return JsonResponse({"status":status})

		from django.http import HttpRequest
		request = HttpRequest()
		request.user = cart.user.username
		
		if not request.user:
			status = "User for cart id " + str(cart.cart_id) + " not found"
			return JsonResponse({"status":status})

	res = remove_voucher(request, cart.cart_id)
	rep = json.loads(res.content.decode('utf-8'))
	if rep['status'] == 'FAILURE':
		status = "Error occured while removing existing voucher"
		return JsonResponse({"status":status})
		
	## Apply selected voucher
	vou = apply_voucher_py_new(request, cart.cart_id, voucher_code, 0, 0, False)
	rep_v = json.loads(vou.content.decode('utf-8'))
	if rep_v['status'] == 'FAILURE':
		status = "Error occured while applying this voucher"

	return JsonResponse({"status":status})
	
	

def emails_for_delay():
	today = datetime.date.today()
	dt = today - timedelta(days=4)
	orders = Order.objects.filter( 
				Q( order_date__lte = dt, order_status = 'PC') | 
				Q(order_date__lte = dt, order_status = 'PR')
			) 
				
	if env == 'PROD':
		file_nm = '/home/artevenue/website/email_list_for_delay.csv'
	else:
		file_nm = 'c:/artevenue/estore/email_list_for_delay.csv'
	
	with open(file_nm, 'w', newline='') as file :
		wr = csv.writer(file, quoting=csv.QUOTE_ALL)		
		row =['email', 'full name', 'order number', 'order_date']
		wr.writerow(row)
		for i in orders:
			row =[i.order_billing.email_id, i.order_billing.full_name, i.order_number, i.order_date]
			wr.writerow(row)
	
@staff_member_required
@has_accounts_access
def invoice_report(request):
	return render(request, 'artevenue/invoice_report.html')		

@csrf_exempt
@has_accounts_access
def get_invoice_report(request):
	startDt = ''
	endDt = ''	
	page = request.POST.get('page', 1)
	printpdf = request.POST.get('printpdf', 'NO')
	
	from_date = request.POST.get("fromdate", '')
	if from_date != '' :
		startDt = datetime.datetime.strptime(from_date, "%Y-%m-%d")	
		
	to_date = request.POST.get("todate", '')
	if to_date != '' :
		endDt = datetime.datetime.strptime(to_date, "%Y-%m-%d")

	order_list = Order.objects.exclude(order_status = 'CN').order_by('invoice_date')
	
	order_items_list = {}
	if startDt:
		order_list = order_list.filter(invoice_date__date__gte = startDt)
	if endDt:
		order_list = order_list.filter(invoice_date__date__lte = endDt)

	## Totals
	totals = order_list.aggregate(Sum('unit_price'), Sum('quantity'), Sum('order_discount_amt'), 
		Sum('shipping_cost'), Sum('sub_total'), Sum('tax'), Sum('order_total'), Avg('order_total'))

	igst = order_list.exclude(order_billing__state__state_name__iexact=ecom_site.store_state).aggregate(igst=Sum('tax'))
	if igst:
		if igst['igst']:
			total_igst = igst['igst']
		else:
			total_igst = 0.0
	else:
		total_igst = 0.0

	cgst = order_list.filter(order_billing__state__state_name__iexact=ecom_site.store_state).aggregate(cgst=Sum('tax'))
	if cgst :
		if cgst['cgst']:
			total_cgst = cgst['cgst'] / 2
		else:
			total_cgst = 0.0
	else:
		total_cgst = 0.0
		
	total_sgst = total_cgst
	
	if printpdf == "YES":
		html_string = render_to_string('artevenue/order_summary_print.html', {
			'orders': order_list, 'totals':totals, 'startDt':startDt, 'endDt':endDt,
			'ecom_site':ecom_site, 'total_cgst':total_cgst, 'total_sgst':total_sgst,
			'total_igst':total_igst})

		html = HTML(string=html_string, base_url=request.build_absolute_uri('/'))
		
		html.write_pdf(target= settings.TMP_FILES + str(request.user) + '_ord_pdf.pdf',
			stylesheets=[
						CSS(settings.CSS_FILES +  'style.default.css'), 
						CSS(settings.CSS_FILES +  'custom.css'),
						CSS(settings.VENDOR_FILES + 'bootstrap/css/bootstrap.min.css') 
						],
						presentational_hints=True);
		
		fs = FileSystemStorage(settings.TMP_FILES)
		with fs.open(str(request.user) + '_ord_sum_pdf.pdf') as pdf:
			response = HttpResponse(pdf, content_type='application/pdf')
			response['Content-Disposition'] = 'attachment; filename="' + str(request.user) + '_ord_pdf.pdf"'
			return response

		return response		
	else:
		return render(request, 'artevenue/invoice_report_table.html', { 
			'orders': order_list, 'totals':totals, 'startDt':startDt, 'endDt':endDt,
			'ecom_site':ecom_site, 'total_cgst':total_cgst, 'total_sgst':total_sgst,
			'total_igst':total_igst})

@csrf_exempt
@is_manager	
def create_set_single(request):
	return render(request, "artevenue/create_set_single.html", {})

@csrf_exempt
@is_manager	
def set_single_data(request):
	set_of = request.GET.get("set_of", '')
	
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
	
	return render(request, "artevenue/set_single_data.html", {'set_of':set_of, 'set_range': range(int(set_of)), 
		'printmedium':printmedium, 'mouldings': mouldings, 'mounts':mounts, 
		'acrylics':acrylics, 'boards':boards,'stretches':stretches, 'env':settings.EXEC_ENV})


@csrf_exempt
@is_manager	
def get_product(request):
	product_id = int(request.GET.get('prod_id', '0'))
	msg =''
	if product_id is None or product_id == 0:
		msg = "No product ID supplied"
		return( JsonResponse({'msg': msg}) )
		
	product = Stock_image.objects.filter(product_id = product_id, is_published=True).first()
	product_category = Stock_image_stock_image_category.objects.filter(stock_image = product).first()
	
	aspect_ratio = 0
	product_name = ''
	product_category_id = 0
	category_name = ''
	if product:
		aspect_ratio = product.aspect_ratio
		product_name = product.name
	if product_category:
		product_category_id = product_category.stock_image_category.category_id
		category_name = product_category.stock_image_category.name
		
	if not product:
		msg = 'Product not found'
	if not product_category:
		msg = 'Product category not found'
		
	return( JsonResponse({'msg': msg, 'product_name':product_name, 
		'aspect_ratio': product.aspect_ratio, 'product_category_id': product_category_id,
		'category_name': category_name, 'env':settings.EXEC_ENV}, safe=False) )


@csrf_exempt
@is_manager	
def save_new_set_single(request):
	err_cd = '00'
	msg = ''
	
	set_of = int(request.POST.get('set_of', '0'))
	prod_name = request.POST.get('name', '')

	prod_arr = request.POST.get('prod_arr', '').split(',')
	image_width = request.POST.get('image_width', )
	image_height = request.POST.get('image_height', )
	category_id_str = request.POST.get('category_id_str', '').split(',')
	print_medium = request.POST.get('print_surface', '')
	moulding_id = request.POST.get('moulding_id', '')
	mount_color = request.POST.get('mount_color', '')
	mnt_size = request.POST.get('mount_size', '0')
	stretch_id = request.POST.get('stretch_id', '')
	aspect_ratio =  Decimal(request.POST.get('aspect_ratio', '0'))
	duplicate_image = request.POST.get('duplicate_image', 'NO')
	
	if moulding_id == '' or moulding_id == '0' or moulding_id == 'NA':
		moulding_id = None

	if mnt_size == '':
		mount_size = 0
	else:
		mount_size = int(mnt_size)

	max_width = 0
	for p in prod_arr:
		if p:
			prd = Collage_stock_image.objects.filter(stock_image_id = int(p), 
				stock_collage__is_published = True).first()
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
					
	mount_id = None
	if mount_color != '':
		mount = Mount.objects.filter(color = mount_color ).first()
		mount_id = mount.mount_id

	if print_medium == 'PAPER':
		board_id = 1
		acrylic_id = 1
		stretch_id = None
	elif print_medium == 'CANVAS':
		stretch_id = 1
		board_id = None
		acrylic_id = None

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
	display_url = 'img/creatives/' + file_nm
	display_thumbnail_url = 'img/creatives/' + file_nm_thumb
	price = 0
	
	for i in category_id_str:
		category_id = i

	prod_type = 'STOCK-IMAGE'
	if set_of > 1:
		prod_type = 'STOCK-COLLAGE'
	else:
		prod_type = 'STOCK-IMAGE'
	
	try:
		stk = Stock_collage(
			product_type_id = prod_type,
			name = prod_name,
			is_published = True,
			category_disp_priority = None,
			set_of = set_of,
			stock_image_category_id = category_id,
			max_width = max_width,
			max_height = round(max_width / aspect_ratio),
			min_width = 8,
			aspect_ratio = aspect_ratio,
			orientation = orientation,
			colors = colors,
			key_words = keywords,
			url = url,
			thumbnail_url = thumbnail_url,
			price = price
		)
		stk.save()

		for p in prod_arr:
			prods = Collage_stock_image(
				stock_collage = stk,
				stock_image_id = p
			)
			prods.save()
		
		specs = Stock_collage_specs(
			stock_collage = stk,
			moulding_id = moulding_id,
			moulding_size = None,
			print_medium_id = print_medium,
			mount_id = mount_id,
			mount_size = mount_size,
			board_id = board_id,
			acrylic_id = acrylic_id,
			stretch_id = stretch_id,
			image_width = image_width,
			image_height = image_height,
			display_url = display_url,
			display_thumbnail_url = display_thumbnail_url
			)
		specs.save()
	
	except Error as e:
		err_cd = "99"
		msg = "System error has occured while saving data. Can't proceed."
		
	return( JsonResponse({'err_cd':err_cd, 'msg': msg }, safe=False) )
	