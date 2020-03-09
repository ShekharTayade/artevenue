from django.shortcuts import render, get_object_or_404
from django.http import HttpResponse
from django.conf import settings
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_protect, csrf_exempt
from django.db import IntegrityError, DatabaseError, Error
from django.contrib.auth.models import User
from django.db.models import F
from django.db.models import Count, Q, Max, Sum
from decimal import Decimal

from datetime import datetime
import datetime
from decimal import Decimal
import json

from ipaddr import client_ip

from artevenue.models import Cart, Stock_image, User_image, Stock_collage, Original_art, Cart_item
from artevenue.models import Product_view, Promotion, Order, Voucher, Voucher_user, Cart_item_view
from artevenue.models import Cart_user_image, Cart_stock_image, Cart_stock_collage, Cart_original_art
from artevenue.models import Order_stock_image, Order_stock_collage, Order_original_art, Order_user_image
from artevenue.models import Referral, Egift_redemption, Egift, Order_items_view, Voucher_used
from artevenue.models import Order_shipping, Order_billing
from .product_views import *
from .user_image_views import *
from .tax_views import *
from .price_views import *

today = datetime.date.today()
ecom = get_object_or_404 (Ecom_site, store_id=settings.STORE_ID )


@csrf_exempt
def show_cart(request):

	## First of all validate the promotions. Revert promotion discounts
	## if the promotion has expired while item is in the cart.
	result = validatePromotions(request)
	if result:
		promo_removed = 'Y'
	else :
		promo_removed = 'N'
	
	usercart = {}
	usercartitems = {}
	shipping_cost = 0 

	''' Let's check if the user has a cart open '''
	try:
		if request.user.is_authenticated:
			usr = User.objects.get(username = request.user)
			usercart = Cart.objects.get(user = usr, cart_status = "AC")
		else:
			sessionid = request.session.session_key		
			if sessionid is None:
				request.session.create()
				sessionid = request.session.session_key
				
			usercart = Cart.objects.get(session_id = sessionid, cart_status = "AC")

		# If any order exists against this cart
		order = Order.objects.filter(cart_id = usercart.cart_id).first()
		if order:
			shipping_cost = order.shipping_cost
		
		
		usercartitems = Cart_item_view.objects.select_related('product', 'promotion').filter(
				cart = usercart.cart_id, product__product_type_id = F('product_type_id')).values(
			'cart_item_id', 'product_id', 'product__publisher','quantity', 'item_total', 'moulding_id',
			'moulding__name', 'moulding__width_inches', 'print_medium_id', 'mount_id', 'mount__name',
			'acrylic_id', 'mount_size', 'product__name', 'image_width', 'image_height', 'stretch_id', 'board_id',
			'product__thumbnail_url', 'cart_id', 'promotion__discount_value', 'promotion__discount_type', 'mount__color',
			'item_unit_price', 'item_sub_total', 'item_disc_amt', 'item_tax', 'item_total', 'product_type',
			'product__image_to_frame', 'promotion_id', 'moulding__width_inner_inches', 'product__description'
			).order_by('product_type')

	except Cart.DoesNotExist:
			usercart = {}

	if request.is_ajax():
		template = "artevenue/cart_include.html"
	else :
		template = "artevenue/cart.html"
	
	total_bare = 0
	cart_total = 0
	ref_status = '' 
	ref_msg = ''
	referral_disc_amount = 0
	try:
		if usercart :
			total_bare = usercart.cart_total - shipping_cost + usercart.cart_disc_amt
			cart_total = usercart.cart_total
			referral_disc_amount = usercart.referral_disc_amount			
			## Check for an applicable referral
			if request.user.is_authenticated:
				ref = apply_referral(request, cart_total + usercart.cart_disc_amt)
				if ref:
					if ref['status'] == "SUCCESS":
						ref_status = ref['status']
						ref_msg = ref['msg']
						referral_id = ref['referral_id']
						referral_disc_amount = ref['disc_amt']
						# Apply applicable referral, if not already applied.
						if not usercart.referral_id :
							cart_total = ref['cart_total']
							cart_disc_amt = usercart.cart_disc_amt - usercart.referral_disc_amount + referral_disc_amount

							# TAX Calculations
							item_tax = 0
							item_sub_total = 0
							taxes = get_taxes()
							####################################################
							### How to apply tax if a cart contains different 
							### product types such as STOCK IMAGE and USER IMAGE,
							### both have different tax rates
							####################################################						
							tax_rate = taxes['stock_image_tax_rate']

							# Reclaculate tax & sub total after applying referral discount
							cart_sub_total = round( cart_total / (1 + (tax_rate/100)), 2 )
							cart_tax = cart_total - cart_sub_total
							try:
								row = Cart.objects.filter(cart_id=usercart.cart_id).update(
									cart_total=cart_total, referral_id = referral_id,
									cart_sub_total = cart_sub_total, cart_tax = cart_tax,
									referral_disc_amount = referral_disc_amount,
									cart_disc_amt = cart_disc_amt)
							except Error as e:
								print(e)
								print(type(e))
								
							# Update the changed values	of usercart for display
							usercart.referral_id = referral_id
							usercart.cart_tax = cart_tax
							usercart.cart_sub_total = cart_sub_total
							usercart.cart_total = cart_total
							usercart.referral_disc_amount = referral_disc_amount
							usercart.cart_disc_amt = cart_disc_amt
							
			cart_total = usercart.cart_total
	except Error as e:
		print(e.message)


	## To disply the total after applying promotion discounts, but before 
	## voucher and referral discount
	cart_without_disc = 0
	if usercart:
		if cart_total:
			cart_without_disc = cart_total		
		if usercart.referral_disc_amount:
			cart_without_disc = cart_total + usercart.referral_disc_amount 
		if usercart.voucher_disc_amount:
			cart_without_disc = cart_without_disc + usercart.voucher_disc_amount

	return render(request, template, {'usercart':usercart, 
		'usercartitems': usercartitems, 'shipping_cost':shipping_cost, 
		'total_bare':total_bare, 'cart_total':cart_total, 
		'ref_msg':ref_msg, 'ref_status':ref_status, 'referral_disc_amount':referral_disc_amount,
		'MEDIA_ROOT':settings.MEDIA_ROOT, 'MEDIA_URL':settings.MEDIA_URL, 
		'cart_without_disc':cart_without_disc, 'promo_removed':promo_removed})
	
def show_wishlist(request):

	if request.is_ajax():

		template = "artevenue/cart_include.html"
	else :
		template = "artevenue/show_wishlist.html"
	
	return render(request, template, {})

	

@csrf_protect
@csrf_exempt	
def add_to_cart(request):
	err_flg = False
	prod_id = request.POST.get('prod_id', '')
	prod_type = request.POST.get('prod_type', '')
	qty = int(request.POST.get('qty', '0'))
	cart_item_flag = request.POST.get('cart_item_flag', 'FALSE')
	
	image_width = Decimal(request.POST.get('image_width', '0'))
	image_height = Decimal(request.POST.get('image_height', '0'))
	
	sqin = image_width * image_height
	rnin = (image_width + image_height) * 2
	
	moulding_id = request.POST.get('moulding_id', '')
	if moulding_id == '0' or moulding_id == 'None' or moulding_id == '' :
		moulding_id = None

	if moulding_id:
		moulding_size = rnin
	else: 
		moulding_size = None
	print_medium_id = request.POST.get('print_medium_id', '')
	print_medium_size = Decimal(request.POST.get('print_medium_size', '0'))
	mount_id = request.POST.get('mount_id', '0')
	if mount_id == '0' or mount_id == 'None' or mount_id == '':
		mount_id = None
	if mount_id:
		mount_size = Decimal(request.POST.get('mount_size', '0'))
		mount_w_left = Decimal(request.POST.get('mount_w_left', '0'))
		mount_w_right = Decimal(request.POST.get('mount_w_right', '0'))
		mount_w_left = Decimal(request.POST.get('mount_w_top', '0'))
		mount_w_left = Decimal(request.POST.get('mount_w_bottom', '0'))
	else:
		mount_size = None
		mount_w_left = None
		mount_w_right = None
		mount_w_top = None
		mount_w_bottom = None
	acrylic_id = request.POST.get('acrylic_id', '0')
	if acrylic_id == '0' or acrylic_id == 'None' or acrylic_id == '':
		acrylic_id = None
	if acrylic_id:
		acrylic_size = sqin
	else:
		acrylic_size = None
	
	board_id = request.POST.get('board_id', '0')
	if board_id == '0' or board_id == 'None' or board_id == '':
		board_id = None
	if board_id:
		board_size = sqin
	else:
		board_size = None

	stretch_id = request.POST.get('stretch_id', '0')
	if stretch_id == '0' or stretch_id == 'None'  or stretch_id == '':
		stretch_id = None
	if stretch_id:
		stretch_size = rnin
	else:
		stretch_size = None
	
	str_item_unit_price = request.POST.get('item_unit_price', '0')
	if str_item_unit_price == '':
		str_item_unit_price = '0'
	item_unit_price = Decimal(str_item_unit_price)
	
	str_total_price = request.POST.get('total_price', '0')
	if str_total_price == '':
		str_total_price = 0
	total_price = Decimal(str_total_price)
	
	str_disc_amt = request.POST.get('disc_amt', '0')
	if str_disc_amt == '':
		str_disc_amt = 0
	disc_amt = Decimal(str_disc_amt)

	userid = None

	discount = request.POST.get('discount', '')

	promo_str = request.POST.get('promotion_id', '0')

	if promo_str == '':
		promo_str = '0'
	promo_id = int(promo_str)
	
	#####################################
	#         Get the item price
	#####################################
	price = get_prod_price(prod_id, 
			prod_type=prod_type,
			image_width=image_width, image_height=image_height,
			print_medium_id = print_medium_id,
			acrylic_id = acrylic_id,
			moulding_id = moulding_id,
			mount_size = mount_size,
			mount_id = mount_id,
			board_id = board_id,
			stretch_id = stretch_id)
	total_price = price['item_price']
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
	if item_unit_price == 0 or item_unit_price is None:
		err_flg = True
		return( JsonResponse({'msg':'Price not avaiable for this image', 'cart_qty':qty}, safe=False) )
		
	# Get the product
	prod = None	
	try:
		if prod_id != '':
			prod = Product_view.objects.get(product_id=prod_id, product_type = prod_type, is_published = True)
		
		if prod.product_type == "USER-IMAGE" or prod.product_type == "STOCK-COLLAGE":
			if request.user.is_authenticated:
				user = User.objects.get(username = request.user)
				user_image = User_image.objects.filter(user = user, status = "INI").first()
			else:
				session_id = request.session.session_key
				user_image = User_image.objects.filter(session_id = session_id, status = "INI").first()		
		
	except Product_view.DoesNotExist:
		msg = "Product " + prod_id + " does not exist"
		err_flg = True
		return( JsonResponse({'msg':msg, 'cart_qty':qty}, safe=False) )
	except User_image.DoesNotExist:
		err_flg = True
		msg = "Couldn't find the uploaded image. Pease try again."
		return( JsonResponse({'msg':msg, 'cart_qty':qty}, safe=False) )

	# TAX Calculations
	item_tax = 0
	item_sub_total = 0
	taxes = get_taxes()

	if prod.product_type_id == 'STOCK-IMAGE':
		tax_rate = taxes['stock_image_tax_rate']
	if prod.product_type_id == 'ORIGINAL-ART':
		tax_rate = taxes['original_art_tax_rate']
	if prod.product_type_id == 'USER-IMAGE':
		tax_rate = taxes['user_image_tax_rate']
	if prod.product_type_id == 'STOCK-COLLAGE':
		tax_rate = taxes['stock_image_tax_rate']
	if prod.product_type_id == 'FRAME':
		tax_rate = taxes['frame_tax_rate']
	
		
	# Calculate tax and sub_total
	item_sub_total = round( total_price / (1 + (tax_rate/100)), 2 )
	item_tax = total_price - item_sub_total
	#############################################################

	promo = {}
	promo['cash_disc']= 0
	promo['percent_disc'] = 0
	# Get any discount on the product
	if prod:
		promo = get_product_promotion(prod_id)

	cash_disc = promo['cash_disc']
	percent_disc = promo['percent_disc']
	
	promotion = {}
	if promo :
		if prod:
			promotion = Promotion.objects.filter(promotion_id = promo_id).first()
	
	
	#################################################################################
	##	total_price contains the price after promotion discounts. The promotion
	##  details obtained above are only for the purpose of saving it into the tables 
	#################################################################################
		
	msg = "Success"
	cart_exists = False
	usercart = {}
	cart_qty = 0
	''' Let's check if the user has a cart open '''
	
	sessionid = request.session.session_key
	if request.user.is_authenticated:
		try:
			userid = User.objects.get(username = request.user)
			usercart = Cart.objects.get(user_id = userid, cart_status = "AC") 
			#cart.objects.filter(user_id = userid)[:1]
		except Cart.DoesNotExist:
			usercart = {}
			cart_exists = False
			
		if usercart:
			cart_exists = True
		else:
			cart_exists = False
	else:
		if sessionid is None:
			request.session.create()
			sessionid = request.session.session_key
			cart_exists = False
		 
		else:
			try:
				# Get usercart by session
				usercart = Cart.objects.get(session_id = sessionid, cart_status="AC")
				#cart.objects.filter(session_id = sessionid)[:1]
			except Cart.DoesNotExist:
				usercart = {}
				cart_exists = False
			
			if usercart:
				cart_exists = True
			else:
				cart_exists = False;

	prod_exits_in_cart = False 
	if cart_exists:

		''' Check if product or user image exists in cart '''
		cart_prods = {}
		if prod:
			## if this is from a cart then we only check if product id
			## exists in the cart, as other factors can be changed by user
			if cart_item_flag == 'TRUE':
				cart_prods = Cart_item_view.objects.filter(cart_id = usercart.cart_id, 
							product_id = prod_id).first()			
			else:
				cart_prods = Cart_item_view.objects.filter(cart_id = usercart.cart_id, 
							product_id = prod_id, moulding_id = moulding_id,
							print_medium_id = print_medium_id, mount_id = mount_id,
							mount_size = mount_size, acrylic_id = acrylic_id,
							board_id = board_id, stretch_id = stretch_id ).first()

		if cart_prods:
			prod_exits_in_cart = True
	
		try :
			if cart_item_flag == 'TRUE' :
				cart_total = Decimal(usercart.cart_total) - (cart_prods.item_total) + (total_price)
			else:
				cart_total = Decimal(usercart.cart_total) + (total_price)
			voucher_disc_amount = usercart.voucher_disc_amount
			# Calculate voucher discount
			if usercart.voucher_id:
				voucher = Voucher.objects.filter(voucher_id = usercart.voucher_id).first()
				if voucher.voucher_code:
					res = apply_voucher_py(request, usercart.cart_id, voucher.voucher_code, cart_total)
					vou = json.loads(res.content)		
					if 'status' in vou:
						status = vou['status']
					else:
						status = ''
					if status == 'SUCCESS' or status == 'SUCCESS-':
						if 'disc_amount' in vou:
							voucher_disc_amount = usercart.voucher_disc_amount + vou['disc_amount'] 
						else:
							voucher_disc_amount = usercart.voucher_disc_amount
						
						if 'cart_total' in vou:
							cart_total = Decimal(vou['cart_total'])
						
			#Update the existing cart
			# Reclaculate tax & sub total after applying voucher
			cart_sub_total = round( cart_total / (1 + (tax_rate/100)), 2 )
			cart_tax = cart_total - cart_sub_total
			
			# Update cart
			if cart_item_flag == 'TRUE':
				usercart.quantity =  usercart.quantity - (cart_prods.quantity) + qty
			else:
				usercart.quantity =  usercart.quantity + qty

			#### Add voucher discount amounts
			usercart.voucher_disc_amount = Decimal(voucher_disc_amount)
			usercart.cart_disc_amt = usercart.cart_disc_amt + disc_amt
			#usercart.cart_sub_total = usercart.cart_sub_total + item_sub_total
			usercart.cart_unit_price = cart_sub_total
			usercart.cart_sub_total = cart_sub_total
			#usercart.cart_tax  = usercart.cart_tax + item_tax
			usercart.cart_tax  = cart_tax
			usercart.cart_total = cart_total
			usercart.save()
			
			''' If the product with same moulding, print_medium etc. already exists in the cart items, then update it, else insert new item '''
			if prod_exits_in_cart:
				## If it has come from the cart then just update the current item for same qty
				## Else update quantity and amount for current item
				if cart_item_flag == 'FALSE':
					iqty = cart_prods.quantity + qty
					s_total = cart_prods.item_sub_total + item_sub_total
					total = cart_prods.item_total + total_price
					unit = cart_prods.item_unit_price
					d_amt = cart_prods.item_disc_amt + disc_amt
					tax_amt = cart_prods.item_tax + item_tax
				else:
					iqty = qty
					s_total = item_sub_total
					total = total_price
					unit = item_unit_price
					d_amt = disc_amt
					tax_amt = item_tax
				
				if prod.product_type_id == 'STOCK-IMAGE':
					usercartitems = Cart_stock_image(
						cart_item_id = cart_prods.cart_item_id,
						cart = usercart,
						promotion = cart_prods.promotion,
						quantity = iqty,
						item_unit_price = unit,
						item_sub_total = s_total,
						item_disc_amt = d_amt,
						item_tax  = tax_amt,
						item_total = total,
						moulding_id = moulding_id,
						moulding_size =  mount_size,
						print_medium_id = print_medium_id,
						print_medium_size = print_medium_size,
						mount_id = mount_id,
						mount_size = mount_size,
						board_id =  board_id,
						board_size = board_size,
						acrylic_id = acrylic_id,
						acrylic_size = acrylic_size,
						stretch_id = stretch_id,
						stretch_size = stretch_size,
						image_width = image_width,
						image_height = image_height,
						created_date = cart_prods.created_date,
						updated_date =  today,
						stock_image_id = prod.product_id
						
					)
				elif prod.product_type_id == 'USER-IMAGE':
					usercartitems = Cart_user_image(
						cart_item_id = cart_prods.cart_item_id,
						cart = usercart,
						promotion = cart_prods.promotion,
						quantity = iqty,
						item_unit_price = unit,
						item_sub_total = s_total,
						item_disc_amt = d_amt,
						item_tax  = tax_amt,
						item_total = total,
						moulding_id = moulding_id,
						moulding_size =  mount_size,
						print_medium_id = print_medium_id,
						print_medium_size = print_medium_size,
						mount_id = mount_id,
						mount_size = mount_size,
						board_id =  board_id,
						board_size = board_size,
						acrylic_id = acrylic_id,
						acrylic_size = acrylic_size,
						stretch_id = stretch_id,
						stretch_size = stretch_size,
						image_width = image_width,
						image_height = image_height,
						created_date = cart_prods.created_date,
						updated_date =  today,
						user_image_id = prod.product_id
						
					)
				elif prod.product_type_id == 'STOCK-COLLAGE':
					usercartitems = Cart_stock_collage(
						cart_item_id = cart_prods.cart_item_id,
						cart = usercart,
						promotion = cart_prods.promotion,
						quantity = iqty,
						item_unit_price = unit,
						item_sub_total = s_total,
						item_disc_amt = d_amt,
						item_tax  = tax_amt,
						item_total = total,
						moulding_id = moulding_id,
						moulding_size =  mount_size,
						print_medium_id = print_medium_id,
						print_medium_size = print_medium_size,
						mount_id = mount_id,
						mount_size = mount_size,
						board_id =  board_id,
						board_size = board_size,
						acrylic_id = acrylic_id,
						acrylic_size = acrylic_size,
						stretch_id = stretch_id,
						stretch_size = stretch_size,
						image_width = image_width,
						image_height = image_height,
						created_date = cart_prods.created_date,
						updated_date =  today,
						stock_collage_id = prod.product_id
					)
				elif prod.product_type_id == 'ORIGINAL-ART':
					usercartitems = Cart_original_art(
						cart_item_id = cart_prods.cart_item_id,
						cart = usercart,
						promotion = cart_prods.promotion,
						quantity = iqty,
						item_unit_price = unit,
						item_sub_total = s_total,
						item_disc_amt = d_amt,
						item_tax  = tax_amt,
						item_total = total,
						moulding_id = moulding_id,
						moulding_size =  mount_size,
						print_medium_id = print_medium_id,
						print_medium_size = print_medium_size,
						mount_id = mount_id,
						mount_size = mount_size,
						board_id =  board_id,
						board_size = board_size,
						acrylic_id = acrylic_id,
						acrylic_size = acrylic_size,
						stretch_id = stretch_id,
						stretch_size = stretch_size,
						image_width = image_width,
						image_height = image_height,
						created_date = cart_prods.created_date,
						updated_date =  today,
						original_art_id = prod.product_id
						
					)				
				usercartitems.save()
				
			else:
				# add new product in the cart
				if prod:
					if prod.product_type_id == 'STOCK-IMAGE' :
						usercartitems = Cart_stock_image(
							cart = usercart,
							promotion = promotion,
							quantity = qty,
							item_unit_price = item_unit_price,
							item_sub_total = item_sub_total,
							item_disc_amt = disc_amt,
							item_tax  = item_tax,
							item_total = total_price,
							moulding_id = moulding_id,
							moulding_size =  mount_size,
							print_medium_id = print_medium_id,
							print_medium_size = print_medium_size,
							mount_id = mount_id,
							mount_size = mount_size,
							board_id =  board_id,
							board_size = board_size,
							acrylic_id = acrylic_id,
							acrylic_size = acrylic_size,
							stretch_id = stretch_id,
							stretch_size = stretch_size,
							image_width = image_width,
							image_height = image_height,
							created_date = today,
							updated_date =  today,
							stock_image_id = prod.product_id
						)
					elif prod.product_type_id == 'USER-IMAGE':
						usercartitems = Cart_user_image(
							cart = usercart,
							promotion = promotion,
							quantity = qty,
							item_unit_price = item_unit_price,
							item_sub_total = item_sub_total,
							item_disc_amt = disc_amt,
							item_tax  = item_tax,
							item_total = total_price,
							moulding_id = moulding_id,
							moulding_size =  mount_size,
							print_medium_id = print_medium_id,
							print_medium_size = print_medium_size,
							mount_id = mount_id,
							mount_size = mount_size,
							board_id =  board_id,
							board_size = board_size,
							acrylic_id = acrylic_id,
							acrylic_size = acrylic_size,
							stretch_id = stretch_id,
							stretch_size = stretch_size,
							image_width = image_width,
							image_height = image_height,
							created_date = today,
							updated_date =  today,
							user_image_id = prod.product_id
						)
					elif prod.product_type_id == 'STOCK-COLLAGE':
						usercartitems = Cart_stock_collage(
							cart = usercart,
							promotion = promotion,
							quantity = qty,
							item_unit_price = item_unit_price,
							item_sub_total = item_sub_total,
							item_disc_amt = disc_amt,
							item_tax  = item_tax,
							item_total = total_price,
							moulding_id = moulding_id,
							moulding_size =  mount_size,
							print_medium_id = print_medium_id,
							print_medium_size = print_medium_size,
							mount_id = mount_id,
							mount_size = mount_size,
							board_id =  board_id,
							board_size = board_size,
							acrylic_id = acrylic_id,
							acrylic_size = acrylic_size,
							stretch_id = stretch_id,
							stretch_size = stretch_size,
							image_width = image_width,
							image_height = image_height,
							created_date = today,
							updated_date =  today,
							stock_collage_id = prod.product_id
						)
					elif prod.product_type_id == 'ORIGINAL-ART':
						usercartitems = Cart_original_art(
							cart = usercart,
							promotion = promotion,
							quantity = qty,
							item_unit_price = item_unit_price,
							item_sub_total = item_sub_total,
							item_disc_amt = disc_amt,
							item_tax  = item_tax,
							item_total = total_price,
							moulding_id = moulding_id,
							moulding_size =  mount_size,
							print_medium_id = print_medium_id,
							print_medium_size = print_medium_size,
							mount_id = mount_id,
							mount_size = mount_size,
							board_id =  board_id,
							board_size = board_size,
							acrylic_id = acrylic_id,
							acrylic_size = acrylic_size,
							stretch_id = stretch_id,
							stretch_size = stretch_size,
							image_width = image_width,
							image_height = image_height,
							created_date = today,
							updated_date =  today,
							original_art_id = prod.product_id
						)
					
					usercartitems.save()
				
			cart_qty = usercart.quantity + qty
				
		except IntegrityError as e:
			err_flg = True
			msg = 'Apologies!! Could not save your cart. Please use the "Contact Us" link at the bottom of this page and let us know. We will be glad to help you.'

		except Error as e:
			err_flg = True
			msg = 'Apologies!! Could not save your cart. Please use the "Contact Us" link at the bottom of this page and let us know. We will be glad to help you.'
	
	# Create a new cart
	else:
	
		try :

			newusercart = Cart(
				store = ecom,
				session_id = sessionid,
				user = userid,
				voucher_id = None,
				voucher_disc_amount = 0,
				referral = None,
				referral_disc_amount = 0,
				quantity =  qty,
				cart_unit_price = unit,
				cart_sub_total = item_sub_total,
				cart_disc_amt = disc_amt,
				cart_tax  = item_tax,
				cart_total = total_price,
				cart_status = 'AC',
				created_date = today,
				updated_date = today
			)
			newusercart.save()
			
			if prod :
				if prod.product_type_id == 'STOCK-IMAGE' :
					usercartitems = Cart_stock_image(
						cart = newusercart,
						promotion = promotion,
						quantity = qty,
						item_unit_price = item_unit_price,
						item_sub_total = item_sub_total,
						item_disc_amt = disc_amt,
						item_tax  = item_tax,
						item_total = total_price,
						moulding_id = moulding_id,
						moulding_size =  mount_size,
						print_medium_id = print_medium_id,
						print_medium_size = print_medium_size,
						mount_id = mount_id,
						mount_size = mount_size,
						board_id =  board_id,
						board_size = board_size,
						acrylic_id = acrylic_id,
						acrylic_size = acrylic_size,
						stretch_id = stretch_id,
						stretch_size = stretch_size,
						image_width = image_width,
						image_height = image_height,
						created_date = today,
						updated_date =  today,
						stock_image_id = prod.product_id
					)
				elif prod.product_type_id == 'USER-IMAGE':
					usercartitems = Cart_user_image(
						cart = newusercart,
						promotion = promotion,
						quantity = qty,
						item_unit_price = item_unit_price,
						item_sub_total = item_sub_total,
						item_disc_amt = disc_amt,
						item_tax  = item_tax,
						item_total = total_price,
						moulding_id = moulding_id,
						moulding_size =  mount_size,
						print_medium_id = print_medium_id,
						print_medium_size = print_medium_size,
						mount_id = mount_id,
						mount_size = mount_size,
						board_id =  board_id,
						board_size = board_size,
						acrylic_id = acrylic_id,
						acrylic_size = acrylic_size,
						stretch_id = stretch_id,
						stretch_size = stretch_size,
						image_width = image_width,
						image_height = image_height,
						created_date = today,
						updated_date =  today,
						user_image_id = prod.product_id
					)
				elif prod.product_type_id == 'STOCK-COLLAGE':
					usercartitems = Cart_stock_collage(
						cart = newusercart,
						promotion = promotion,
						quantity = qty,
						item_unit_price = item_unit_price,
						item_sub_total = item_sub_total,
						item_disc_amt = disc_amt,
						item_tax  = item_tax,
						item_total = total_price,
						moulding_id = moulding_id,
						moulding_size =  mount_size,
						print_medium_id = print_medium_id,
						print_medium_size = print_medium_size,
						mount_id = mount_id,
						mount_size = mount_size,
						board_id =  board_id,
						board_size = board_size,
						acrylic_id = acrylic_id,
						acrylic_size = acrylic_size,
						stretch_id = stretch_id,
						stretch_size = stretch_size,
						image_width = image_width,
						image_height = image_height,
						created_date = today,
						updated_date =  today,
						stock_collage_id = prod.product_id
					)
				elif prod.product_type_id == 'ORIGINAL-ART':
					usercartitems = Cart_original_art(
						cart = newusercart,
						promotion = promotion,
						quantity = qty,
						item_unit_price = item_unit_price,
						item_sub_total = item_sub_total,
						item_disc_amt = disc_amt,
						item_tax  = item_tax,
						item_total = total_price,
						moulding_id = moulding_id,
						moulding_size =  mount_size,
						print_medium_id = print_medium_id,
						print_medium_size = print_medium_size,
						mount_id = mount_id,
						mount_size = mount_size,
						board_id =  board_id,
						board_size = board_size,
						acrylic_id = acrylic_id,
						acrylic_size = acrylic_size,
						stretch_id = stretch_id,
						stretch_size = stretch_size,
						image_width = image_width,
						image_height = image_height,
						created_date = today,
						updated_date =  today,
						original_art_id = prod.product_id
					)
				
			usercartitems.save()

			cart_qty = qty
			
		except IntegrityError as e:
			err_flg = True
			msg = 'Apologies!! Could not save your cart. Please use the "Contact Us" link at the bottom of this page and let us know. We will be glad to help you.'

		except Error as e:
			err_flg = True
			msg = 'Apologies!! Could not save your cart. Please use the "Contact Us" link at the bottom of this page and let us know. We will be glad to help you.'


	# Update the status of the User_image to "MTC" (Moved to Cart)
	if prod.product_type_id == "USER-IMAGE":
		try: 
			u = User_image (
				product_id = prod.product_id,
				product_type_id = prod.product_type_id,
				session_id = prod.session_id,
				user = prod.user,
				image_to_frame = prod.image_to_frame,
				status = 'MTC',
				created_date = prod.created_date
			)
			u.save()
		except Error as e:
			err_flg = True
			msg = 'Apologies!! We had a system issue. Please use the "Contact Us" link at the bottom of this page and let us know. We will be glad to help you.'
	
	
	return( JsonResponse({'msg':msg, 'cart_qty':cart_qty, 'err_flg':err_flg}, safe=False) )
		
@csrf_exempt		
def update_cart_item(request):
	json_data = json.loads(request.body.decode("utf-8"))

	# Get existing cart items
	cart_item = Cart_item_view.objects.select_related('product', 'promotion').filter( 
		cart_item_id = json_data['cart_item_id'], cart_id = json_data['cart_id'],
			product__product_type_id = F('product_type_id')).first()

	if not cart_item:
		return JsonResponse({'msg':'Not cart items found for cart # ' + cart_item_id}, safe=False)	
	
	# Get the cart this item is associated with
	cart = Cart.objects.filter(cart_id = cart_item.cart_id, cart_status = "AC").first()
		
	updated_qty = int(json_data['updated_qty'])
	##############################################
	#get item_price
	##############################################
	image_price = 0
	item_price = 0
	disc_amt = 0
	item_unit_price = 0


	if cart_item.product:
		c_item = get_item_price_by_cart_item(json_data['cart_item_id'])
	
	if c_item:
		item_price = round(c_item['item_price'])
		disc_amt = round(c_item['disc_amt'])
		item_unit_price = round(c_item['item_unit_price'], -1)

	# TAX Calculations
	item_tax = 0
	item_sub_total = 0
	taxes = get_taxes()
	#if product exists then it's an image tax
	if cart_item.product_type_id == 'STOCK-IMAGE' :
		tax_rate = taxes['stock_image_tax_rate']
	elif cart_item.product_type_id == 'USER-IMAGE' :
		tax_rate = taxes['user_image_tax_rate']
	elif cart_item.product_type_id == 'STOCK-COLLAGE' :
		tax_rate = taxes['stock_collage_tax_rate']
	elif cart_item.product_type_id == 'ORIGINAL-ART' :
		tax_rate = taxes['original_art_tax_rate']
	elif cart_item.product_type_id == 'FRAME' :
		tax_rate = taxes['frame_tax_rate']

		
	# Update the discount, tax, sub_total and item_total as per the updated quantity
	item_total = item_price * updated_qty
	unit_disc_amt = disc_amt
	disc_amt = disc_amt * updated_qty
	item_unit_price = item_unit_price
	
	# Calculate tax and sub_total
	item_sub_total = round( ( item_total / (1 + (tax_rate/100)) ), 2)
	item_tax = item_total - item_sub_total
	#############################################################
	
	cart_total = cart.cart_total - cart_item.item_total + item_total
	# Calcuate referral discount
	ref_disc_amount = 0
	ref = apply_referral(request, cart_total)
	if ref['status'] == 'SUCCESS':
		cart_total = ref['cart_total']
		ref_disc_amount = ref['disc_amt']
	
	# Calculate voucher discount
	if cart.voucher_id:		
		voucher = Voucher.objects.filter(voucher_id = cart.voucher_id).first()
		if voucher.voucher_code:
			res = apply_voucher_py(request, cart.cart_id, voucher.voucher_code, cart_total)
			vou = json.loads(res.content)		
			if 'status' in vou:
				status = vou['status']
			else:
				status = ''
			if status == 'SUCCESS' or status == 'SUCCESS-':
				if 'disc_amount' in vou:
					voucher_disc_amount = vou['disc_amount'] 
				else:
					voucher_disc_amount = 0
				cart.voucher_disc_amount = Decimal(voucher_disc_amount)
				cart.cart_disc_amt  = cart.referral_disc_amount + Decimal(voucher_disc_amount)
				
				if 'cart_total' in vou:
					cart_total = Decimal(vou['cart_total'])

	msg = "SUCESS"

	# Update the cart item and the cart
	try :
		'''
		newusercart = Cart(
			cart_id = cart.cart_id,
			store = cart.store,
			session_id = cart.session_id,
			user_id = cart.user_id,
			voucher_id = cart.voucher_id,
			voucher_disc_amount = cart.voucher_disc_amount,
			referral_id = cart.referral_id,
			referral_disc_amount = ref_disc_amount,
			quantity =  cart.quantity - cart_item.quantity + updated_qty,
			cart_sub_total = cart.cart_sub_total - cart_item.item_sub_total + item_sub_total,
			cart_disc_amt  = cart.cart_disc_amt - cart_item.item_disc_amt + disc_amt,
			cart_tax  = cart.cart_tax - cart_item.item_tax + item_tax,
			cart_total = cart_total,
			cart_status = cart.cart_status,
			created_date = cart.created_date,
			updated_date = today
		)
		newusercart.save()
		'''		
		# Reclaculate tax after applying voucher
		cart_sub_total = round( cart_total / (1 + (tax_rate/100)), 2 )
		cart_tax = cart_total - cart_sub_total
		
		cart.cart_disc_amt  = cart.cart_disc_amt - (cart_item.quantity * unit_disc_amt) + disc_amt
		cart.quantity =  cart.quantity - cart_item.quantity + updated_qty
		cart.cart_sub_total = cart_sub_total
		cart.cart_tax  = cart_tax
		cart.cart_total = cart_total
		cart.save()		

		if cart_item.product_type_id == 'STOCK-IMAGE':
			usercartitems = Cart_stock_image(
				cart_item_id = cart_item.cart_item_id,
				cart_id = cart_item.cart_id,
				promotion = cart_item.promotion,
				quantity = updated_qty,
				item_unit_price = item_unit_price,
				item_sub_total = item_sub_total,
				item_disc_amt  = disc_amt,
				item_tax  = item_tax,
				item_total = item_total,
				moulding_id = cart_item.moulding_id,
				moulding_size = cart_item.moulding_size,
				print_medium_id = cart_item.print_medium_id,
				print_medium_size = cart_item.print_medium_size,
				mount_id = cart_item.mount_id,
				mount_size = cart_item.mount_size,
				board_id = cart_item.board_id,
				board_size = cart_item.board_size,
				acrylic_id = cart_item.acrylic_id,
				acrylic_size = cart_item.acrylic_size,
				stretch_id = cart_item.stretch_id,
				stretch_size = cart_item.stretch_size,
				image_width = cart_item.image_width,
				image_height = cart_item.image_height,
				created_date = cart_item.created_date,
				updated_date = today,
				stock_image_id = cart_item.product_id
				)

		elif cart_item.product_type_id == 'USER-IMAGE':
			usercartitems = Cart_user_image(
				cart_item_id = cart_item.cart_item_id,
				cart_id = cart_item.cart_id,
				promotion = cart_item.promotion,
				quantity = updated_qty,
				item_unit_price = item_unit_price,
				item_sub_total = item_sub_total,
				item_disc_amt  = disc_amt,
				item_tax  = item_tax,
				item_total = item_total,
				moulding_id = cart_item.moulding_id,
				moulding_size = cart_item.moulding_size,
				print_medium_id = cart_item.print_medium_id,
				print_medium_size = cart_item.print_medium_size,
				mount_id = cart_item.mount_id,
				mount_size = cart_item.mount_size,
				board_id = cart_item.board_id,
				board_size = cart_item.board_size,
				acrylic_id = cart_item.acrylic_id,
				acrylic_size = cart_item.acrylic_size,
				stretch_id = cart_item.stretch_id,
				stretch_size = cart_item.stretch_size,
				image_width = cart_item.image_width,
				image_height = cart_item.image_height,
				created_date = cart_item.created_date,
				updated_date = today,
				user_image_id = cart_item.product_id
				)
		elif cart_item.product_type_id == 'STOCK-COLLAGE':
			usercartitems = Cart_stock_collage(
				cart_item_id = cart_item.cart_item_id,
				cart_id = cart_item.cart_id,
				promotion = cart_item.promotion,
				quantity = updated_qty,
				item_unit_price = item_unit_price,
				item_sub_total = item_sub_total,
				item_disc_amt  = disc_amt,
				item_tax  = item_tax,
				item_total = item_total,
				moulding_id = cart_item.moulding_id,
				moulding_size = cart_item.moulding_size,
				print_medium_id = cart_item.print_medium_id,
				print_medium_size = cart_item.print_medium_size,
				mount_id = cart_item.mount_id,
				mount_size = cart_item.mount_size,
				board_id = cart_item.board_id,
				board_size = cart_item.board_size,
				acrylic_id = cart_item.acrylic_id,
				acrylic_size = cart_item.acrylic_size,
				stretch_id = cart_item.stretch_id,
				stretch_size = cart_item.stretch_size,
				image_width = cart_item.image_width,
				image_height = cart_item.image_height,
				created_date = cart_item.created_date,
				updated_date = today,
				stock_collage_id = cart_item.product_id
				)
		elif cart_item.product_type_id == 'ORIGINAL-ART':
			usercartitems = Cart_original_art(
				cart_item_id = cart_item.cart_item_id,
				cart_id = cart_item.cart_id,
				promotion = cart_item.promotion,
				quantity = updated_qty,
				item_unit_price = item_unit_price,
				item_sub_total = item_sub_total,
				item_disc_amt  = disc_amt,
				item_tax  = item_tax,
				item_total = item_total,
				moulding_id = cart_item.moulding_id,
				moulding_size = cart_item.moulding_size,
				print_medium_id = cart_item.print_medium_id,
				print_medium_size = cart_item.print_medium_size,
				mount_id = cart_item.mount_id,
				mount_size = cart_item.mount_size,
				board_id = cart_item.board_id,
				board_size = cart_item.board_size,
				acrylic_id = cart_item.acrylic_id,
				acrylic_size = cart_item.acrylic_size,
				stretch_id = cart_item.stretch_id,
				stretch_size = cart_item.stretch_size,
				image_width = cart_item.image_width,
				image_height = cart_item.image_height,
				created_date = cart_item.created_date,
				updated_date = today,
				original_art_id = cart_item.product_id
				)

		usercartitems.save()


	except IntegrityError as e:
		msg = 'Apologies!! Could not save your cart. Please use the "Contact Us" link at the bottom of this page and let us know. We will be glad to help you.'

	except Error as e:
		msg = 'Apologies!! Could not save your cart. Please use the "Contact Us" link at the bottom of this page and let us know. We will be glad to help you.'
			
	
	return( JsonResponse({'msg':msg, 'updated_qty':updated_qty}, safe=False) )

	
@csrf_exempt	
def delete_cart_item(request):	
	cart_item_id = request.POST.get('cart_item_id','')
	sub_total = request.POST.get('sub_total','')
	cart_total = request.POST.get('cart_total','')
	tax = request.POST.get('tax','')
	item_total = request.POST.get('item_total','')
	
	cart_item = Cart_item_view.objects.filter(cart_item_id = cart_item_id).first()
	if not cart_item:
		return JsonResponse({'msg':'Not cart items found for cart # ' + cart_item_id}, safe=False)	
	
	# Get the cart this item is associated with
	cart = Cart.objects.filter(cart_id = cart_item.cart_id, cart_status = "AC").first()
	
	# number of items in the cart
	num_cart_item = Cart_item_view.objects.filter(cart = cart).count()
	
	# Get related order
	order = Order.objects.filter( cart = cart ).first()
	order_item = {}
	
	if order:
		order_item = Order_items_view.objects.filter(
					order = order,
					product_id = cart_item.product_id,
					product_type_id = cart_item.product_type_id,
					moulding = cart_item.moulding,
					print_medium = cart_item.print_medium,
					mount = cart_item.mount,
					mount_size = cart_item.mount_size,
					board = cart_item.board,
					acrylic = cart_item.acrylic,
					stretch = cart_item.stretch,
					image_width = cart_item.image_width,
					image_height = cart_item.image_height 
				).first()	

	msg = "SUCCESS"

	try :
		# Delete Order Item from respective product types
		if order_item :
			if order_item.product_type_id == 'STOCK-IMAGE':
				oi = Order_stock_image.objects.get(cart_item_id = cart_item.cart_item_id)
			if order_item.product_type_id == 'USER-IMAGE':
				oi = Order_user_image.objects.get(cart_item_id = cart_item.cart_item_id)
			if order_item.product_type_id == 'STOCK-COLLAGE':
				oi = Order_stock_collage.objects.get(cart_item_id = cart_item.cart_item_id)
			if order_item.product_type_id == 'ORIGINAL-ART':
				oi = Order_original_art.objects.get(cart_item_id = cart_item.cart_item_id)
		
			oi.delete()			
		
		# Delete Cart Item from respective product types
		if cart_item.product_type_id == 'STOCK-IMAGE':
			ci = Cart_stock_image.objects.get(cart_item_ptr_id = cart_item.cart_item_id)
		if cart_item.product_type_id == 'USER-IMAGE':
			ci = Cart_user_image.objects.get(cart_item_ptr_id = cart_item.cart_item_id)
		if cart_item.product_type_id == 'STOCK-COLLAGE':
			ci = Cart_stock_collage.objects.get(cart_item_ptr_id = cart_item.cart_item_id)
		if cart_item.product_type_id == 'ORIGINAL-ART':
			ci = Cart_original_art.objects.get(cart_item_ptr_id = cart_item.cart_item_id)

		ci.delete()	
			
		# If this was the last item in the cart then delete the cart as well
		# if there are more items in the cart, then update cart quantity and remove the item
		if num_cart_item == 1:
			if order:
				## Delete order shipping and billing address
				os = Order_shipping.objects.filter(order_id = order.order_id).first()
				if os:
					os.delete()
				ob = Order_billing.objects.filter(order_id = order.order_id).first()
				if os:
					ob.delete()
					
				order.delete()

			if cart:
				cart.delete()
				
		else :
			if order :
				o = Order (
					order_id = order.order_id,
					order_number = order.order_number,
					order_date = order.order_date,
					cart_id = order.cart_id, 
					session_id = order.session_id,
					quantity = cart.quantity - cart_item.quantity,
					store_id = settings.STORE_ID,
					user = cart.user,
					voucher_id = order.voucher_id,
					voucher_disc_amount = order.voucher_disc_amount,
					referral = order.referral,
					referral_disc_amount = order.referral_disc_amount,
					sub_total = order.sub_total - (cart_item.item_sub_total),
					order_discount_amt = order.order_discount_amt - cart_item.item_disc_amt,
					tax = order.tax - (cart_item.item_tax),
					order_total = cart.cart_total - cart_item.item_total,
					shipping_cost = order.shipping_cost,
					shipping_method = order.shipping_method,
					shipper = order.shipper,
					shipping_status = order.shipping_status,
					created_date = order.created_date,
					updated_date = today,
					order_status = order.order_status	
				)
				o.save()

			# TAX Calculations
			taxes = get_taxes()
			#if product exists then it's an image tax
			if cart_item.product_type_id == 'STOCK-IMAGE' :
				tax_rate = taxes['stock_image_tax_rate']
			elif cart_item.product_type_id == 'USER-IMAGE' :
				tax_rate = taxes['user_image_tax_rate']
			elif cart_item.product_type_id == 'STOCK-COLLAGE' :
				tax_rate = taxes['stock_collage_tax_rate']
			elif cart_item.product_type_id == 'ORIGINAL-ART' :
				tax_rate = taxes['original_art_tax_rate']
			elif cart_item.product_type_id == 'FRAME' :
				tax_rate = taxes['frame_tax_rate']

			'''
			########################################################
			#	Get voucher details, if any. Adjust the totals based
			#	on the applicable voucher amount 
			########################################################					
			voucher_disc_amount = cart.voucher_disc_amount
			cart_disc_amt = cart.cart_disc_amt - cart_item.item_disc_amt
			if cart.voucher_id:
				voucher = Voucher.objects.filter(voucher_id = cart.voucher_id).first()
				if voucher.voucher_code:
					disc_type = voucher.discount_type
					disc_value = voucher.discount_value
					if disc_type == 'PERCENTAGE':
						voucher_disc_amount = cart_sub_total * voucher.discount_value/100
						# Remove old voucher discount and add new 
						cart_disc_amt = cart_disc_amt - cart.voucher_disc_amount + voucher_disc_amount 
						cart_total = cart_total - cart.voucher_disc_amount + voucher_disc_amount
					else:
						None	# Do nothing, the cash value is already part of cart_disc_amt and cart total already includes that
			########################################################
			#	END: Apply Voucher, if any
			########################################################			
			
			# TAX Calculations
			taxes = get_taxes()
			#if product exists then it's an image tax
			if cart_item.product_type_id == 'STOCK-IMAGE' :
				tax_rate = taxes['stock_image_tax_rate']
			elif cart_item.product_type_id == 'USER-IMAGE' :
				tax_rate = taxes['user_image_tax_rate']
			elif cart_item.product_type_id == 'STOCK-COLLAGE' :
				tax_rate = taxes['stock_collage_tax_rate']
			elif cart_item.product_type_id == 'ORIGINAL-ART' :
				tax_rate = taxes['original_art_tax_rate']
			elif cart_item.product_type_id == 'FRAME' :
				tax_rate = taxes['frame_tax_rate']

			'''
			# Reclaculate tax & sub total after applying voucher
			cart_total = cart.cart_total - cart_item.item_total
			cart_sub_total = round( cart_total / (1 + (tax_rate/100)), 2 )			
			cart_tax = cart_total - cart_sub_total
			
			# Update cart
			cart.quantity = cart.quantity - cart_item.quantity
			cart.cart_unit_price = cart.cart_unit_price - cart_item.item_unit_price
			if cart.voucher_id:
				cart.voucher_disc_amount = cart.voucher_disc_amount - cart_item.item_disc_amt
			cart.cart_disc_amt = cart.cart_disc_amt - cart_item.item_disc_amt
			cart.cart_sub_total = cart_sub_total
			cart.cart_tax  = cart_tax
			cart.cart_total = cart_total
			cart.save()				
			'''
			## Update for any existing voucher already applied to cart
			if cart.voucher_id:
				voucher = Voucher.objects.get(voucher_id = cart.voucher_id)
				response = apply_voucher_py_new(request, cart.cart_id, voucher.voucher_code, 
					cart_total, cart_sub_total, False)
				res = json.loads(response.content.decode('utf-8'))
				if res['status'] == 'SUCCESS' or res['status'] == 'SUCCESS-':
					print('OK')
				else:
					msg = "There was an issue while apply your Coupan: " + res['status']
					err_flg = True
			'''		
	except cart.DoesNotExist:
		msg = "Cart does not exist"
	
	except cart_item.DoesNotExist:
		msg = "Cart item does not exist"
	
	except Error as e:
		msg = 'Apologies!! Could not save your cart. Please use the "Contact Us" link at the bottom of this page and let us know. We will be glad to help you.'	
	
	return JsonResponse({'msg':msg}, safe=False)


	
@csrf_exempt
def apply_voucher(request):	

	cart_id = int(request.POST.get('cart_id', '0'))
	voucher_code = request.POST.get('voucher_code', '')
	cart_total = Decimal(request.POST.get('cart_total', '0'))

	res = apply_voucher_py_new(request, cart_id, voucher_code, cart_total)

	vou = json.loads(res.content)
	
	if 'status' in vou:
		status = vou['status']
	else:
		status = ''
	if 'disc_amount' in vou:
		disc_amount = vou['disc_amount'] 
	else:
		disc_amount = 0
	if 'cart_total' in vou:
		cart_total = vou['cart_total']
	if 'voucher_bal_amount' in vou:
		voucher_bal_amount = vou['voucher_bal_amount']
	else:
		voucher_bal_amount = 0
	
	if 'cart_disc_amt' in vou:
		cart_disc_amt = vou['cart_disc_amt']
	else:
		cart_disc_amt = 0
	
	
	return JsonResponse({"status":status, 'disc_amount': disc_amount, 
				'cart_total':cart_total, 'voucher_bal_amount':voucher_bal_amount,
				'cart_disc_amt':cart_disc_amt})	

def apply_voucher_py(request, cart_id, voucher_code, cart_total):
	status = "SUCCESS"	
	if voucher_code == '':
		return JsonResponse({"status":"INVALID-CODE"})

	# get logged in user
	try: 
		user = User.objects.get(username = request.user)
	except User.DoesNotExist:
		user = None	
		
	voucher = Voucher.objects.filter(voucher_code = voucher_code, effective_from__lte = today, 
			effective_to__gte = today, store_id = settings.STORE_ID).first()			
		
	# Get the gift transaction, it there's one for the logged in user

	if not voucher :
		return JsonResponse({"status":"INVALID-CODE"})
	
	if user is not None:
		try:
			eGift = Egift.objects.get(voucher = voucher, receiver = user)		
		except Egift.DoesNotExist:
			eGift = {}
	else:
		eGift = {}

	cart = Cart.objects.filter(cart_id = cart_id, cart_status = "AC").first()
	
	# Check if voucher discount is already applied to cart
	if cart.voucher_disc_amount:
		applied_disc = cart.voucher_disc_amount
	else:
		applied_disc = 0
	
	voucher_user = Voucher_user.objects.filter(voucher = voucher, effective_from__lte = today, 
			effective_to__gte = today).first()

	if not voucher.all_applicability:
		if not voucher_user :
			return JsonResponse({"status":"INVALID-CODE"})
		if voucher_user.used_date != None :
			return JsonResponse({"status":"USED"})				
		if voucher_user.user != user:
			return JsonResponse({"status":"USER-MISMATCH"})	
		if voucher_user.expiry_date < today.date():
			return JsonResponse({"status":"EXPIRED"})
			
	disc_type = voucher.discount_type
	disc_amount = 0
	new_cart_total = 0
	voucher_bal_amount = 0
	avl_disc_amount = 0
	total_disc_amount = 0

	if eGift:
		# Get the eGift transaction amount
		eGift_redemption = Egift_redemption.objects.filter( egift = eGift 
				).aggregate(total_redemption=Sum('redemption_amount'))		
		if eGift_redemption['total_redemption']:
			total_redemption = Decimal(eGift_redemption['total_redemption'])
		else: 
			total_redemption = 0
		
		if total_redemption >= eGift.gift_amount:
			avl_disc_amount = 0
			status = 'NO-MORE'
		else:
			avl_disc_amount = round(eGift.gift_amount - total_redemption - applied_disc)

		# Limit discount to total cart value
		if avl_disc_amount > cart_total: 
			disc_amount = cart_total 
			new_cart_total = 0
			status = "SUCCESS-"
		else:
			disc_amount = avl_disc_amount
			new_cart_total = round(cart_total - disc_amount)
			
		total_disc_amount = round(disc_amount + applied_disc)
		voucher_bal_amount = eGift.gift_amount - total_redemption - total_disc_amount
		#if new_cart_total < 0:  # Total cart value is 0 is disc is more than cart total			
				
	else:
		if voucher.all_applicability:
			if cart.voucher_disc_amount > 0 :
				return JsonResponse({"status":"USED"})
				
			if disc_type == "PERCENTAGE":
				disc_amount = cart_total * voucher.discount_value/100
				new_cart_total = round(cart_total - ( cart_total * voucher.discount_value/100 ))
			elif disc_type == "CASH":
				if total_redemption >= eGift.gift_amount:
					avl_disc_amount = 0
					status = 'NO-MORE'	
					disc_amount = 0
					new_cart_total = cart_total
					voucher_bal_amount = 0
				else:
					disc_amount = voucher.discount_value
					new_cart_total = round(cart_total - voucher.discount_value)
					voucher_bal_amount =  voucher.discount_value - total_redemption - total_disc_amount
			else: 
				disc_amount = 0
				new_cart_total = cart_total
				
			if new_cart_total < 0:
				# Limit the discount to the total cart value
				new_cart_total = 0
			total_disc_amount = round(disc_amount + applied_disc)
		else:
			return JsonResponse({"status":"DOESNOT-APPLY"})
			
	#if cart.voucher_id and not eGift:
	#	return JsonResponse({"status":"ONLY-ONE"})

	# Update the cart with voucher
	if cart :
		
		try:
			cart_disc_amt = disc_amount + cart.cart_disc_amt
			
			c = Cart (
				cart_id = cart_id,
				store = cart.store,
				session_id = cart.session_id,
				user = cart.user,
				voucher_id = voucher.voucher_id,
				voucher_disc_amount = total_disc_amount,
				referral = cart.referral,
				referral_disc_amount = cart.referral_disc_amount,
				quantity = cart.quantity,
				cart_sub_total = cart.cart_sub_total,
				cart_disc_amt  = cart.cart_disc_amt + total_disc_amount,
				cart_tax  = cart.cart_tax,
				cart_total = new_cart_total,
				created_date = cart.created_date,
				updated_date =  today,
				cart_status = cart.cart_status
			)
			c.save()

			# if there is no more balance left in voucher, then update the 
			# voucher as used.
			if voucher_bal_amount == 0:
				if voucher_user:
					v = Voucher_user (
						id = voucher_user.id,
						voucher = voucher_user.voucher,
						user = voucher_user.user,
						effective_from = voucher_user.effective_from,
						effective_to = voucher_user.effective_to,
						used_date = today
					)
					v.save()

			## if it's eGift, update the records
			'''
			if eGift:
				# Update gift redemption accordongly
				e = Egift_redemption ( 
						egift = eGift,
						redemption_date = today,
						redemption_amount = disc_amount)
				e.save()				
			'''
		except Error as e:
			status = 'INT-ERR'

	return JsonResponse({"status":status, 'disc_amount': total_disc_amount, 
				'cart_total':new_cart_total, 'voucher_bal_amount':voucher_bal_amount,
				'cart_disc_amt':cart.cart_disc_amt, 'disc_type':disc_type})
	

@csrf_exempt
def apply_referral(request, cart_total):	

	status = ''
	disc_perc = 10
	disc_amt = 0
	# Get logged in user
	if request.user.is_authenticated:
		user = User.objects.get(username = request.user)
	else:
		msg = ''
		return ({"status":"NO-USER", 'msg':msg, 'disc_perc':'0',
			'cart_total':cart_total,'referral_id':0, 'disc_amt':0, 'disc_amt':disc_amt})

	
	## Check if it's the referrer 
	referrer = Referral.objects.filter(referred_by = request.user)
	for r in referrer:
		if r.referred_by_claimed_date is None:
			referee = User.objects.filter(email = r.email_id).first()			
			# Check if the referee has placed any order
			if referee: 
				ord = Order.objects.filter(user = referee, order_status = 'PC')
				if ord: 
					disc_amt = ( cart_total * 10/100 )
					new_cart_total = cart_total - disc_amt
					status = "SUCCESS"
					msg = "Congratulations! you get 10% off on order value for a sucessful referral for " + r.email_id + "."
					return  ({'status':status, 'msg':msg, 
						'disc_perc':disc_perc, 'cart_total':new_cart_total, 
						'referral_id':r.id, 'disc_amt':disc_amt})
					

	## Check if it's the referee 
	referee = Referral.objects.filter(email_id = request.user.email).first()
	if referee:
		if referee.referee_claimed_date is None:
			disc_amt = ( cart_total * 10/100 )
			new_cart_total = cart_total - disc_amt
			status = "SUCCESS"
			msg = "Congratulations! you get 10% off on order value as a gift through a referral (" + referee.referred_by.email + ")."
			return  ({'status':status, 'msg':msg, 
				'disc_perc':disc_perc, 'cart_total':new_cart_total, 
				'referral_id':referee.id, 'disc_amt':disc_amt})
		
	# Else return no discount
	status = "NOT-FOUND"
	msg = "No valid referral found"
	return  ({'status':status, 'msg':msg, 'disc_perc':'0', 
		'cart_total':cart_total, 'referral_id':0, 'disc_amt':disc_amt})
	
@csrf_exempt	
def add_to_cart_new(request):

	err_flg = False
	msg = "Success" # to return message to the front end

	#####################################
	#  Get details for item to be added
	#####################################
	prod_id = request.POST.get('prod_id', '')
	prod_type = request.POST.get('prod_type', '')
	qty = int(request.POST.get('qty', '0'))
	cart_item_flag = request.POST.get('cart_item_flag', 'FALSE')
	
	image_width = Decimal(request.POST.get('image_width', '0'))
	image_height = Decimal(request.POST.get('image_height', '0'))
	
	sqin = image_width * image_height
	rnin = (image_width + image_height) * 2
	
	moulding_id = request.POST.get('moulding_id', '')
	if moulding_id == '0' or moulding_id == 'None' or moulding_id == '' :
		moulding_id = None

	if moulding_id:
		moulding_size = rnin
	else: 
		moulding_size = None
	print_medium_id = request.POST.get('print_medium_id', 'NA')
	print_medium_size = Decimal(request.POST.get('print_medium_size', '0'))
	mount_id = request.POST.get('mount_id', '0')
	if mount_id == '0' or mount_id == 'None' or mount_id == '':
		mount_id = None
	if mount_id:
		mount_size = Decimal(request.POST.get('mount_size', '0'))
		mount_w_left = Decimal(request.POST.get('mount_w_left', '0'))
		mount_w_right = Decimal(request.POST.get('mount_w_right', '0'))
		mount_w_left = Decimal(request.POST.get('mount_w_top', '0'))
		mount_w_left = Decimal(request.POST.get('mount_w_bottom', '0'))
		if mount_size > 5 :
			err_flg = True
			return( JsonResponse({'msg':'Sorry, mount size should be between 1 and 5 inch', 'cart_qty':qty}, safe=False) )
		
	else:
		mount_size = None
		mount_w_left = None
		mount_w_right = None
		mount_w_top = None
		mount_w_bottom = None
	acrylic_id = request.POST.get('acrylic_id', '0')
	if acrylic_id == '0' or acrylic_id == 'None' or acrylic_id == '':
		acrylic_id = None
	if acrylic_id:
		acrylic_size = sqin
	else:
		acrylic_size = None
	
	board_id = request.POST.get('board_id', '0')
	if board_id == '0' or board_id == 'None' or board_id == '':
		board_id = None
	if board_id:
		board_size = sqin
	else:
		board_size = None

	stretch_id = request.POST.get('stretch_id', '0')
	if stretch_id == '0' or stretch_id == 'None'  or stretch_id == '':
		stretch_id = None
	if stretch_id:
		stretch_size = rnin
	else:
		stretch_size = None
	
	str_item_unit_price = request.POST.get('item_unit_price', '0')
	if str_item_unit_price == '':
		str_item_unit_price = '0'
	item_unit_price = Decimal(str_item_unit_price)
	
	str_item_price = request.POST.get('total_price', '0')
	if str_item_price == '':
		str_item_price = 0
	item_price = Decimal(str_item_price)
	
	str_disc_amt = request.POST.get('disc_amt', '0')
	if str_disc_amt == '':
		str_disc_amt = 0
	disc_amt = Decimal(str_disc_amt)
	#####################################
	# END: Get details for item to be added
	#####################################


	ip_address = get_ip_addr(request)


	#####################################
	#         Get the item price
	#####################################
	price = get_prod_price(prod_id, 
			prod_type=prod_type,
			image_width=image_width, image_height=image_height,
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
	item_unit_price = price['item_unit_price']
	item_disc_amt = price['disc_amt']
	disc_applied = price['disc_applied']
	promotion_id = price['promotion_id']
	#####################################
	# END::::    Get the item price
	#####################################	
	
	#####################################
	# 	if item price not found, return
	#####################################	
	if item_unit_price == 0 or item_unit_price is None:
		err_flg = True
		return( JsonResponse({'msg':'Price not available for this image', 'cart_qty':qty}, safe=False) )
	##################################################
	# END:	if item price not found, don't add to cart
	##################################################

	##################################################
	#	Get the product object
	##################################################
	prod = None	
	try:
		if prod_id != '':
			prod = Product_view.objects.get(product_id=prod_id, product_type = prod_type, is_published = True)
		### Currently only for STOCK-IMAGE and USER-IMAGE
		if prod.product_type == "USER-IMAGE" or prod.product_type == "STOCK-COLLAGE":
			if request.user.is_authenticated:
				user = User.objects.get(username = request.user)
				user_image = User_image.objects.filter(user = user, status = "INI").first()
			else:
				session_id = request.session.session_key
				user_image = User_image.objects.filter(session_id = session_id, status = "INI").first()			
	except Product_view.DoesNotExist:
		msg = "Product " + prod_id + " does not exist"
		err_flg = True
		return( JsonResponse({'msg':msg, 'cart_qty':qty}, safe=False) )
	except User_image.DoesNotExist:
		err_flg = True
		msg = "Couldn't find the uploaded image. Pease try again."
		return( JsonResponse({'msg':msg, 'cart_qty':qty}, safe=False) )
	##################################################
	# END:	Get the product object
	##################################################


	
	########################################################
	#	Calculate sub total, tax for the item
	########################################################
	item_tax = 0
	item_sub_total = 0
	#### Get Tax
	taxes = get_taxes()
	if prod.product_type_id == 'STOCK-IMAGE':
		tax_rate = taxes['stock_image_tax_rate']
	if prod.product_type_id == 'ORIGINAL-ART':
		tax_rate = taxes['original_art_tax_rate']
	if prod.product_type_id == 'USER-IMAGE':
		tax_rate = taxes['user_image_tax_rate']
	if prod.product_type_id == 'STOCK-COLLAGE':
		tax_rate = taxes['stock_image_tax_rate']
	if prod.product_type_id == 'FRAME':
		tax_rate = taxes['frame_tax_rate']	
	
	# Calculate tax and sub_total
	item_unit_price = item_unit_price * qty
	item_sub_total = round( (item_price*qty) / (1 + (tax_rate/100)), 2 )
	item_tax = round( (item_price*qty) - item_sub_total, 2 )
	########################################################
	#	END: Calculate sub total, tax for the item
	########################################################
	

	##############################################################
	# 	Get the product promotion details, if the item carries it
	##############################################################
	promo = {}
	if prod:
		promo = get_product_promotion(prod_id)	
	promotion = {}
	if promo :
		if promo['promotion_id']:
			promotion = Promotion.objects.filter(promotion_id = promo['promotion_id']).first()
	#####################################################
	# END:	Get the product promotion, if the item carries it
	#####################################################
	

	########################################################
	# 	Check if there is an active cart and get the cart_exists
	# 	Else have an empty cart object. Also set cart exists flag
	########################################################
	userid = None
	cart_exists = False
	usercart = {}
	cart_qty = 0
	''' Let's check if the user has a cart open '''
	sessionid = request.session.session_key
	if request.user.is_authenticated:
		try:
			userid = User.objects.get(username = request.user)
			usercart = Cart.objects.get(user_id = userid, cart_status = "AC") 
			#cart.objects.filter(user_id = userid)[:1]
		except Cart.DoesNotExist:
			usercart = {}
			cart_exists = False
			
		if usercart:
			cart_exists = True
		else:
			cart_exists = False
	else:
		if sessionid is None:
			request.session.create()
			sessionid = request.session.session_key
			cart_exists = False		 
		else:
			try:
				# Get usercart by session
				usercart = Cart.objects.get(session_id = sessionid, cart_status="AC")
				#cart.objects.filter(session_id = sessionid)[:1]
			except Cart.DoesNotExist:
				usercart = {}
				cart_exists = False
			
			if usercart:
				cart_exists = True
			else:
				cart_exists = False;
	########################################################
	#	END: 	Check if there an active cart and get the cart_exists
	# 	Else have an empty cart object. Also set cart exists flag
	########################################################


	########################################################
	# Add_to_cart handles two cases:
	# 1. Entirely new item being added to cart
	# 2. An existing item is being added back after editing it
	#
	# Get the related cart item, if it's existing
	########################################################
	cart_disc_amt = 0
	cart_item = {}
	if cart_exists:
		''' Check if product or user image exists in cart '''
		if prod:
			## if this is from existing cart item then we only check if product id
			## exists in the cart, as other factors can be changed by user
			if cart_item_flag == 'TRUE':
				cart_item = Cart_item_view.objects.filter(cart_id = usercart.cart_id, 
						product_id = prod_id).first()						
			else:
				cart_item = Cart_item_view.objects.filter(cart_id = usercart.cart_id, 
							product_id = prod_id, moulding_id = moulding_id,
							print_medium_id = print_medium_id, mount_id = mount_id,
							mount_size = mount_size, acrylic_id = acrylic_id,
							board_id = board_id, stretch_id = stretch_id ).first()
	########################################################
	# END: Get the related cart item, if it's existing
	########################################################


	########################################################
	#	Calculcate the cart total, based on if it's an existing
	#	item being modified or a new item
	# cart_flag_item is 'TRUE', when an existing item is modified
	########################################################
	if cart_item_flag == 'TRUE' or cart_item :
		cart_total = Decimal(usercart.cart_total) - (cart_item.item_total) + (item_price * qty)
	else:
		if usercart:
			cart_total = Decimal(usercart.cart_total) + (item_price * qty)
		else:
			cart_total = (item_price * qty)

	########################################################
	#	Get voucher details, if any. Adjust the totals based
	#	on the applicable voucher amount 
	########################################################
	'''
	if usercart:
		voucher_disc_amount = usercart.voucher_disc_amount
		## if it's the same cart item, then remove earlier discount and add new discount
		if cart_item:
			cart_disc_amt = usercart.cart_disc_amt - cart_item.item_disc_amt + (item_disc_amt * qty)
		else:
			cart_disc_amt = usercart.cart_disc_amt + (item_disc_amt * qty)
		if usercart.voucher_id:
			voucher = Voucher.objects.filter(voucher_id = usercart.voucher_id).first()
			if voucher.voucher_code:
				disc_type = voucher.discount_type
				disc_value = voucher.discount_value
				if disc_type == 'PERCENTAGE':
					voucher_disc_amount = cart_total * voucher.discount_value/100
					# Remove old voucher discount and add new 
					cart_disc_amt = cart_disc_amt - usercart.voucher_disc_amount + voucher_disc_amount 
					cart_total = cart_total - usercart.voucher_disc_amount + voucher_disc_amount
				else:
					None	# Do nothing, the cash value is already part of cart_disc_amt and cart total already includes that
	'''
	########################################################
	#	END: Apply Voucher, if any
	########################################################

	
	########################################################
	#	Calculate sub total, tax for the CART
	########################################################
	'''
	taxes = get_taxes()
	if prod.product_type_id == 'STOCK-IMAGE':
		tax_rate = taxes['stock_image_tax_rate']
	if prod.product_type_id == 'ORIGINAL-ART':
		tax_rate = taxes['original_art_tax_rate']
	if prod.product_type_id == 'USER-IMAGE':
		tax_rate = taxes['user_image_tax_rate']
	if prod.product_type_id == 'STOCK-COLLAGE':
		tax_rate = taxes['stock_image_tax_rate']
	if prod.product_type_id == 'FRAME':
		tax_rate = taxes['frame_tax_rate']	
	'''
	## Before tax and vou, referral disc
	if usercart:
		if cart_item_flag == 'TRUE' or cart_item :
			cart_unit_price = item_unit_price
		else:
			cart_unit_price = usercart.cart_unit_price + item_unit_price
	else:
		cart_unit_price = item_unit_price
		
	# Calculate tax and sub_total(after discount)
	cart_sub_total = round( (cart_total) / (1 + (tax_rate/100)), 2 ) 
	cart_tax = round((cart_total) - cart_sub_total, 2)
	########################################################
	#	END: Calculate sub total, tax for the cart
	########################################################

	########################################################
	#	Update the CART
	########################################################
	try:
		if usercart :
			## To remove the existing cart item qty and use new qty
			if cart_item:
				cart_item_qty = cart_item.quantity 
				unit_price = usercart.cart_unit_price - cart_item.item_unit_price + item_unit_price
				disc = usercart.cart_disc_amt
			else:
				cart_item_qty = 0
				unit_price = usercart.cart_unit_price + item_unit_price
				disc = usercart.cart_disc_amt 
			uc = Cart.objects.filter(cart_id = usercart.cart_id).update(
					#voucher_disc_amount = voucher_disc_amount,
					quantity = usercart.quantity - cart_item_qty + qty,
					cart_unit_price = unit_price,
					cart_sub_total = cart_sub_total,
					cart_disc_amt  = disc,
					cart_tax  = cart_tax,
					cart_total = cart_total,
					updated_date = today,
					ip_address = ip_address
				)
			
			## Update usercart object to have the latest values
			usercart.quantity = usercart.quantity - cart_item_qty + qty
			#usercart.cart_unit_price = cart_unit_price
			usercart.cart_sub_total = cart_sub_total
			#usercart.cart_disc_amt  = cart_disc_amt
			usercart.cart_tax  = cart_tax
			usercart.cart_total = cart_total
			usercart.updated_date = today
			
		else:
			## For a new cart, there will not be any voucher or referral discount.
			## Only amount discount will include will be promotion discount for the
			## current item
			newusercart = Cart(
				store = ecom,
				session_id = sessionid,
				user = userid,
				voucher_id = None,
				voucher_disc_amount = 0,
				referral = None,
				referral_disc_amount = 0,
				quantity =  qty,
				cart_unit_price = item_unit_price,
				cart_sub_total = item_sub_total,
				cart_disc_amt = 0,
				cart_tax  = item_tax,
				cart_total = item_price,
				cart_status = 'AC',
				created_date = today,
				updated_date = today,
				ip_address = ip_address
			)
			newusercart.save()	
	except IntegrityError as e:
		err_flg = True
		msg = 'Apologies!! Could not save your cart. Please use the "Contact Us" link at the bottom of this page and let us know. We will be glad to help you.'

	except Error as e:
		err_flg = True
		msg = 'Apologies!! Could not save your cart. Please use the "Contact Us" link at the bottom of this page and let us know. We will be glad to help you.'
	########################################################
	#	END: Update the CART
	########################################################

	########################################################
	#	Update the CART ITEM
	########################################################
	## Set the appropriate cart based on existing cart or a new
	## user cart
	try:
		if usercart:
			cart = usercart
		else:
			cart = newusercart	## This one is created new

		if prod.product_type_id == 'STOCK-IMAGE':
			usercartitems = Cart_stock_image()
			usercartitems.stock_image_id = prod.product_id
		elif prod.product_type_id == 'USER-IMAGE':
			usercartitems = Cart_user_image()
			usercartitems.user_image_id = prod.product_id
		elif prod.product_type_id == 'STOCK-COLLAGE':
			usercartitems = Cart_stock_collage()
			usercartitems.stock_collage_id = prod.product_id
		elif prod.product_type_id == 'ORIGINAL-ART':
			usercartitems = Cart_original_art()
			usercartitems.original_art_id = prod.product_id

		## Update or Insert the cart item
		if cart_item:
			## Assign cart item id and created date if it's existing cart item, 
			## else new cart item id and created date will be auto created
			usercartitems.cart_item_id = cart_item.cart_item_id
			usercartitems.created_date = cart_item.created_date

		usercartitems.cart = cart
		usercartitems.promotion_id = promotion_id
		usercartitems.quantity = qty
		usercartitems.item_unit_price = item_unit_price
		usercartitems.item_sub_total = item_sub_total
		#usercartitems.item_disc_amt = (item_disc_amt*qty)
		usercartitems.item_tax  = item_tax
		usercartitems.item_total = round(item_price*qty)
		usercartitems.moulding_id = moulding_id
		usercartitems.moulding_size =  mount_size
		usercartitems.print_medium_id = print_medium_id
		usercartitems.print_medium_size = print_medium_size
		usercartitems.mount_id = mount_id
		usercartitems.mount_size = mount_size
		usercartitems.board_id =  board_id
		usercartitems.board_size = board_size
		usercartitems.acrylic_id = acrylic_id
		usercartitems.acrylic_size = acrylic_size
		usercartitems.stretch_id = stretch_id
		usercartitems.stretch_size = stretch_size
		usercartitems.image_width = image_width
		usercartitems.image_height = image_height
		usercartitems.updated_date =  today

		usercartitems.save()		
	
		## Update for any existing voucher already applied to cart
		if cart.voucher_id:
			voucher = Voucher.objects.get(voucher_id = cart.voucher_id)
			response = apply_voucher_py_new(request, cart.cart_id, voucher.voucher_code, 
				cart.cart_total, cart.cart_sub_total, False)
			res = json.loads(response.content.decode('utf-8'))
			if res['status'] == 'SUCCESS' or res['status'] == 'SUCCESS-':
				print('OK')
			else:
				msg = "There was an issue while apply your Coupan: " + res['status']
				err_flg = True
				
	
	except IntegrityError as e:
		err_flg = True
		msg = 'Apologies!! Could not save your cart. Please use the "Contact Us" link at the bottom of this page and let us know. We will be glad to help you.'

	except Error as e:
		err_flg = True
		msg = 'Apologies!! Could not save your cart. Please use the "Contact Us" link at the bottom of this page and let us know. We will be glad to help you.'


	# Update the status of the User_image to "MTC" (Moved to Cart)
	if prod.product_type_id == "USER-IMAGE":
		try: 
			u = User_image (
				product_id = prod.product_id,
				product_type_id = prod.product_type_id,
				session_id = prod.session_id,
				user = prod.user,
				image_to_frame = prod.image_to_frame,
				status = 'MTC',
				created_date = prod.created_date
			)
			u.save()
		except Error as e:
			err_flg = True
			msg = 'Apologies!! We had a system issue. Please use the "Contact Us" link at the bottom of this page and let us know. We will be glad to help you.'
	
	return( JsonResponse({'msg':msg, 'cart_qty':cart_qty, 'err_flg':err_flg}, safe=False) )




def apply_voucher_py_new(request, cart_id, voucher_code, cart_total, car_sub_total=0,
		voucher_use_check=True):
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
	## Get eGift record for logged in user
	############################################	
	if user is not None:
		try:
			eGift = Egift.objects.get(voucher = voucher, receiver_email = user.email)		
		except Egift.DoesNotExist:
			eGift = {}
	else:
		eGift = {}	
	############################################
	## END: Get eGift record for logged in user
	############################################

	############################################
	## Get the active cart and any voucher disc 
	## already applied
	############################################	
	cart = Cart.objects.filter(cart_id = cart_id, cart_status = "AC").first()
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
	if voucher_use_check:
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
	## Process eGift or Voucher transactions 
	############################################	
	if eGift:
		# Get the eGift transaction amount
		eGift_redemption = Egift_redemption.objects.filter( egift = eGift 
				).aggregate(total_redemption=Sum('redemption_amount'))		
		if eGift_redemption['total_redemption']:
			total_redemption = Decimal(eGift_redemption['total_redemption'])
		else: 
			total_redemption = 0
			
		if total_redemption >= eGift.gift_amount:
			avl_disc_amount = 0
			status = 'NO-MORE'
		else:
			avl_disc_amount = eGift.gift_amount - total_redemption - applied_disc

		# Limit discount to total cart value
		if avl_disc_amount > cart.cart_total: 
			disc_amount = cart.cart_total 
			new_cart_total = 0
			status = "SUCCESS-"
		else:
			disc_amount = avl_disc_amount
			new_cart_total = round(cart.cart_total - disc_amount)
			'''
			########################
			########################
			########################
			########################
			cart_sub_total = round(cart.cart_sub_total - disc_amount)
			taxes = get_taxes()
			####################################################
			### How to apply tax if a cart contains different 
			### product types such as STOCK IMAGE and USER IMAGE,
			### both have different tax rates
			####################################################						
			tax_rate = taxes['stock_image_tax_rate']
			cart_tax = round( (cart_sub_total * tax_rate / 100 ), 2 )
			# Reclaculate tax & cart total after applying discount
			new_cart_total = cart_sub_total + cart_tax
			cart_tax = new_cart_total - cart_sub_total
			########################
			########################
			########################
			########################			
			'''
		total_disc_amount = disc_amount + applied_disc
		voucher_bal_amount = eGift.gift_amount - total_redemption - total_disc_amount

	## If it's not eGift, then it has to be an all appliable voucher.
	## All applicable voucher is allowed only with disc type as PERCENTAGE
	else:
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
	## Update cart and cart item. 
	## Order, order item, if any, will get updated
	## when user navigates to order pages
	############################################
	if cart :		
		try:
			c = Cart (
				cart_id = cart_id,
				store = cart.store,
				session_id = cart.session_id,
				user = cart.user,
				voucher_id = voucher.voucher_id,
				voucher_disc_amount = total_disc_amount,
				referral = cart.referral,
				referral_disc_amount = cart.referral_disc_amount,
				quantity = cart.quantity,
				cart_unit_price = cart.cart_unit_price,
				cart_sub_total = new_cart_sub_total,
				cart_disc_amt  = cart.cart_disc_amt - cart.voucher_disc_amount + total_disc_amount,
				cart_tax  = cart_tax,
				cart_total = new_cart_total,
				created_date = cart.created_date,
				updated_date =  today,
				cart_status = cart.cart_status
			)
			c.save()

			## Update cart amounts based on the voucher applied.
			update_cart_voucher_amounts(request, cart_id)

			# if there is no more balance left in voucher, then update the 
			# voucher as used.
			if voucher_bal_amount == 0:
				if voucher_user:
					v = Voucher_user (
						id = voucher_user.id,
						voucher = voucher_user.voucher,
						user = voucher_user.user,
						effective_from = voucher_user.effective_from,
						effective_to = voucher_user.effective_to,
						used_date = today,
						created_date = voucher_user.created_date,
						updated_date = today
					)
					v.save()

		except Error as e:
			status = 'INT-ERR'

	#############################################
	## END: Process eGift or Voucher transactions 
	############################################	
	return JsonResponse({"status":status, 'disc_amount': total_disc_amount, 
				'cart_total':new_cart_total, 'voucher_bal_amount':voucher_bal_amount,
				'cart_disc_amt':cart.cart_disc_amt, 'disc_type':disc_type})
		
		
## Check and remove discounts is any promotion has expired and 
## update the cart.		
def validatePromotions(request):
	usercart = {}
	usercartitems = {}
	change_flag = False
	try:
		if request.user.is_authenticated:
			usr = User.objects.get(username = request.user)
			usercart = Cart.objects.get(user = usr, cart_status = "AC")
		else:
			sessionid = request.session.session_key		
			if sessionid is None:
				request.session.create()
				sessionid = request.session.session_key
				
			usercart = Cart.objects.get(session_id = sessionid, cart_status = "AC")

		usercartitems = Cart_item_view.objects.select_related('product', 
			'promotion').filter( cart = usercart.cart_id, 
				product__product_type_id = F('product_type_id')).order_by(
					'product_type')

		# If any order exists against this cart
		order = Order.objects.filter(cart_id = usercart.cart_id).first()
		
		## Order items, if any
		if order:
			orderitems = Order_items_view.objects.filter(order_id = order.order_id)
		else :
			orderitems = {}
		
	except Cart.DoesNotExist:
			usercart = {}
			## Cart items

	except Error as e:
		print(e.message)

	## If cart contains, promotion items, validate those
	for u in usercartitems:
		if u.promotion_id:
			promo = Promotion.objects.filter(promotion_id = u.promotion_id).first()
			if promo:
				if promo.effective_to < today:	## Promotion is no longer running
					change_flag = True
					## Revert promo discounts
					price = get_prod_price(u.product_id, 
							prod_type=u.product_type_id,
							image_width=u.image_width, image_height=u.image_height,
							print_medium_id = u.print_medium_id,
							acrylic_id = u.acrylic_id,
							moulding_id = u.moulding_id,
							mount_size = u.mount_size,
							mount_id = u.mount_id,
							board_id = u.board_id,
							stretch_id = u.stretch_id)
					total_price = price['item_price']
					msg = price['msg']
					cash_disc = price['cash_disc']
					percent_disc = price['percent_disc']
					item_unit_price = price['item_unit_price']
					disc_amt = price['disc_amt']
					disc_applied = price['disc_applied']
					promotion_id = price['promotion_id']					
					
					# TAX Calculations
					item_tax = 0
					item_sub_total = 0
					taxes = get_taxes()

					if u.product_type_id == 'STOCK-IMAGE':
						tax_rate = taxes['stock_image_tax_rate']
					if u.product_type_id == 'ORIGINAL-ART':
						tax_rate = taxes['original_art_tax_rate']
					if u.product_type_id == 'USER-IMAGE':
						tax_rate = taxes['user_image_tax_rate']
					if u.product_type_id == 'STOCK-COLLAGE':
						tax_rate = taxes['stock_image_tax_rate']
					if u.product_type_id == 'FRAME':
						tax_rate = taxes['frame_tax_rate']					
						
					# Calculate tax and sub_total
					item_sub_total = round( total_price / (1 + (tax_rate/100)), 2 )
					item_tax = round(total_price - item_sub_total,2)
					
					#############################################################
					## update cart item and cart
					#############################################################
					ci = Cart_item.objects.filter(cart_item_id = u.cart_item_id).update(
							promotion_id = promotion_id,
							quantity = u.quantity,
							item_unit_price = item_unit_price,
							item_sub_total = item_sub_total,
							item_disc_amt = disc_amt,
							item_tax  = item_tax,
							item_total = total_price,
							updated_date = today
						)
					if orderitems:
						## Update order item, if any
						if u.product_type == 'STOCK-IMAGE':
							oi = Order_stock_image.objects.filter(cart_item_id = u.cart_item_id).update(
									promotion_id = promotion_id,
									quantity = u.quantity,
									item_unit_price = item_unit_price,
									item_sub_total = item_sub_total,
									item_disc_amt = disc_amt,
									item_tax  = item_tax,
									item_total = total_price,
									updated_date = today
								)
						elif u.product_type == 'USER-IMAGE':
							oi = Order_user_image.objects.filter(cart_item_id = u.cart_item_id).update(
									promotion_id = promotion_id,
									quantity = u.quantity,
									item_unit_price = item_unit_price,
									item_sub_total = item_sub_total,
									item_disc_amt = disc_amt,
									item_tax  = item_tax,
									item_total = total_price,
									updated_date = today
								)
						elif u.product_type == 'STOCK-COLLAGE':
							oi = Order_stock_collage.objects.filter(cart_item_id = u.cart_item_id).update(
									promotion_id = promotion_id,
									quantity = u.quantity,
									item_unit_price = item_unit_price,
									item_sub_total = item_sub_total,
									item_disc_amt = disc_amt,
									item_tax  = item_tax,
									item_total = total_price,
									updated_date = today
								)
						elif u.product_type == 'ORIGINAL-ART':
							oi = Order_original_art.objects.filter(cart_item_id = u.cart_item_id).update(
									promotion_id = promotion_id,
									quantity = u.quantity,
									item_unit_price = item_unit_price,
									item_sub_total = item_sub_total,
									item_disc_amt = disc_amt,
									item_tax  = item_tax,
									item_total = total_price,
									updated_date = today
								)
					cart_sub_total = usercart.cart_sub_total - u.item_sub_total + item_sub_total
					cart_disc_amt = usercart.cart_disc_amt - u.item_disc_amt + disc_amt
					cart_tax  = usercart.cart_tax - u.item_tax + item_tax
					cart_total = usercart.cart_total - u.item_total + total_price
					c = Cart.objects.filter(cart_id = usercart.cart_id).update(
							cart_sub_total = cart_sub_total,
							cart_disc_amt = cart_disc_amt,
							cart_tax  = cart_tax,
							cart_total = cart_total,
							updated_date = today
						)
						
					if order:
						order_sub_total = order.order_sub_total - u.item_sub_total + item_sub_total,
						order_disc_amt = order.order_disc_amt - u.item_disc_amt + disc_amt,
						order_tax  = order.order_tax - u.item_tax + item_tax,
						order_total = order.order_total - u.item_total + total_price,
						o = Order.objects.filter(order_id = order.order_id).update(
								order_sub_total = order_sub_total,
								order_disc_amt = order_disc_amt,
								order_tax  = order_tax,
								order_total = order_total,
								updated_date = today
							) 
	return change_flag
	


############################################################################
## When a voucher is applied to a cart, this method calculates and updates
## the cart item sub total, discount amount, tax and item total AND
## cart sub total, tax and cart total.
## Execute this method every time a voucher is applied or there is a change
## to any of the amounts of cart item or cart
############################################################################
def update_cart_voucher_amounts(request, cart_id):
	cart = Cart.objects.get(cart_id = cart_id, cart_status = "AC")

	cart_sub_total = 0
	cart_tax = 0
	cart_total = 0
	
	######################################################################
	## Check for any voucher applied & proceed only if voucher is applied
	######################################################################
	if cart.voucher_id:
		cart_items = Cart_item_view.objects.filter(cart_id = cart_id)

		## Get taxes
		taxes = get_taxes()

		## Summation of all item sub totals (unit_price - disc_amt)
		c_sub = cart_items.aggregate(Sum('item_sub_total'))
		if c_sub['item_sub_total__sum']:
			cart_sub = c_sub['item_sub_total__sum']
		else:
			cart_sub = 0
		
		################################################################
		## For each item, we look at how much percentage of cart level
		## sub total is each item sub total and then subtract that much
		## amount from item sub total
		################################################################		
		for ci in cart_items:
			#####################################
			#         Get the item price
			#####################################
			price = get_prod_price(ci.product_id, 
					prod_type=ci.product_type_id,
					image_width=ci.image_width, image_height=ci.image_height,
					print_medium_id = ci.print_medium_id,
					acrylic_id = ci.acrylic_id,
					moulding_id = ci.moulding_id,
					mount_size = ci.mount_size,
					mount_id = ci.mount_id,
					board_id = ci.board_id,
					stretch_id = ci.stretch_id)
			total_price = price['item_price']
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

			## Get applicable tax rate
			if ci.product_type_id == 'STOCK-IMAGE':
				tax_rate = taxes['stock_image_tax_rate']
			if ci.product_type_id == 'USER-IMAGE':
				tax_rate = taxes['user_image_tax_rate']
			if ci.product_type_id == 'STOCK-COLLAGE':
				tax_rate = taxes['stock_collage_tax_rate']
			if ci.product_type_id == 'ORIGINAL-ART':
				tax_rate = taxes['original_art_tax_rate']


			# Calculate tax and sub_total
			# total price below includes the promotion discount, if any
			item_sub_total = round( (total_price*ci.quantity) / (1 + (tax_rate/100)), 2 )
			item_tax = round(total_price - item_sub_total, 2)
		
			## Get the percentage of item subtotal of cart subtotal
			voucher = Voucher.objects.get(voucher_id = cart.voucher_id)
			if voucher.discount_type == 'PERCENTAGE':
				perc = voucher.discount_value
				## Add the voucher discount 
				item_disc_amt = disc_amt + (item_sub_total * perc / 100)
				## Now apply that much percentage of voucher discount to this item
				item_sub_total = round( item_sub_total - (item_sub_total * perc / 100), 2 )				
			else:
				perc = item_sub_total * 100 / cart_sub
				## Add the voucher discount 
				item_disc_amt = disc_amt + (cart.voucher_disc_amount * perc / 100)
				## Now apply that much percentage of voucher discount to this item
				item_sub_total = round( item_sub_total - (cart.voucher_disc_amount * perc / 100), 2)
			
					
			# Calculate tax and sub_total
			item_tax = round((item_sub_total * tax_rate) / 100, 2)
			item_total = round(item_sub_total + item_tax)
			
			# Update cart item
			if ci.product_type_id == 'STOCK-IMAGE':
				c = Cart_stock_image.objects.filter(cart_item_id = ci.cart_item_id).update(
					item_sub_total = item_sub_total, item_tax = item_tax,
					item_disc_amt = item_disc_amt, item_total = item_total)
			if ci.product_type_id == 'USER-IMAGE':
				c = Cart_user_image.objects.filter(cart_item_id = ci.cart_item_id).update(
					item_sub_total = item_sub_total, item_tax = item_tax,
					item_disc_amt = item_disc_amt, item_total = item_total)
			if ci.product_type_id == 'STOCK-COLLAGE':
				c = Cart_stock_collage.objects.filter(cart_item_id = ci.cart_item_id).update(
					item_sub_total = item_sub_total, item_tax = item_tax,
					item_disc_amt = item_disc_amt, item_total = item_total)
			if ci.product_type_id == 'ORIGINAL-ART':
				c = Cart_original_art.objects.filter(cart_item_id = ci.cart_item_id).update(
					item_sub_total = item_sub_total, item_tax = item_tax,
					item_disc_amt = item_disc_amt, item_total = item_total)

			## Cart level amounts
			cart_sub_total = cart_sub_total + item_sub_total
			cart_tax = cart_tax + item_tax
			cart_total = cart_total + item_total

		## Update cart sub total, tax and total
		c = Cart.objects.filter(cart_id = cart_id).update(
			cart_sub_total = cart_sub_total,
			cart_tax = cart_tax,
			cart_total = cart_total
			)
			
	return 
				
def get_ip_addr(request):
	ipaddr = client_ip(request)
	return ipaddr
