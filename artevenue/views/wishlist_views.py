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
from artevenue.models import Promotion, Stock_image, User_image
from artevenue.models import Wishlist, Wishlist_item, Tax

from .frame_views import *
from .image_views import *
from .product_views import *
from .tax_views import *
from .user_image_views import *

today = datetime.date.today()
ecom = get_object_or_404 (Ecom_site, store_id=settings.STORE_ID )

@csrf_protect
@csrf_exempt
def add_to_wishlist(request):
	prod_id = request.POST.get('prod_id', '')
	user_image_id = request.POST.get('user_image_id', '')
	qty = int(request.POST.get('qty', '0'))

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
		#acrylic_size = Decimal(request.POST.get('acrylic_size', '0'))
		acrylic_size = sqin
	else:
		acrylic_size = None
	
	board_id = request.POST.get('board_id', '')
	if board_id == '0' or board_id == 'None':
		board_id = None
	if board_id:
		#board_size = Decimal(request.POST.get('board_size', '0'))
		board_size = sqin
	else:
		board_size = None

	stretch_id = request.POST.get('stretch_id', '0')
	if stretch_id == '0' or stretch_id == 'None':
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
	
	# Get the product or User Image
	prod = None
	user_image = None
	
	try:
		if prod_id != '':
			prod = Product.objects.get(product_id=prod_id, is_published = True)
		else :
			if request.user.is_authenticated:
				user = User.objects.get(username = request.user)
				user_image = User_image.objects.filter(user = user, status = "INI").first()
			else:
				session_id = request.session.session_key
				user_image = User_image.objects.filter(session_id = session_id, status = "INI").first()		
		
	except Product.DoesNotExist:
		msg = "Product " + prod_id + " does not exist"
		return( JsonResponse({'msg':msg, 'wishlist_qty':qty}, safe=False) )
	except User_image.DoesNotExist:
		msg = "Couldn't find the uploaded image. Pease try again."
		return( JsonResponse({'msg':msg, 'wishlist_qty':qty}, safe=False) )

		
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
	if user_image:
		promo = get_frame_promotion(moulding_id)
	#promo_id = promo['promotion_id'] ### To be taken from the input to this function, so the promo code flows here
	cash_disc = promo['cash_disc']
	percent_disc = promo['percent_disc']
	
	# get Promotion object for adding it in the wishlist item
	p_promotion = None
	f_promotion = None
	if promo :
		if prod:
			p_promotion = Promotion.objects.filter(promotion_id = promo_id).first()
		if user_image:
			promo_id = promo['promotion_id']
			f_promotion = Frame_promotion.objects.filter(promotion_id = promo_id).first()
	
	
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
			wish_exists = False
		 
		else:
			try:
				# Get userwishlist by session
				userwishlist = Wishlist.objects.get(session_id = sessionid, wishlist_status="AC")
				#wishlist.objects.filter(session_id = sessionid)[:1]
			except Wishlist.DoesNotExist:
				userwishlist = {}
				wishlist_exists = False
			
			if userwishlist:
				wishlist_exists = True
			else:
				wishlist_exists = False;

	if wishlist_exists:

		''' Check if product or user image exists in wishlist '''
		wishlist_prods = {}
		wishlist_user_images = {}
		if prod:
			wishlist_prods = Wishlist_item.objects.filter(wishlist_id = userwishlist.wishlist_id, 
						product_id = prod_id, moulding_id = moulding_id,
						print_medium_id = print_medium_id, mount_id = mount_id,
						mount_size = mount_size, acrylic_id = acrylic_id,
						board_id = board_id, stretch_id = stretch_id ).first()
		if user_image:
			wishlist_user_images = Wishlist_item.objects.filter(wishlist_id = userwishlist.wishlist_id, 
						user_image_id = user_image_id, moulding_id = moulding_id,
						print_medium_id = print_medium_id, mount_id = mount_id,
						mount_size = mount_size, acrylic_id = acrylic_id,
						board_id = board_id, stretch_id = stretch_id ).first()
		

		prod_exits_in_wishlist = False 

		if wishlist_prods or wishlist_user_images:
			
			prod_exits_in_wishlist = True
	
		try :
			
			#Update the existing wishlist
			newuserwishlist = Wishlist(
				wishlist_id = userwishlist.wishlist_id,
				store = ecom,
				user = userid,
				wishlist_sub_total = userwishlist.wishlist_sub_total + item_sub_total,
				wishlist_disc_amt = userwishlist.wishlist_disc_amt + disc_amt,
				wishlist_tax  = userwishlist.wishlist_tax + item_tax,
				wishlist_total = Decimal(userwishlist.wishlist_total) + (total_price),
				session_id = sessionid,
				quantity =  userwishlist.quantity + qty,
				voucher_id = userwishlist.voucher_id,
				voucher_disc_amount = userwishlist.voucher_disc_amount,
				updated_date = today,
				wishlist_status = userwishlist.wishlist_status
			)

			newuserwishlist.save()
			
			''' If the product with same moulding, print_medium etc. already exists in the wishlist items, then update it, else insert new item '''
			if prod_exits_in_wishlist:
				userwishlistitems = Wishlist_item(
					wishlist_item_id = wishlist_prods.wishlist_item_id,
					wishlist = userwishlist,
					product_id = wishlist_prods.product_id,
					user_image = wishlist_prods.user_image,
					promotion = wishlist_prods.promotion,
					frame_promotion = wishlist_prods.frame_promotion,
					quantity = wishlist_prods.quantity + qty,
					item_unit_price = item_unit_price,
					item_sub_total = wishlist_prods.item_sub_total + item_sub_total,
					item_disc_amt = wishlist_prods.item_disc_amt + disc_amt,
					item_tax  = wishlist_prods.item_tax + item_tax,
					item_total = wishlist_prods.item_total + total_price,
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
				userwishlistitems.save()
			else:
				# add new product in the wishlist
				if prod:
					userwishlistitems = Wishlist_item(
						wishlist = userwishlist,
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
					userwishlistitems = Wishlist_item(
						wishlist = userwishlist,
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
				user = userid,
				session_id = sessionid,
				quantity =  qty,
				wishlist_sub_total = item_sub_total,
				wishlist_disc_amt = disc_amt,
				wishlist_tax  = item_tax,
				wishlist_total = total_price,
				updated_date = today,
				wishlist_status = 'AC'		
			)

			newuserwishlist.save()
			
			if prod :
				userwishlistitems = Wishlist_item(
					wishlist = newuserwishlist,
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
				userwishlistitems = Wishlist_item(
					wishlist = newuserwishlist,
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
			
			userwishlistitems.save()

			wishlist_qty = qty
			
		except IntegrityError as e:
			msg = 'Apologies!! Could not save your wishlist. Please use the "Contact Us" link at the bottom of this page and let us know. We will be glad to help you.'

		except Error as e:
			msg = 'Apologies!! Could not save your wishlist. Please use the "Contact Us" link at the bottom of this page and let us know. We will be glad to help you.'

	# Update the status of the User_image to "MTC" (Moved to Wishlist)
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
	''' Let's check if the user has a wishlist open '''
	try:
		if request.user.is_authenticated:
			usr = User.objects.get(username = request.user)
			userwishlist = Wishlist.objects.get(user = usr, wishlist_status = "AC")
		else:
			sessionid = request.session.session_key		
			if sessionid is None:
				request.session.create()
				sessionid = request.session.session_key
				
			userwishlist = Wishlist.objects.get(session_id = sessionid, wishlist_status = "AC")

		userwishlistitems = Wishlist_item.objects.select_related('product', 'promotion').filter(wishlist = userwishlist.wishlist_id,
			product__product_image__image_type='THUMBNAIL').values(
			'wishlist_item_id', 'product_id', 'quantity', 'item_total', 'moulding_id',
			'moulding__name', 'moulding__width_inches', 'print_medium_id', 'mount_id', 'mount__name',
			'acrylic_id', 'mount_size', 'product__name', 'image_width', 'image_height',
			'product__product_image__url', 'wishlist_id', 'promotion__discount_value', 'promotion__discount_type', 'mount__color',
			'item_unit_price', 'item_sub_total', 'item_disc_amt', 'item_tax', 'item_total'
			)
		
		# Let's get the user uploaded images, if any
		user_image = Wishlist_item.objects.select_related('user_image', 'frame_promotion').filter(
			wishlist = userwishlist.wishlist_id, product__isnull = True).values(
			'wishlist_item_id', 'user_image_id', 'user_image__image_to_frame', 'quantity', 'item_total', 'moulding_id',
			'moulding__name', 'moulding__width_inches', 'print_medium_id', 'mount_id', 'mount__name',
			'acrylic_id', 'mount_size', 'product__name', 'image_width', 'image_height',
			'product__product_image__url', 'wishlist_id', 'promotion__discount_value', 'promotion__discount_type', 'mount__color',
			'item_unit_price', 'item_sub_total', 'item_disc_amt', 'item_tax', 'item_total'
			)
		
			
	except Wishlist.DoesNotExist:
			userwishlist = {}

	## Get Tax rates
	taxes = get_taxes()
	image_tax_rate = taxes['image_tax_rate']
	oth_tax_rate = taxes ['oth_tax_rate']


	
	if request.is_ajax():

		template = "artevenue/wishlist_include.html"
	else :
		template = "artevenue/wishlist.html"
	
	
	total_bare = 0
	
	if userwishlist :
		total_bare = userwishlist.wishlist_total  - shipping_cost - userwishlist.voucher_disc_amount
	
	return render(request, template, {'userwishlist':userwishlist, 
		'userwishlistitems': userwishlistitems, 'total_bare':total_bare,
		'user_image':user_image})

@csrf_exempt	
def delete_wishlist_item(request):

	wishlist_item_id = request.POST.get('wishlist_item_id','')
	sub_total = request.POST.get('sub_total','')
	wishlist_total = request.POST.get('wishlist_total','')
	tax = request.POST.get('tax','')
	item_total = request.POST.get('item_total','')
	
	wishlist_item = Wishlist_item.objects.filter(wishlist_item_id = wishlist_item_id).first()
	
	if not wishlist_item:
		return JsonResponse({'msg':'Not wishlist items found for wishlist # ' + wishlist_item_id}, safe=False)	
	
	# Get the wishlist this item is associated with
	wishlist = Wishlist.objects.filter(wishlist_id = wishlist_item.wishlist_id, wishlist_status = "AC").first()
	
	# number of items in the wishlist
	num_wishlist_item = Wishlist_item.objects.filter(wishlist = wishlist).count()

	
	## Get Tax rates
	taxes = get_taxes()
	image_tax_rate = taxes['image_tax_rate']
	oth_tax_rate = taxes ['oth_tax_rate']
	
	net_oth_price = 0
	oth_tax = 0
	net_image_price = 0
	image_tax = 0
	
	msg = "SUCCESS"
	
	try :

		# If this was the last item in the wishlist then delete the item as well as wishlist
		# if there are more items in the wishlist, then update wishlist quantity and remove the item
		if num_wishlist_item == 1:
			# Delete Item
			wishlist_item.delete()
			wishlist.delete()
			
		else :
			# update wishlist Qty
			c = Wishlist (
				wishlist_id = wishlist_item.wishlist_id, 
				quantity = wishlist.quantity - wishlist_item.quantity,
				store_id = settings.STORE_ID,
				session_id = wishlist.session_id,
				user = wishlist.user,
				wishlist_total = wishlist.wishlist_total - wishlist_item.item_total,
				updated_date = today,
				wishlist_status = wishlist.wishlist_status,
				wishlist_sub_total = wishlist.wishlist_sub_total - wishlist_item.item_sub_total,
				wishlist_disc_amt  = wishlist.wishlist_disc_amt - wishlist_item.item_disc_amt,
				wishlist_tax  = wishlist.wishlist_tax - wishlist_item.item_tax,
				voucher_id = wishlist.voucher_id,
				voucher_disc_amount = wishlist.voucher_disc_amount,
				
			)
			c.save()
			
			wishlist_item.delete()
			
		
	except wishlist.DoesNotExist:
		msg = "Wishlist does not exist"
	
	except wishlist_item.DoesNotExist:
		msg = "Wishlist item does not exist"
	
	except Error as e:
		msg = 'Apologies!! Could not save your wishlist. Please use the "Contact Us" link at the bottom of this page and let us know. We will be glad to help you.'

	
	
	return JsonResponse({'msg':msg}, safe=False)
