from django.shortcuts import render, get_object_or_404
from django.http import HttpResponse
from django.conf import settings
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_protect, csrf_exempt
from django.db import IntegrityError, DatabaseError, Error
from django.contrib.auth.models import User

from datetime import datetime
import datetime
from decimal import Decimal
import json

from artevenue.models import Cart, Stock_image, User_image, Stock_collage, Original_art
from artevenue.models import Product_view

from .product_views import *
from .user_image_views import *
from .tax_views import *

today = datetime.date.today()
ecom = get_object_or_404 (Ecom_site, store_id=settings.STORE_ID )


@csrf_exempt
def show_cart(request):

	if request.is_ajax():

		template = "artevenue/cart_include.html"
	else :
		template = "artevenue/cart.html"
	
	return render(request, template, {})

	
	
def show_wishlist(request):

	if request.is_ajax():

		template = "artevenue/cart_include.html"
	else :
		template = "artevenue/show_wishlist.html"
	
	return render(request, template, {})

	
	
@csrf_exempt	
def sync_cart_session_user(request, sessionid):

	# Get current session id
	#sessionid = request.session.session_key
	
	if sessionid is None:
		return JsonResponse({"status":"NOCART"})
	
	try:
		# Get usercart by session and user is None
		sessioncart = Cart.objects.get(session_id = sessionid, user = None, cart_status = "AC")
	except Cart.DoesNotExist:
		return JsonResponse({"status":"NOCART"})
	
	if sessioncart:
		if request.user.is_authenticated:
			try:
			
				# Check if the user already has a cart open
				userid = User.objects.get(username = request.user)

				cart = Cart.objects.filter(user = userid, cart_status = "AC")
				# User already has a cart open, then return
				if cart:
					# Abondon the existing session cart & return back
					updcart = Cart(
						cart_id = sessioncart.cart_id,
						store = sessioncart.store,
						user_id = userid,
						cart_total = sessioncart.cart_total,
						session_id = sessioncart.session_id,
						quantity =  sessioncart.quantity,
						updated_date = sessioncart.updated_date,
						cart_status = 'AB'
					)						
					updcart.save()
					return JsonResponse({"status":"CARTOPEN"})
			
				# Update the session Carr with current user id
				updcart = Cart(
					cart_id = sessioncart.cart_id,
					store = sessioncart.store,
					user_id = userid,
					cart_total = sessioncart.cart_total,
					session_id = sessioncart.session_id,
					quantity =  sessioncart.quantity,
					updated_date = sessioncart.updated_date,
					cart_status = sessioncart.cart_status
				)						
				
				updcart.save()

			finally:
				return JsonResponse({"status":"NOUSER"})
				
			return JsonResponse({"status":"SYNCHED"})
			
		else:
			return JsonResponse({"status":"NOUSER"})
	
	return JsonResponse({"status":"NOCART"})


@csrf_protect
@csrf_exempt	
def add_to_cart(request):
	prod_id = request.POST.get('prod_id', '')
	qty = int(request.POST.get('qty', '0'))

	image_width = Decimal(request.POST.get('image_width', '0'))
	image_height = Decimal(request.POST.get('image_height', '0'))
	
	sqin = image_width * image_height
	rnin = (image_width + image_height) * 2
	
	moulding_id = request.POST.get('moulding_id', '')
	if moulding_id == '0' or moulding_id == 'None':
		moulding_id = None

	if moulding_id:
		moulding_size = rnin
	else: 
		moulding_size = None
	print_medium_id = request.POST.get('print_medium_id', '')
	print_medium_size = Decimal(request.POST.get('print_medium_size', '0'))
	mount_id = request.POST.get('mount_id', '0')
	if mount_id == '0' or mount_id == 'None':
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
	if acrylic_id == '0' or acrylic_id == 'None':
		acrylic_id = None
	if acrylic_id:
		acrylic_size = sqin
	else:
		acrylic_size = None
	
	board_id = request.POST.get('board_id', '')
	if board_id == '0' or board_id == 'None':
		board_id = None
	if board_id:
		board_size = sqin
	else:
		board_size = None

	stretch_id = request.POST.get('stretch_id', '0')
	if stretch_id == '0' or stretch_id == 'None':
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
	
	# Get the product
	prod = None	
	try:
		if prod_id != '':
			prod = Product_view.objects.get(product_id	=prod_id, is_published = True)
		
		if prod.product_type == "USER-IMAGE" or prod.product_type == "STOCK-COLLAGE":
			if request.user.is_authenticated:
				user = User.objects.get(username = request.user)
				user_image = User_image.objects.filter(user = user, status = "INI").first()
			else:
				session_id = request.session.session_key
				user_image = User_image.objects.filter(session_id = session_id, status = "INI").first()		
		
	except Product.DoesNotExist:
		msg = "Product " + prod_id + " does not exist"
		return( JsonResponse({'msg':msg, 'cart_qty':qty}, safe=False) )
	except User_image.DoesNotExist:
		msg = "Couldn't find the uploaded image. Pease try again."
		return( JsonResponse({'msg':msg, 'cart_qty':qty}, safe=False) )

		
	# TAX Calculations
	item_tax = 0
	item_sub_total = 0
	taxes = get_taxes()
	#if product exists then it's an image tax
	if prod :
		tax_rate = taxes['image_tax_rate']
	else :
		tax_rate = taxes['moulding_tax_rate']
	
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

	if cart_exists:

		''' Check if product or user image exists in cart '''
		cart_prods = {}
		cart_user_images = {}
		if prod:
			cart_prods = Cart_item.objects.filter(cart_id = usercart.cart_id, 
						product_id = prod_id, moulding_id = moulding_id,
						print_medium_id = print_medium_id, mount_id = mount_id,
						mount_size = mount_size, acrylic_id = acrylic_id,
						board_id = board_id, stretch_id = stretch_id ).first()
		if user_image:
			cart_user_images = Cart_item.objects.filter(cart_id = usercart.cart_id, 
						user_image_id = user_image_id, moulding_id = moulding_id,
						print_medium_id = print_medium_id, mount_id = mount_id,
						mount_size = mount_size, acrylic_id = acrylic_id,
						board_id = board_id, stretch_id = stretch_id ).first()
		

		prod_exits_in_cart = False 

		if cart_prods or cart_user_images:
			
			prod_exits_in_cart = True
	
		try :
			
			#Update the existing cart
			newusercart = Cart(
				cart_id = usercart.cart_id,
				store = ecom,
				user = userid,
				cart_sub_total = usercart.cart_sub_total + item_sub_total,
				cart_disc_amt = usercart.cart_disc_amt + disc_amt,
				cart_tax  = usercart.cart_tax + item_tax,
				cart_total = Decimal(usercart.cart_total) + (total_price),
				session_id = sessionid,
				quantity =  usercart.quantity + qty,
				voucher_id = usercart.voucher_id,
				voucher_disc_amount = usercart.voucher_disc_amount,
				updated_date = today,
				cart_status = usercart.cart_status
			)

			newusercart.save()
			
			''' If the product with same moulding, print_medium etc. already exists in the cart items, then update it, else insert new item '''
			if prod_exits_in_cart:
				usercartitems = Cart_item(
					cart_item_id = cart_prods.cart_item_id,
					cart = usercart,
					product_id = cart_prods.product_id,
					user_image = cart_prods.user_image,
					promotion = cart_prods.promotion,
					frame_promotion = cart_prods.frame_promotion,
					quantity = cart_prods.quantity + qty,
					item_unit_price = item_unit_price,
					item_sub_total = cart_prods.item_sub_total + item_sub_total,
					item_disc_amt = cart_prods.item_disc_amt + disc_amt,
					item_tax  = cart_prods.item_tax + item_tax,
					item_total = cart_prods.item_total + total_price,
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
					updated_date =  today
					
				)
				usercartitems.save()
			else:
				# add new product in the cart
				if prod:
					usercartitems = Cart_item(
						cart = usercart,
						product_id = prod_id,
						user_image = user_image,
						promotion = p_promotion,
						frame_promotion = f_promotion,
						quantity = qty,
						item_unit_price = item_unit_price,
						item_sub_total = item_sub_total,
						item_tax  = item_tax,
						item_disc_amt = disc_amt,
						item_total = total_price,
						print_medium_id = print_medium_id,
						print_medium_size = print_medium_size,
						moulding_id = moulding_id,
						moulding_size = moulding_size,
						mount_id = mount_id,
						mount_size = mount_size,
						acrylic_id = acrylic_id,
						acrylic_size = acrylic_size,
						stretch_id = stretch_id,
						stretch_size = stretch_size,
						board_id = board_id,
						board_size = board_size,
						image_width = image_width,
						image_height = image_height,
						updated_date = today
					)
				elif user_image:
					usercartitems = Cart_item(
						cart = usercart,
						product_id = prod_id,
						user_image = user_image,
						promotion = p_promotion,
						frame_promotion = f_promotion,
						quantity = qty,
						item_unit_price = item_unit_price,
						item_sub_total = item_sub_total,
						item_tax  = item_tax,
						item_disc_amt = disc_amt,
						item_total = total_price,
						print_medium_id = print_medium_id,
						print_medium_size = print_medium_size,
						moulding_id = moulding_id,
						moulding_size = moulding_size,
						mount_id = mount_id,
						mount_size = mount_size,
						acrylic_id = acrylic_id,
						acrylic_size = acrylic_size,
						stretch_id = stretch_id,
						stretch_size = stretch_size,
						board_id = board_id,
						board_size = board_size,
						image_width = image_width,
						image_height = image_height,
						updated_date = today
					)
				
				usercartitems.save()
				
			cart_qty = usercart.quantity + qty
				
		except IntegrityError as e:
			msg = 'Apologies!! Could not save your cart. Please use the "Contact Us" link at the bottom of this page and let us know. We will be glad to help you.'

		except Error as e:
			msg = 'Apologies!! Could not save your cart. Please use the "Contact Us" link at the bottom of this page and let us know. We will be glad to help you.'
	
	# Create a new cart
	else:
	
		try :

			newusercart = Cart(
				store = ecom,
				user = userid,
				session_id = sessionid,
				quantity =  qty,
				cart_sub_total = item_sub_total,
				cart_disc_amt = disc_amt,
				cart_tax  = item_tax,
				cart_total = total_price,
				updated_date = today,
				cart_status = 'AC'		
			)

			newusercart.save()
			
			if prod :
				usercartitems = Cart_item(
					cart = newusercart,
					product = prod,
					user_image = user_image,
					promotion = p_promotion,
					frame_promotion = f_promotion,
					quantity = qty,
					item_unit_price = item_unit_price,
					item_sub_total = item_sub_total,
					item_tax  = item_tax,
					item_disc_amt = disc_amt,
					item_total = total_price,
					print_medium_id = print_medium_id,
					print_medium_size = print_medium_size,
					moulding_id = moulding_id,
					moulding_size = moulding_size,
					mount_id = mount_id,
					mount_size = mount_size,
					acrylic_id = acrylic_id,
					acrylic_size = acrylic_size,
					stretch_id = stretch_id,
					stretch_size = stretch_size,
					board_id = board_id,
					board_size = board_size,
					image_width = image_width,
					image_height = image_height,
					updated_date = today
				)
			elif user_image:
				usercartitems = Cart_item(
					cart = newusercart,
					product_id = prod_id,
					user_image = user_image,
					promotion = p_promotion,
					frame_promotion = f_promotion,
					quantity = qty,
					item_unit_price = item_unit_price,
					item_sub_total = item_sub_total,
					item_tax  = item_tax,
					item_disc_amt = disc_amt,
					item_total = total_price,
					print_medium_id = print_medium_id,
					print_medium_size = print_medium_size,
					moulding_id = moulding_id,
					moulding_size = moulding_size,
					mount_id = mount_id,
					mount_size = mount_size,
					acrylic_id = acrylic_id,
					acrylic_size = acrylic_size,
					stretch_id = stretch_id,
					stretch_size = stretch_size,
					board_id = board_id,
					board_size = board_size,
					image_width = image_width,
					image_height = image_height,
					updated_date = today
				)
			
			usercartitems.save()

			cart_qty = qty
			
		except IntegrityError as e:
			msg = 'Apologies!! Could not save your cart. Please use the "Contact Us" link at the bottom of this page and let us know. We will be glad to help you.'

		except Error as e:
			msg = 'Apologies!! Could not save your cart. Please use the "Contact Us" link at the bottom of this page and let us know. We will be glad to help you.'

	# Update the status of the User_image to "MTC" (Moved to Cart)
	if prod.product_type == "USR-IMAGE":
		try: 
			u = User_image (
				id = user_image.id,
				session_id = user_image.session_id,
				user = user_image.user,
				image_to_frame = user_image.image_to_frame,
				status = 'MTC',
				created_date = user_image.created_date
			)
			u.save()
		except Error as e:
			msg = 'Apologies!! We had a system issue. Please use the "Contact Us" link at the bottom of this page and let us know. We will be glad to help you.'
	
	return( JsonResponse({'msg':msg, 'cart_qty':cart_qty}, safe=False) )
		
	