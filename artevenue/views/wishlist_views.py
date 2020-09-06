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

from artevenue.models import Stock_image_category
from artevenue.models import Promotion, Stock_image, Product_view
from artevenue.models import Wishlist, Wishlist_item, Wishlist_stock_image, User_image 
from artevenue.models import Wishlist_user_image, Wishlist_stock_collage
from artevenue.models import Wishlist_original_art, Wishlist_item_view
from artevenue.models import User_collection, User_space

from .product_views import *
from .tax_views import *
from .cart_views import *

from django.contrib.auth.decorators import login_required

today = datetime.date.today()
ecom = get_object_or_404 (Ecom_site, store_id=settings.STORE_ID )

@csrf_protect
@csrf_exempt
def add_to_wishlist(request):
	prod_id = request.POST.get('prod_id', '')
	prod_type = request.POST.get('prod_type', '')
	qty = int(request.POST.get('qty', '0'))
	wishlist_item_flag = request.POST.get('wishlist_item_flag', 'FALSE')

	image_width = Decimal(request.POST.get('image_width', '0'))
	image_height = Decimal(request.POST.get('image_height', '0'))
	
	sqin = image_width * image_height
	rnin = (image_width + image_height) * 2
	
	moulding_id = request.POST.get('moulding_id', '')
	if moulding_id == '0' or moulding_id == 'None':
		moulding_id = None

	#moulding_size = Decimal(request.POST.get('moulding_size', '0'))
	if moulding_id:
		moulding_size = rnin
	else: 
		moulding_size = None
	print_medium_id = request.POST.get('print_medium_id', 'PAPER')
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
	if acrylic_id == '0' or acrylic_id == 'None' or acrylic_id == '':
		acrylic_id = None
	if acrylic_id:
		#acrylic_size = Decimal(request.POST.get('acrylic_size', '0'))
		acrylic_size = sqin
	else:
		acrylic_size = None
	
	board_id = request.POST.get('board_id', '')
	if board_id == '0' or board_id == 'None' or board_id == '':
		board_id = None
	if board_id:
		#board_size = Decimal(request.POST.get('board_size', '0'))
		board_size = sqin
	else:
		board_size = None

	stretch_id = request.POST.get('stretch_id', '0')
	if stretch_id == '0' or stretch_id == 'None' or stretch_id == '' :
		stretch_id = None
	if stretch_id:
		#stretch_size = Decimal(request.POST.get('stretch_size', '0'))
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
		return( JsonResponse({'msg':'Price not avaiable for this image', 'cart_qty':qty}, safe=False) )
	
	prod = None	
	user_image = None
	# Get the product
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
		return( JsonResponse({'msg':msg, 'cart_qty':qty}, safe=False) )
	except User_image.DoesNotExist:
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
	wishlist_exists = False
	userwishlist = {}
	wishlist_qty = 0
	''' Let's check if the user has a wishlist open '''

	sessionid = request.session.session_key
	if request.user.is_authenticated:
		try:
			userid = User.objects.get(username = request.user)
			userwishlist = Wishlist.objects.get(user_id = userid, wishlist_status = "AC") 
		except Wishlist.DoesNotExist:
			userwishlist = {}
			wishlist_exists = False
			
		if userwishlist:
			wishlist_exists = True
		else:
			wishlist_exists = False
	else:
		if sessionid is None:
			request.session.create()
			sessionid = request.session.session_key
			wishlist_exists = False
		 
		else:
			try:
				# Get userwishlist by session
				userwishlist = Wishlist.objects.get(session_id = sessionid, wishlist_status="AC")
			except Wishlist.DoesNotExist:
				userwishlist = {}
				wishlist_exists = False
			
			if userwishlist:
				wishlist_exists = True
			else:
				wishlist_exists = False;

	prod_exits_in_wishlist = False
	if wishlist_exists:
		wishlist_prods = {}
		
		''' Check if product or user image exists in wishlist '''
		if prod:
			## if this is from a wishilst then we only check if product id
			## exists in the cart, as other factors can be changed by user
			if wishlist_item_flag == 'TRUE':
				wishlist_prods = Wishlist_item_view.objects.filter(wishlist_id = userwishlist.wishlist_id, 
							product_id = prod_id).first()			
			else:		
				wishlist_prods = Wishlist_item_view.objects.filter(wishlist_id = userwishlist.wishlist_id, 
							product_id = prod_id, moulding_id = moulding_id,
							print_medium_id = print_medium_id, mount_id = mount_id,
							mount_size = mount_size, acrylic_id = acrylic_id,
							board_id = board_id, stretch_id = stretch_id ).first() 

		if wishlist_prods:
			
			prod_exits_in_wishlist = True
	
		try :
			if wishlist_item_flag == 'TRUE' :
				wishlist_total = Decimal(userwishlist.wishlist_total) - (wishlist_prods.item_total) + (total_price)
			else:
				wishlist_total = Decimal(userwishlist.wishlist_total) + (total_price)

			# Reclaculate tax & sub total after applying voucher
			wishlist_sub_total = round( wishlist_total / (1 + (tax_rate/100)), 2 )
			wishlist_tax = wishlist_total - wishlist_sub_total
			
			# Update cart
			if wishlist_item_flag == 'TRUE':
				wishlist_quantity =  userwishlist.quantity - (wishlist_prods.quantity) + qty
				d_amt = userwishlist.wishlist_disc_amt - wishlist_prods.item_disc_amt + disc_amt
			else:
				wishlist_quantity =  userwishlist.quantity + qty
				d_amt = userwishlist.wishlist_disc_amt + disc_amt
				
			#Update the existing wishlist
			newuserwishlist = Wishlist(
				wishlist_id = userwishlist.wishlist_id,
				store = ecom,
				session_id = sessionid,
				user = userid,
				voucher_id = userwishlist.voucher_id,
				voucher_disc_amount = userwishlist.voucher_disc_amount,
				referral = userwishlist.referral,
				referral_disc_amount = userwishlist.referral_disc_amount,
				quantity =  wishlist_quantity,
				wishlist_sub_total = wishlist_sub_total,
				wishlist_disc_amt = d_amt,
				wishlist_tax  = wishlist_tax,
				wishlist_total = wishlist_total,
				wishlist_status = userwishlist.wishlist_status,
				created_date = userwishlist.created_date,
				updated_date = today
			)

			newuserwishlist.save()
			
			''' If the product with same moulding, print_medium etc. already exists in the wishlist items, then update it, else insert new item '''
			if prod_exits_in_wishlist:
				## If it has come from the wishlist then just update the current item for same qty
				## Else update quantity and amount for current item
				if wishlist_item_flag == 'FALSE':
					iqty = wishlist_prods.quantity + qty
					s_total = wishlist_prods.item_sub_total + item_sub_total
					total = wishlist_prods.item_total + total_price
					unit = wishlist_prods.item_unit_price
					d_amt = wishlist_prods.item_disc_amt + disc_amt
					tax_amt = wishlist_prods.item_tax + item_tax
				else:
					iqty = qty
					s_total = item_sub_total
					total = total_price
					unit = item_unit_price
					d_amt = disc_amt
					tax_amt = item_tax
			
				if prod.product_type_id == 'STOCK-IMAGE':
					userwishlistitems = Wishlist_stock_image(
						wishlist_item_id = wishlist_prods.wishlist_item_id,
						wishlist = userwishlist,
						promotion = wishlist_prods.promotion,
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
						created_date = wishlist_prods.created_date,
						updated_date =  today,
						stock_image_id = prod.product_id
						
					)
				elif prod.product_type_id == 'USER-IMAGE':
					userwishlistitems = Wishlist_user_image(
						wishlist_item_id = wishlist_prods.wishlist_item_id,
						wishlist = userwishlist,
						promotion = wishlist_prods.promotion,
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
						created_date = wishlist_prods.created_date,
						updated_date =  today,
						user_image_id = prod.product_id
						
					)
				elif prod.product_type_id == 'STOCK-COLLAGE':
					userwishlistitems = Wishlist_stock_collage(
						wishlist_item_id = wishlist_prods.wishlist_item_id,
						wishlist = userwishlist,
						promotion = wishlist_prods.promotion,
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
						created_date = wishlist_prods.created_date,
						updated_date =  today,
						stock_collage_id = prod.product_id
					)
				elif prod.product_type_id == 'ORIGINAL-ART':
					userwishlistitems = Wishlist_original_art(
						wishlist_item_id = wishlist_prods.wishlist_item_id,
						wishlist = userwishlist,
						promotion = wishlist_prods.promotion,
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
						created_date = wishlist_prods.created_date,
						updated_date =  today,
						original_art_id = prod.product_id
						
					)				
				userwishlistitems.save()
			else:
				# add new product in the wishlist
				if prod:
					if prod.product_type_id == 'STOCK-IMAGE' :
						userwishlistitems = Wishlist_stock_image(
							wishlist = userwishlist,
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
						userwishlistitems = Wishlist_user_image(
							wishlist = userwishlist,
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
						userwishlistitems = Wishist_stock_collage(
							wishlist = userwishlist,
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
						userwishlistitems = Wishlist_original_art(
							wishlist = userwishlist,
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
						
				userwishlistitems.save()
				
			wishlist_qty = userwishlist.quantity + qty
				
		except IntegrityError as e:
			msg = 'Apologies!! Could not save your wishlist. Please use the "Contact Us" link at the bottom of this page and let us know. We will be glad to help you.'

		except Error as e:
			msg = 'Apologies!! Could not save your wishlist. Please use the "Contact Us" link at the bottom of this page and let us know. We will be glad to help you.'

	
	# Create a new wishlist
	else:
	
		try :

			newuserwishlist = Wishlist(
				store = ecom,
				session_id = sessionid,
				user = userid,
				voucher_id = None,
				voucher_disc_amount = 0,
				referral = None,
				referral_disc_amount = 0,
				quantity = qty,
				wishlist_sub_total = item_sub_total,
				wishlist_disc_amt = disc_amt,
				wishlist_tax  =item_tax,
				wishlist_total = total_price,
				wishlist_status = 'AC',
				created_date = today,
				updated_date = today
				
			)

			newuserwishlist.save()
			
			if prod :
				if prod.product_type_id == 'STOCK-IMAGE' :
					userwishlistitems = Wishlist_stock_image(
						wishlist = newuserwishlist,
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
					userwishlistitems = Wishlist_user_image(
						wishlist = newuserwishlist,
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
					userwishlistitems = Wishist_stock_collage(
						wishlist = newuserwishlist,
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
					userwishlistitems = Wishlist_original_art(
						wishlist = newuserwishlist,
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
					
			userwishlistitems.save()
			
			wishlist_qty = qty
			
		except IntegrityError as e:
			msg = 'Apologies!! Could not save your wishlist. Please use the "Contact Us" link at the bottom of this page and let us know. We will be glad to help you.'

		except Error as e:
			msg = 'Apologies!! Could not save your wishlist. Please use the "Contact Us" link at the bottom of this page and let us know. We will be glad to help you.'

	# Update the status of the User_image to "MTC" (Moved to Cart)
	if user_image:
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
	
	return( JsonResponse({'msg':msg, 'wishlist_qty':wishlist_qty}, safe=False) )
	

@csrf_exempt
def show_wishlist(request):
	userwishlist = {}
	userwishlistitems = {}
	shipping_cost = 0 
	user_image = None
	cart_quantity = 0
	user_collection = {}
	user_space = {}

	''' Let's check if the user has a wishlist open '''
	try:
		if request.user.is_authenticated:
			usr = User.objects.get(username = request.user)
			userwishlist = Wishlist.objects.get(user = usr, wishlist_status = "AC")
			cart_quantity = Cart.objects.filter(user = usr, cart_status = "AC").count()
			
			user_collection = User_collection.objects.filter(user = usr)
			coll_ids = user_collection.values('user_collection_id')
			user_space = User_space.objects.filter(
				user_collection_id__in = coll_ids).order_by('user_collection_id')
			
		else:
			sessionid = request.session.session_key		
			if sessionid is None:
				request.session.create()
				sessionid = request.session.session_key				
			userwishlist = Wishlist.objects.get(session_id = sessionid, wishlist_status = "AC")
			cart_quantity = Cart.objects.filter(session_id = sessionid,cart_status = "AC").count()

		userwishlistitems = Wishlist_item_view.objects.select_related('product', 'promotion').filter(
				wishlist = userwishlist.wishlist_id, product__product_type_id = F('product_type_id')).values(
			'wishlist_item_id', 'product_id', 'quantity', 'item_total', 'moulding_id',
			'moulding__name', 'moulding__width_inches', 'print_medium_id', 'mount_id', 'mount__name',
			'acrylic_id', 'mount_size', 'product__name', 'image_width', 'image_height',
			'product__thumbnail_url', 'wishlist_id', 'promotion__discount_value', 'promotion__discount_type', 'mount__color',
			'item_unit_price', 'item_sub_total', 'item_disc_amt', 'item_tax', 'item_total', 'product_type',
			'product__image_to_frame', 'product__publisher', 'product__art_width', 'product__art_height', 'product__art_medium',
			'product__art_surface', 'product__art_surface_desc', 'product__high_resolution_url',
			'user_collection_id', 'user_space_id', 'user_collection__name', 'user_space__name', 'product__description'
			).order_by('user_collection_id', 'user_space_id', 'product_type')
		

	except Wishlist.DoesNotExist:
			userwishlist = {}
	
	if request.is_ajax():

		template = "artevenue/wishlist_include_new.html"
	else :
		template = "artevenue/wishlist.html"
	
	
	total_bare = 0
	
	if userwishlist :
		total_bare = userwishlist.wishlist_total  - shipping_cost - userwishlist.voucher_disc_amount
	
	return render(request, template, {'userwishlist':userwishlist, 
		'userwishlistitems': userwishlistitems, 'total_bare':total_bare,
		'user_image':user_image, 'cart_quantity':cart_quantity, 
		'user_collection':user_collection, 'user_space':user_space})

@csrf_exempt	
def delete_wishlist_item(request):
	wishlist_item_id = request.POST.get('wishlist_item_id','')
	sub_total = request.POST.get('sub_total','')
	wishlist_total = request.POST.get('wishlist_total','')
	tax = request.POST.get('tax','')
	item_total = request.POST.get('item_total','')
	
	wishlist_item = Wishlist_item_view.objects.filter(wishlist_item_id = wishlist_item_id).first()
	
	if not wishlist_item:
		return JsonResponse({'msg':'Not wishlist items found for wishlist # ' + wishlist_item_id}, safe=False)	
	
	# Get the wishlist this item is associated with
	wishlist = Wishlist.objects.filter(wishlist_id = wishlist_item.wishlist_id, wishlist_status = "AC").first()
	
	# number of items in the wishlist
	num_wishlist_item = Wishlist_item_view.objects.filter(wishlist = wishlist).count()
	
	msg = "SUCCESS"
	
	try :
		# Delete Cart Item from respective product types
		if wishlist_item.product_type_id == 'STOCK-IMAGE':
			ci = Wishlist_stock_image.objects.get(wishlist_item_id = wishlist_item.wishlist_item_id)
		if wishlist_item.product_type_id == 'USER-IMAGE':
			ci = Wishlist_user_image.objects.get(wishlist_item_id = wishlist_item.wishlist_item_id)
		if wishlist_item.product_type_id == 'STOCK-COLLAGE':
			ci = Wishlist_stock_collage.objects.get(wishlist_item_id = wishlist_item.wishlist_item_id)
		if wishlist_item.product_type_id == 'ORIGINAL-ART':
			ci = Wishlist_original_art.objects.get(wishlist_item_id = wishlist_item.wishlist_item_id)
		ci.delete()	
		
		# If this was the last item in the wishlist then delete the item as well as wishlist
		# if there are more items in the wishlist, then update wishlist quantity and remove the item
		if num_wishlist_item == 1:
			# Delete Whishlist
			wishlist.delete()
			
		else :
			# update wishlist Qty & amounts
			c = Wishlist.objects.filter( wishlist_id = wishlist_item.wishlist_id).update(
					quantity = wishlist.quantity - wishlist_item.quantity,
					wishlist_total = wishlist.wishlist_total - wishlist_item.item_total,
					wishlist_status = wishlist.wishlist_status,
					wishlist_sub_total = wishlist.wishlist_sub_total - wishlist_item.item_sub_total,
					wishlist_disc_amt  = wishlist.wishlist_disc_amt - wishlist_item.item_disc_amt,
					wishlist_tax  = wishlist.wishlist_tax - wishlist_item.item_tax,
					created_date = wishlist.created_date,	
					updated_date = today)
						
	except wishlist.DoesNotExist:
		msg = "Wishlist does not exist"
	
	except wishlist_item.DoesNotExist:
		msg = "Wishlist item does not exist"
	
	except Error as e:
		msg = 'Apologies!! Could not save your wishlist. Please use the "Contact Us" link at the bottom of this page and let us know. We will be glad to help you.'

	
	
	return JsonResponse({'msg':msg}, safe=False)


@csrf_exempt
def move_all_items_to_cart(request, wishlist_id):

	if not wishlist_id:
		wishlist_id = request.POST.get('wishlist_id', '')
		
	if wishlist_id == '':
		return 'Invalid request'
		
	try:
		wishlist = Wishlist.objects.get(wishlist_id = wishlist_id)
	except Wishlist.DoesNotExist:
		wishlist = None
		
	if not wishlist :
		return 'Invalid request'	
	
	wishlistitems = Wishlist_item_view.objects.get(wishlist_id = wishlist_id)

	for w in wishlist:
		move_item_to_cart(request, w.wishlist_item_id)

	

@csrf_exempt
def move_item_to_cart(request, wishlist_item_id = None):
	if not wishlist_item_id:
		wishlist_item_id = request.POST.get('wishlist_item_id', '')
		
	if wishlist_item_id == '':
		return 'Invalid request'
		
	items_count = 0
	try:
		wishlistitem = Wishlist_item_view.objects.get(wishlist_item_id = wishlist_item_id)
		wishlist = Wishlist.objects.get(wishlist_id = wishlistitem.wishlist_id)
	except Wishlist_item_view.DoesNotExist:
		wishlistitem = None
		
	if not wishlistitem :
		return 'Invalid request'
	
	#from django.test.client import RequestFactory
	#request = RequestFactory().post('/')
	request.POST = request.POST.copy()
		
	request.POST['prod_id'] = wishlistitem.product_id
	request.POST['prod_type'] = wishlistitem.product_type_id
	request.POST['qty'] = '1'
	request.POST['image_width'] = wishlistitem.image_width	
	request.POST['image_height'] = wishlistitem.image_height
	request.POST['moulding_id'] = wishlistitem.moulding_id or ''
	request.POST['print_medium_id'] = wishlistitem.print_medium_id or ''
	request.POST['mount_size'] = wishlistitem.mount_size or ''
	request.POST['mount_w_left'] = ''
	request.POST['mount_w_right'] = ''
	request.POST['mount_w_top'] = ''
	request.POST['mount_w_bottom'] = ''
	request.POST['acrylic_id'] = wishlistitem.acrylic_id or ''
	request.POST['board_id'] = wishlistitem.board_id or ''
	request.POST['stretch_id'] = wishlistitem.stretch_id or ''
	
	request.POST['item_unit_price'] = wishlistitem.item_unit_price or ''
	request.POST['total_price'] = wishlistitem.item_total or ''
	request.POST['disc_amt'] = wishlistitem.item_disc_amt or ''
	request.POST['discount'] = ''
	request.POST['promotion_id'] = wishlistitem.promotion_id or ''
	
	err_flg = False
	res = json.loads( add_to_cart_new(request).content )
	
	if not res['err_flg'] :
		if wishlistitem.product_type_id == 'STOCK-IMAGE':
			w = Wishlist_stock_image.objects.filter(wishlist_item_id = wishlistitem.wishlist_item_id)
		if wishlistitem.product_type_id == 'ORIGINAL-ART':
			w = Wishlist_user_image.objects.filter(wishlist_item_id = wishlistitem.wishlist_item_id)
		if wishlistitem.product_type_id == 'USER-IMAGE':
			w = Wishlist_stock_collage.objects.filter(wishlist_item_id = wishlistitem.wishlist_item_id)
		if wishlistitem.product_type_id == 'STOCK-COLLAGE':
			w = Wishlist_original_art.objects.filter(wishlist_item_id = wishlistitem.wishlist_item_id)
		w.delete()
		
		items_count = Wishlist_item_view.objects.filter(wishlist_id = wishlistitem.wishlist_id).count()

		if items_count == 1:
			wishlist.delete()
		else:
			wl = Wishlist.objects.filter(wishlist_id = wishlistitem.wishlist_id).update(
				quantity = wishlist.quantity - wishlistitem.quantity, 
				wishlist_sub_total = wishlist.wishlist_sub_total - wishlistitem.item_sub_total,
				wishlist_tax = wishlist.wishlist_tax - wishlistitem.item_tax,
				wishlist_total = wishlist.wishlist_total - wishlistitem.item_total)
				
	else:
		err_flg = True
		
	return JsonResponse({'msg':'Item removed from your wish list', 'err_flg':err_flg}, safe=False)


@csrf_exempt
def move_all_to_cart(request, wishlist_items = None):
	if not wishlist_items:
		wishlist_items = request.POST.getlist('wishlist_items[]', [])
		
	if wishlist_items == []:
		return 'Invalid request'
		
	items_count = 0
	try:
		wishlistitems = Wishlist_item_view.objects.filter(wishlist_item_id__in = wishlist_items)
		wishlist_ids = list(Wishlist_item_view.objects.filter(wishlist_item_id__in = wishlist_items).values_list('wishlist_id', flat=True))
		wishlist = Wishlist.objects.filter(wishlist_id__in = wishlist_ids)
		items_count = Wishlist_item_view.objects.filter(wishlist_id__in = wishlist_ids).count()
	except Wishlist_item_view.DoesNotExist:
		wishlistitems = None
		
	if not wishlistitems :
		return 'Invalid request'
	
	for wi in wishlistitems:
		request.POST = request.POST.copy()
		
		request.POST['prod_id'] = wi.product_id
		request.POST['prod_type'] = wi.product_type_id
		request.POST['qty'] = '1'
		request.POST['image_width'] = wi.image_width	
		request.POST['image_height'] = wi.image_height
		request.POST['moulding_id'] = wi.moulding_id or ''
		request.POST['print_medium_id'] = wi.print_medium_id or ''
		request.POST['mount_size'] = wi.mount_size or ''
		request.POST['mount_w_left'] = ''
		request.POST['mount_w_right'] = ''
		request.POST['mount_w_top'] = ''
		request.POST['mount_w_bottom'] = ''
		request.POST['acrylic_id'] = wi.acrylic_id or ''
		request.POST['board_id'] = wi.board_id or ''
		request.POST['stretch_id'] = wi.stretch_id or ''
		
		request.POST['item_unit_price'] = wi.item_unit_price or ''
		request.POST['total_price'] = wi.item_total or ''
		request.POST['disc_amt'] = wi.item_disc_amt or ''
		request.POST['discount'] = ''
		request.POST['promotion_id'] = wi.promotion_id or ''
	
		err_flg = False
		res = json.loads( add_to_cart_new(request).content )
	
	if not res['err_flg'] :
		for wi in wishlistitems:
			if wi.product_type_id == 'STOCK-IMAGE':
				w = Wishlist_stock_image.objects.filter(wishlist_item_id = wi.wishlist_item_id)
			if wi.product_type_id == 'ORIGINAL-ART':
				w = Wishlist_user_image.objects.filter(wishlist_item_id = wi.wishlist_item_id)
			if wi.product_type_id == 'USER-IMAGE':
				w = Wishlist_stock_collage.objects.filter(wishlist_item_id = wi.wishlist_item_id)
			if wi.product_type_id == 'STOCK-COLLAGE':
				w = Wishlist_original_art.objects.filter(wishlist_item_id = wi.wishlist_item_id)
			w.delete()
		
		wishlist.delete()
				
	else:
		err_flg = True
		
	return JsonResponse({'msg':'Items removed from your wish list', 'err_flg':err_flg}, safe=False)

@login_required
def user_collection(request, user_collection_id = None):
	userwishlist = {}
	userwishlistitems = {}
	user_collection = {}
	user_space = {}

	''' Let's check if the user has a wishlist open '''
	try:
		if request.user.is_authenticated:
			usr = User.objects.get(username = request.user)
			userwishlist = Wishlist.objects.get(user = usr, wishlist_status = "AC")
			
			user_collection = User_collection.objects.filter(user = usr)
			coll_ids = user_collection.values('user_collection_id')
			user_space = User_space.objects.filter(
				user_collection_id__in = coll_ids).order_by('user_collection_id')
			
		userwishlistitems = Wishlist_item_view.objects.select_related('product', 'user_collection', 'user_space').filter(
				wishlist = userwishlist.wishlist_id, product__product_type_id = F('product_type_id'))
		user_collection = User_collection.objects.get(user_collection_id = user_collection_id)
		user_space = User_space.objects.filter(user_collection_id = user_collection_id)
	except Wishlist.DoesNotExist:
			userwishlist = {}	
	except User_collection.DoesNotExist:
		user_collection = {}
	
	return render(request, "artevenue/user_collection.html", {'userwishlist':userwishlist, 
		'userwishlistitems': userwishlistitems, 
		'user_collection':user_collection, 'user_space':user_space})


@csrf_exempt
def move_to_collection(request):
	wishlist_item_id = request.POST.get('wishlist_item_id','')
	user_collection_id = request.POST.get('user_collection_id', '')
	upd = {}
	space_name = ''

	try:
		itm = Wishlist_item_view.objects.get(
			wishlist_item_id = wishlist_item_id)
		
		if itm.product_type_id == 'STOCK-IMAGE':			
			upd = Wishlist_stock_image.objects.filter(
				wishlist_item_id = wishlist_item_id).update(
				user_collection_id = user_collection_id,
				updated_date = today)
		if itm.product_type_id == 'USER-IMAGE':			
			upd = Wishlist_user_image.objects.filter(
				wishlist_item_id = wishlist_item_id).update(
				user_collection_id = user_collection_id,
				updated_date = today)
		if itm.product_type_id == 'ORIGINAL-ART':			
			upd = Wishlist_oroginal_art.objects.filter(
				wishlist_item_id = wishlist_item_id).update(
				user_collection_id = user_collection_id,
				updated_date = today)
		if itm.product_type_id == 'STOCK-COLLAGE':			
			upd = Wishlist_stock_collage.objects.filter(
				wishlist_item_id = wishlist_item_id).update(
				user_collection_id = user_collection_id,
				updated_date = today)
				
	except Wishlist_item_view.DoesNotExist:
		space_name = ''
					
	return JsonResponse({}, safe=False)


@csrf_exempt
def move_to_space(request):
	wishlist_item_id = request.POST.get('wishlist_item_id','')
	space_id = request.POST.get('space_id','')
	user_collection_id = request.POST.get('user_collection_id', '')
	upd = {}
	space_name = ''

	try:
		itm = Wishlist_item_view.objects.get(
			wishlist_item_id = wishlist_item_id)
		
		if itm.product_type_id == 'STOCK-IMAGE':			
			upd = Wishlist_stock_image.objects.filter(
				wishlist_item_id = wishlist_item_id).update(
				user_space_id = space_id, 
				user_collection_id = user_collection_id,
				updated_date = today)
		if itm.product_type_id == 'USER-IMAGE':			
			upd = Wishlist_user_image.objects.filter(
				wishlist_item_id = wishlist_item_id).update(
				user_space_id = space_id, 
				user_collection_id = user_collection_id,
				updated_date = today)
		if itm.product_type_id == 'ORIGINAL-ART':			
			upd = Wishlist_oroginal_art.objects.filter(
				wishlist_item_id = wishlist_item_id).update(
				user_space_id = space_id, 
				user_collection_id = user_collection_id,
				updated_date = today)
		if itm.product_type_id == 'STOCK-COLLAGE':			
			upd = Wishlist_stock_collage.objects.filter(
				wishlist_item_id = wishlist_item_id).update(
				user_space_id = space_id, 
				user_collection_id = user_collection_id,
				updated_date = today)

		if upd > 0 :
			obj = User_space.objects.get(user_space_id = space_id)
			if obj:
				space_name = obj.name
				
	except Wishlist_item_view.DoesNotExist:
		space_name = ''
					
	return JsonResponse({'space_name':space_name}, safe=False)


@csrf_exempt
def remove_from_collection(request):
	wishlist_item_id = int(request.POST.get('wishlist_item_id','0'))
	user_collection_id = int(request.POST.get('user_collection_id', '0'))

	try:
		itm = Wishlist_item_view.objects.get(
			wishlist_item_id = wishlist_item_id)
		
		if itm.product_type_id == 'STOCK-IMAGE':			
			upd = Wishlist_stock_image.objects.filter(
				wishlist_item_id = wishlist_item_id).update(
				user_collection_id = None, updated_date = today )
		if itm.product_type_id == 'USER-IMAGE':			
			upd = Wishlist_user_image.objects.filter(
				wishlist_item_id = wishlist_item_id).update(
				user_collection_id = None, updated_date = today )
		if itm.product_type_id == 'ORIGINAL-ART':			
			upd = Wishlist_oroginal_art.objects.filter(
				wishlist_item_id = wishlist_item_id).update(
				user_collection_id = None, updated_date = today )
		if itm.product_type_id == 'STOCK-COLLAGE':			
			upd = Wishlist_stock_collage.objects.filter(
				wishlist_item_id = wishlist_item_id).update(
				user_collection_id = None, updated_date = today )
				
	except Wishlist_item_view.DoesNotExist:
		space_name = ''
					
	return JsonResponse({}, safe=False)

@csrf_exempt
def remove_from_space(request):
	wishlist_item_id = int(request.POST.get('wishlist_item_id','0'))
	user_collection_id = int(request.POST.get('user_collection_id','0'))

	try:
		itm = Wishlist_item_view.objects.get(
			wishlist_item_id = wishlist_item_id)
		
		if itm.product_type_id == 'STOCK-IMAGE':			
			upd = Wishlist_stock_image.objects.filter(
				wishlist_item_id = wishlist_item_id).update(
				user_collection_id = None, user_space_id = None, updated_date = today )
		if itm.product_type_id == 'USER-IMAGE':			
			upd = Wishlist_user_image.objects.filter(
				wishlist_item_id = wishlist_item_id).update(
				user_collection_id = None, user_space_id = None, updated_date = today )
		if itm.product_type_id == 'ORIGINAL-ART':			
			upd = Wishlist_oroginal_art.objects.filter(
				wishlist_item_id = wishlist_item_id).update(
				user_collection_id = None, user_space_id = None, updated_date = today )
		if itm.product_type_id == 'STOCK-COLLAGE':			
			upd = Wishlist_stock_collage.objects.filter(
				wishlist_item_id = wishlist_item_id).update(
				user_collection_id = None, user_space_id = None, updated_date = today )
				
	except Wishlist_item_view.DoesNotExist:
		space_name = ''
					
	return JsonResponse({}, safe=False)


@csrf_exempt
def create_collection(request):
	collection_name = request.POST.get('collection_name', '')
	if collection_name == '':
		return JsonResponse({'collection_name':''}, safe=False)

	if request.user.is_authenticated:
		user = User.objects.get(username = request.user)
	else:
		user = {}
	
	if not user:
		return JsonResponse({'collection_name':''}, safe=False)
		
	uc = User_collection(
		name = collection_name,
		user = user)
	uc.save()
	return JsonResponse({'collection_name':collection_name,
		'collection_id':uc.user_collection_id}, safe=False)


@csrf_exempt
def create_space(request):
	collection_id = int(request.POST.get('collection_id', '0'))
	space_name = request.POST.get('space_name', '')
	if collection_id == '0':
		return JsonResponse({'space_name':''}, safe=False)
	if space_name == '':
		return JsonResponse({'space_name':''}, safe=False)

	if request.user.is_authenticated:
		user = User.objects.get(username = request.user)
	else:
		user = {}
	
	if not user:
		return JsonResponse({'space_name':''}, safe=False)
		
	us = User_space(
		user_collection_id = collection_id,
		name = space_name)
	us.save()
	return JsonResponse({'space_name':space_name,
		'collection_id':collection_id,
		'space_id':us.user_space_id}, safe=False)

@csrf_exempt
def remove_collection(request):
	wishlist_item_id = request.POST.get('wishlist_item_id', '')
	collection_id = request.POST.get('collection_id', '')
	if collection_id == '':
		return JsonResponse({'collection_id':''}, safe=False)

	itm = Wishlist_item_view.objects.filter(
		user_collection_id = collection_id)
	
	for i in itm:
		if i.product_type_id == 'STOCK-IMAGE':			
			upd = Wishlist_stock_image.objects.filter(
				wishlist_item_id = i.wishlist_item_id).update(
				user_collection_id = None, user_space_id = None, updated_date = today )
		if i.product_type_id == 'USER-IMAGE':			
			upd = Wishlist_user_image.objects.filter(
				wishlist_item_id = i.wishlist_item_id).update(
				user_collection_id = None, user_space_id = None, updated_date = today )
		if i.product_type_id == 'ORIGINAL-ART':			
			upd = Wishlist_oroginal_art.objects.filter(
				wishlist_item_id = i.wishlist_item_id).update(
				user_collection_id = None, user_space_id = None, updated_date = today )
		if i.product_type_id == 'STOCK-COLLAGE':			
			upd = Wishlist_stock_collage.objects.filter(
				wishlist_item_id = i.wishlist_item_id).update(
				user_collection_id = None, user_space_id = None, updated_date = today )

	uc = User_collection.objects.filter(user_collection_id = collection_id).delete()
				
	return JsonResponse({'collection_id':collection_id}, safe=False)
	

@csrf_exempt
def remove_space(request):
	wishlist_item_id = request.POST.get('wishlist_item_id', '')
	space_id = request.POST.get('space_id', '')
	
	if space_id == '':
		return JsonResponse({'space_id':''}, safe=False)

	itm = Wishlist_item_view.objects.filter(
		user_space_id = space_id)
	for i in itm:
		if i.product_type_id == 'STOCK-IMAGE':			
			upd = Wishlist_stock_image.objects.filter(
				wishlist_item_id = i.wishlist_item_id).update(
				user_collection_id = None, user_space_id = None, updated_date = today )
		if i.product_type_id == 'USER-IMAGE':			
			upd = Wishlist_user_image.objects.filter(
				wishlist_item_id = i.wishlist_item_id).update(
				user_collection_id = None, user_space_id = None, updated_date = today )
		if i.product_type_id == 'ORIGINAL-ART':			
			upd = Wishlist_oroginal_art.objects.filter(
				wishlist_item_id = i.wishlist_item_id).update(
				user_collection_id = None, user_space_id = None, updated_date = today )
		if i.product_type_id == 'STOCK-COLLAGE':			
			upd = Wishlist_stock_collage.objects.filter(
				wishlist_item_id = i.wishlist_item_id).update(
				user_collection_id = None, user_space_id = None, updated_date = today )

	User_space.objects.filter(user_space_id = space_id).delete()
			

	return JsonResponse({'space_id':space_id}, safe=False)
	
		