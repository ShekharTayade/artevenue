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
from django.db.models import F

from artevenue.models import Cart, Cart_item_view, Order, Order_stock_image, Order_user_image
from artevenue.models import Order_stock_collage, Order_original_art, Order_items_view
from artevenue.models import User_billing_address, User_shipping_address
from artevenue.models import Order_billing, Order_shipping, Shipping_cost_slabs
from artevenue.models import Country, State, City, Pin_code, Pin_city_state_country
from artevenue.models import Generate_number_by_month


env = settings.EXEC_ENV

if env == 'DEV' or env == 'TESTING':
	PAYU_BASE_URL = "https://sandboxsecure.payu.in/_payment"  # Testing
	SURL = 'http://localhost:7000/payment_done/'
	FURL = 'http://localhost:7000/payment_unsuccessful/'
	CURL = 'http://localhost:7000/payment_unsuccessful/'
	E_SURL = 'http://localhost:7000/egift_payment_done/'
	E_FURL = 'http://localhost:7000/egift_payment_unsuccessful/'
	E_CURL = 'http://localhost:7000/egift_payment_unsuccessful/'
elif env == 'PROD':
	PAYU_BASE_URL = "https://secure.payu.in/_payment "  # LIVE 
	SURL = 'https://www.artevenue.com/payment_done/'
	FURL = 'https://www.artevenue.com/payment_unsuccessful/'
	CURL = 'https://www.artevenue.com/payment_unsuccessful/'
	E_SURL = 'https://www.artevenue.com/egift_payment_done/'
	E_FURL = 'https://www.artevenue.com/egift_payment_unsuccessful/'
	E_CURL = 'https://www.artevenue.com/egift_payment_unsuccessful/'
else:
	PAYU_BASE_URL = "https://sandboxsecure.payu.in/_payment"  # Testing
	SURL = 'http://localhost:7000/payment_done/'
	FURL = 'http://localhost:7000/payment_unsuccessful/'
	CURL = 'http://localhost:7000/payment_unsuccessful/'
	E_SURL = 'http://localhost:7000/egift_payment_done/'
	E_FURL = 'http://localhost:7000/egift_payment_unsuccessful/'
	E_CURL = 'http://localhost:7000/egift_payment_unsuccessful/'
		
SERVICE_PROVIDER = 'Montage Art Private Limited'



today = datetime.datetime.today()

def checkout_step1_address(request):
	today = datetime.datetime.today()
	cart_id = request.POST.get('cart_id', '')
	sub_total = Decimal(request.POST.get('sub_total', '0'))
	tax = Decimal(request.POST.get('tax', '0'))	
	disc_amt = Decimal(request.POST.get('disc_amt', '0'))
	cart_total = Decimal(request.POST.get('cart_total', '0'))

	msg = ''

	if cart_id == '':
		return render(request, "artevenue/checkout_step1_address_new.html", {})		
	
	#############################################################
	### CREATE THE ORDER
	#############################################################
	# get cart details
	usercart = Cart.objects.filter(cart_id = cart_id, cart_status = "AC").first()
	usercart_items = Cart_item_view.objects.filter(cart_id = cart_id)

	if not usercart_items:
		return render(request, "artevenue/checkout_step1_address_new.html", {'order_total':0,
					'sub_total':sub_total, 'tax':tax})	
	
	# get shipping and billing addresses if it's a logged in user
	billing_addr = {}
	shipping_addr = {}
	
	order_id = None
	shipping_cost = 0
	
	# Check if order for cart_id is already created
	order = Order.objects.filter(cart_id = cart_id).first()

	if order :
		ord_unit_price = usercart.cart_unit_price,
		sub_total = usercart.cart_sub_total
		tax = usercart.cart_tax
		order_total = usercart.cart_total
		# to retain these from the existing order. Other fields will be
		# taken from the usercart
		shipping_method = order.shipping_method
		shipper = order.shipper
		shipping_status = order.shipping_status
		shipping_cost = order.shipping_cost

		order_items = Order_items_view.objects.filter(order = order)
		order_id = order.order_id
		order_number = order.order_number

		#ord_total = order.order_total
		#sub_total = order.sub_total
		#tax = order.tax		
		
		try:		
			# Check if product is already in the order, if not add
			for c in usercart_items:
				update_ord_itm = False
				'''
				ord_itm = order_items.filter(order_id = order.order_id,
					product_id = c.product_id,
					product_type_id = c.product_type_id,
					promotion_id = c.promotion_id,
					moulding_id = c.moulding_id,
					moulding_size = c.moulding_size,
					print_medium_id = c.print_medium_id,
					print_medium_size = c.print_medium_size,
					mount_id = c.mount_id,
					mount_size = c.mount_size,
					board_id = c.board_id,
					board_size = c.board_size,
					acrylic_id = c.acrylic_id,
					acrylic_size = c.acrylic_size,
					stretch_id = c.stretch_id,
					stretch_size = c.stretch_size,
					image_width = c.image_width,
					image_height = c.image_height
				).first()
				'''
				ord_itm = Order_items_view.objects.filter(order_id = order.order_id,
					product_id = c.product_id,
					product_type_id = c.product_type_id,
					cart_item_id = c.cart_item_id
				).first()
				
				# If same item is found, then update, else insert
				if ord_itm:
					update_ord_itm = True
					if c.product_type_id == 'STOCK-IMAGE':
						Order_stock_image.objects.filter(
							order_item_id = ord_itm.order_item_id).update(							
								#quantity = c.quantity, item_sub_total=c.item_sub_total,
								#item_disc_amt = c.item_disc_amt, item_tax = c.item_tax,
								#item_total = c.item_total
								
								promotion_id = c.promotion_id,
								quantity = c.quantity,
								item_unit_price = c.item_unit_price,
								item_sub_total = c.item_sub_total,
								item_disc_amt  = c.item_disc_amt,
								item_tax  = c.item_tax,
								item_total = c.item_total,
								moulding_id = c.moulding_id,
								moulding_size = c.moulding_size,
								print_medium_id = c.print_medium_id, 
								print_medium_size = c.print_medium_size,
								mount_id = c.mount_id,
								mount_size = c.mount_size,
								board_id = c.board_id,
								board_size = c.board_size,
								acrylic_id = c.acrylic_id,
								acrylic_size = c.acrylic_size,
								stretch_id = c.stretch_id,
								stretch_size = c.stretch_size,
								image_width = c.image_width,
								image_height = c.image_height,
								created_date = 	today,
								updated_date = today
								)
					if c.product_type_id == 'USER-IMAGE':
						Order_user_image.objects.filter(
							order_item_id = ord_itm.order_item_id).update(
								#quantity = c.quantity, item_sub_total=c.item_sub_total,
								#item_disc_amt = c.item_disc_amt, item_tax = c.item_tax,
								#item_total = c.item_total
								
								promotion_id = c.promotion_id,
								quantity = c.quantity,
								item_unit_price = c.item_unit_price,
								item_sub_total = c.item_sub_total,
								item_disc_amt  = c.item_disc_amt,
								item_tax  = c.item_tax,
								item_total = c.item_total,
								moulding_id = c.moulding_id,
								moulding_size = c.moulding_size,
								print_medium_id = c.print_medium_id, 
								print_medium_size = c.print_medium_size,
								mount_id = c.mount_id,
								mount_size = c.mount_size,
								board_id = c.board_id,
								board_size = c.board_size,
								acrylic_id = c.acrylic_id,
								acrylic_size = c.acrylic_size,
								stretch_id = c.stretch_id,
								stretch_size = c.stretch_size,
								image_width = c.image_width,
								image_height = c.image_height,
								created_date = 	today,
								updated_date = today
								)
					if c.product_type_id == 'STOCK-COLLAGE':
						Order_stock_collage.objects.filter(
							order_item_id = ord_itm.order_item_id).update(
								#quantity = c.quantity, item_sub_total=c.item_sub_total,
								#item_disc_amt = c.item_disc_amt, item_tax = c.item_tax,
								#item_total = c.item_total
								
								promotion_id = c.promotion_id,
								quantity = c.quantity,
								item_unit_price = c.item_unit_price,
								item_sub_total = c.item_sub_total,
								item_disc_amt  = c.item_disc_amt,
								item_tax  = c.item_tax,
								item_total = c.item_total,
								moulding_id = c.moulding_id,
								moulding_size = c.moulding_size,
								print_medium_id = c.print_medium_id, 
								print_medium_size = c.print_medium_size,
								mount_id = c.mount_id,
								mount_size = c.mount_size,
								board_id = c.board_id,
								board_size = c.board_size,
								acrylic_id = c.acrylic_id,
								acrylic_size = c.acrylic_size,
								stretch_id = c.stretch_id,
								stretch_size = c.stretch_size,
								image_width = c.image_width,
								image_height = c.image_height,
								created_date = 	today,
								updated_date = today
								)
					if c.product_type_id == 'ORIGINAL-ART':
						Order_original_art.objects.filter(
							order_item_id = ord_itm.order_item_id).update(
								#quantity = c.quantity, item_sub_total=c.item_sub_total,
								#item_disc_amt = c.item_disc_amt, item_tax = c.item_tax,
								#item_total = c.item_total
								promotion_id = c.promotion_id,
								quantity = c.quantity,
								item_unit_price = c.item_unit_price,
								item_sub_total = c.item_sub_total,
								item_disc_amt  = c.item_disc_amt,
								item_tax  = c.item_tax,
								item_total = c.item_total,
								moulding_id = c.moulding_id,
								moulding_size = c.moulding_size,
								print_medium_id = c.print_medium_id, 
								print_medium_size = c.print_medium_size,
								mount_id = c.mount_id,
								mount_size = c.mount_size,
								board_id = c.board_id,
								board_size = c.board_size,
								acrylic_id = c.acrylic_id,
								acrylic_size = c.acrylic_size,
								stretch_id = c.stretch_id,
								stretch_size = c.stretch_size,
								image_width = c.image_width,
								image_height = c.image_height,
								created_date = 	today,
								updated_date = today
								)
				else:
					update_ord_itm = True
					# Insert the new order item
					if c.product_type_id == 'STOCK-IMAGE' :
						new_ord_item = Order_stock_image(	
							order = order,
							cart_item_id = c.cart_item_id,
							promotion_id = c.promotion_id,
							quantity = c.quantity,
							item_unit_price = c.item_unit_price,
							item_sub_total = c.item_sub_total,
							item_disc_amt  = c.item_disc_amt,
							item_tax  = c.item_tax,
							item_total = c.item_total,
							moulding_id = c.moulding_id,
							moulding_size = c.moulding_size,
							print_medium_id = c.print_medium_id, 
							print_medium_size = c.print_medium_size,
							mount_id = c.mount_id,
							mount_size = c.mount_size,
							board_id = c.board_id,
							board_size = c.board_size,
							acrylic_id = c.acrylic_id,
							acrylic_size = c.acrylic_size,
							stretch_id = c.stretch_id,
							stretch_size = c.stretch_size,
							image_width = c.image_width,
							image_height = c.image_height,
							created_date = 	today,
							updated_date = today,
							stock_image_id = c.product_id
						)
						new_ord_item.save()

					if c.product_type_id == 'USER-IMAGE' :
						new_ord_item = Order_user_image(	
							order = order,
							cart_item_id = c.cart_item_id,
							promotion_id = c.promotion_id,
							quantity = c.quantity,
							item_unit_price = c.item_unit_price,
							item_sub_total = c.item_sub_total,
							item_disc_amt  = c.item_disc_amt,
							item_tax  = c.item_tax,
							item_total = c.item_total,
							moulding_id = c.moulding_id,
							moulding_size = c.moulding_size,
							print_medium_id = c.print_medium_id, 
							print_medium_size = c.print_medium_size,
							mount_id = c.mount_id,
							mount_size = c.mount_size,
							board_id = c.board_id,
							board_size = c.board_size,
							acrylic_id = c.acrylic_id,
							acrylic_size = c.acrylic_size,
							stretch_id = c.stretch_id,
							stretch_size = c.stretch_size,
							image_width = c.image_width,
							image_height = c.image_height,
							created_date = 	today,
							updated_date = today,
							user_image_id = c.product_id
						)
						new_ord_item.save()
					if c.product_type_id == 'STOCK-COLLAGE' :
						new_ord_item = Order_stock_collage(	
							order = order,
							cart_item_id = c.cart_item_id,
							promotion_id = c.promotion_id,
							quantity = c.quantity,
							item_unit_price = c.item_unit_price,
							item_sub_total = c.item_sub_total,
							item_disc_amt  = c.item_disc_amt,
							item_tax  = c.item_tax,
							item_total = c.item_total,
							moulding_id = c.moulding_id,
							moulding_size = c.moulding_size,
							print_medium_id = c.print_medium_id, 
							print_medium_size = c.print_medium_size,
							mount_id = c.mount_id,
							mount_size = c.mount_size,
							board_id = c.board_id,
							board_size = c.board_size,
							acrylic_id = c.acrylic_id,
							acrylic_size = c.acrylic_size,
							stretch_id = c.stretch_id,
							stretch_size = c.stretch_size,
							image_width = c.image_width,
							image_height = c.image_height,
							created_date = 	today,
							updated_date = today,
							stock_collage_id = c.product_id
						)
						new_ord_item.save()
					if c.product_type_id == 'ORIGINAL-ART' :
						new_ord_item = Order_original_art(	
							order = order,
							cart_item_id = c.cart_item_id,
							promotion_id = c.promotion_id,
							quantity = c.quantity,
							item_unit_price = c.item_unit_price,
							item_sub_total = c.item_sub_total,
							item_disc_amt  = c.item_disc_amt,
							item_tax  = c.item_tax,
							item_total = c.item_total,
							moulding_id = c.moulding_id,
							moulding_size = c.moulding_size,
							print_medium_id = c.print_medium_id, 
							print_medium_size = c.print_medium_size,
							mount_id = c.mount_id,
							mount_size = c.mount_size,
							board_id = c.board_id,
							board_size = c.board_size,
							acrylic_id = c.acrylic_id,
							acrylic_size = c.acrylic_size,
							stretch_id = c.stretch_id,
							stretch_size = c.stretch_size,
							image_width = c.image_width,
							image_height = c.image_height,
							created_date = 	today,
							updated_date = today,
							original_art_id = c.product_id
						)
						new_ord_item.save()
						
			# Update Order
			ord = Order(
				order_id = order.order_id,
				order_number = order.order_number,
				order_date = order.order_date,
				cart = usercart,
				store_id = settings.STORE_ID,
				session_id = usercart.session_id,
				user = usercart.user,
				voucher = usercart.voucher,
				voucher_disc_amount = usercart.voucher_disc_amount,
				referral = usercart.referral,
				referral_disc_amount = usercart.referral_disc_amount,					
				unit_price = usercart.cart_unit_price,
				quantity = usercart.quantity,
				sub_total = usercart.cart_sub_total,
				order_discount_amt = usercart.cart_disc_amt,
				tax = usercart.cart_tax,
				shipping_cost = order.shipping_cost,
				order_total = usercart.cart_total,
				shipping_method = order.shipping_method,
				shipper = order.shipper,		
				shipping_status = order.shipping_status,
				created_date =  order.created_date,
				updated_date =  today,
				order_status = order.order_status				
			)
			ord.save()
			
			order_id = ord.order_id
			order_number = ord.order_number				
			shipping_cost = ord.shipping_cost
			ord_unit_price = ord.unit_price,
			sub_total = ord.sub_total
			tax = ord.tax
			order_total = ord.order_total
				
		except Error as e:
			msg = 'Apologies!! Could not save your cart. Please use the "Contact Us" link at the bottom of this page and let us know. We will be glad to help you.'
		
	
	else :
		try:
			order_number = get_order_next_order_number()
			new_ord = Order(
				order_number = order_number,
				order_date = None,
				cart = usercart,
				store_id = settings.STORE_ID,
				session_id = usercart.session_id,
				user = usercart.user,
				voucher = usercart.voucher,
				voucher_disc_amount = usercart.voucher_disc_amount,
				referral = usercart.referral,
				referral_disc_amount = usercart.referral_disc_amount,
				unit_price = usercart.cart_unit_price,
				quantity = usercart.quantity,
				sub_total = usercart.cart_sub_total,
				order_discount_amt = usercart.cart_disc_amt,
				tax = usercart.cart_tax,
				shipping_cost = 0,
				order_total = usercart.cart_total,
				shipping_method = None,
				shipper = None,		
				shipping_status = None,
				created_date = today,
				updated_date =  today,
				order_status = 'PP'				
			)
			
			new_ord.save()
			order_id = new_ord.order_id
			order_number = new_ord.order_number
			shipping_cost = 0 # as it's newly created order
			ord_unit_price = new_ord.unit_price,
			sub_total = new_ord.sub_total
			tax = new_ord.tax
			order_total = new_ord.order_total

			for c in usercart_items:
				if c.product_type_id == 'STOCK-IMAGE':	
					new_ord_item = Order_stock_image(	
						order = new_ord,
						cart_item_id = c.cart_item_id,
						promotion_id = c.promotion_id,
						quantity = c.quantity,
						item_unit_price = c.item_unit_price,
						item_sub_total = c.item_sub_total,
						item_disc_amt  = c.item_disc_amt,
						item_tax  = c.item_tax,
						item_total = c.item_total,
						moulding_id = c.moulding_id,
						moulding_size = c.moulding_size,
						print_medium_id = c.print_medium_id, 
						print_medium_size = c.print_medium_size,
						mount_id = c.mount_id,
						mount_size = c.mount_size,
						board_id = c.board_id,
						board_size = c.board_size,
						acrylic_id = c.acrylic_id,
						acrylic_size = c.acrylic_size,
						stretch_id = c.stretch_id,
						stretch_size = c.stretch_size,
						image_width = c.image_width,
						image_height = c.image_height,
						created_date = 	today,
						updated_date = today,
						stock_image_id = c.product_id
					)				
				if c.product_type_id == 'USER-IMAGE':	
					new_ord_item = Order_user_image(	
						order = new_ord,
						cart_item_id = c.cart_item_id,
						promotion_id = c.promotion_id,
						quantity = c.quantity,
						item_unit_price = c.item_unit_price,
						item_sub_total = c.item_sub_total,
						item_disc_amt  = c.item_disc_amt,
						item_tax  = c.item_tax,
						item_total = c.item_total,
						moulding_id = c.moulding_id,
						moulding_size = c.moulding_size,
						print_medium_id = c.print_medium_id, 
						print_medium_size = c.print_medium_size,
						mount_id = c.mount_id,
						mount_size = c.mount_size,
						board_id = c.board_id,
						board_size = c.board_size,
						acrylic_id = c.acrylic_id,
						acrylic_size = c.acrylic_size,
						stretch_id = c.stretch_id,
						stretch_size = c.stretch_size,
						image_width = c.image_width,
						image_height = c.image_height,
						created_date = 	today,
						updated_date = today,
						user_image_id = c.product_id
					)				
				if c.product_type_id == 'STOCK-COLLAGE':	
					new_ord_item = Order_stock_collage(	
						order = new_ord,
						cart_item_id = c.cart_item_id,
						promotion_id = c.promotion_id,
						quantity = c.quantity,
						item_unit_price = c.item_unit_price,
						item_sub_total = c.item_sub_total,
						item_disc_amt  = c.item_disc_amt,
						item_tax  = c.item_tax,
						item_total = c.item_total,
						moulding_id = c.moulding_id,
						moulding_size = c.moulding_size,
						print_medium_id = c.print_medium_id, 
						print_medium_size = c.print_medium_size,
						mount_id = c.mount_id,
						mount_size = c.mount_size,
						board_id = c.board_id,
						board_size = c.board_size,
						acrylic_id = c.acrylic_id,
						acrylic_size = c.acrylic_size,
						stretch_id = c.stretch_id,
						stretch_size = c.stretch_size,
						image_width = c.image_width,
						image_height = c.image_height,
						created_date = 	today,
						updated_date = today,
						stock_collage_id = c.product_id
					)				
				if c.product_type_id == 'ORIGINAL-ART':	
					new_ord_item = Order_original_art(	
						order = new_ord,
						cart_item_id = c.cart_item_id,
						promotion_id = c.promotion_id,
						quantity = c.quantity,
						item_unit_price = c.item_unit_price,
						item_sub_total = c.item_sub_total,
						item_disc_amt  = c.item_disc_amt,
						item_tax  = c.item_tax,
						item_total = c.item_total,
						moulding_id = c.moulding_id,
						moulding_size = c.moulding_size,
						print_medium_id = c.print_medium_id, 
						print_medium_size = c.print_medium_size,
						mount_id = c.mount_id,
						mount_size = c.mount_size,
						board_id = c.board_id,
						board_size = c.board_size,
						acrylic_id = c.acrylic_id,
						acrylic_size = c.acrylic_size,
						stretch_id = c.stretch_id,
						stretch_size = c.stretch_size,
						image_width = c.image_width,
						image_height = c.image_height,
						created_date = 	today,
						updated_date = today,
						original_art_id = c.product_id
					)				

				new_ord_item.save()
				
	
		except Error as e:
			msg = 'Apologies!! Could not save your cart. Please use the "Contact Us" link at the bottom of this page and let us know. We will be glad to help you.'

	# Let's get shipping, billing addressm if exists 	
	# if it already exists, take it from Order Shipping, else get it from preferred addr, if it exists
	shipping_addr = Order_shipping.objects.filter(order = order).select_related('state', 'country').first()
	billing_addr = Order_billing.objects.filter(order = order).select_related('state', 'country').first()

	if shipping_addr is None:
		if request.user.is_authenticated:
			userObj = User.objects.get(username = request.user)
			shipping_addr = User_shipping_address.objects.filter(user = userObj).select_related('state', 'country').last()
	
	if billing_addr is None:
		if request.user.is_authenticated:
			userObj = User.objects.get(username = request.user)
			billing_addr = User_billing_address.objects.filter(user = userObj).select_related('state', 'country').last()
	
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
		
	if order:
		disc_amt = order.order_discount_amt
	else:
		disc_amt = 0
	return render(request, "artevenue/checkout_step1_address_new.html", {'order_total':order_total,
					'sub_total':sub_total, 'tax':tax,'shipping_addr':shipping_addr, 'billing_addr':billing_addr,
					'disc_amt':disc_amt, 'country_arr':country_arr, 'state_arr':state_arr,  'shipping_cost':shipping_cost,
					'city_arr':city_arr, 'pin_code_arr':pin_code_arr, 'order_number':order_number,
					'order_id':order_id,'env': env })

'''					
@csrf_exempt					
def get_addr_pin_city_state(request):

	ipin_code = request.POST.get('pin_code', None)
	
	pin_code = {}
	city = {}
	cstate = {}
	country = {}

	if ipin_code :
		pin_codeObj = Pin_code.objects.filter(pin_code = ipin_code)
		pin_code = pin_codeObj.values("pin_code").distinct()
		city = Pin_city_state_country.objects.filter(pin_code__in = pin_codeObj).values("city").distinct()
		cstate = Pin_city_state_country.objects.filter(pin_code__in = pin_codeObj).values("state").distinct()
		country = Pin_city_state_country.objects.filter(pin_code__in = pin_codeObj).values("country__country_name").distinct()
	else :
		pin_code = Pin_city_state_country.objects.values("pin_code").distinct()
		city = Pin_city_state_country.objects.values("city").distinct()
		cstate = Pin_city_state_country.objects.values("state").distinct()
		country = Pin_city_state_country.objects.values("country__country_name").distinct()

		
	return( JsonResponse({'pin_code':list(pin_code), 'city':list(city), 'cstate':list(cstate),
			'country':list(country)}, safe=False) )		


@csrf_exempt
def validate_address(request):
	ipin_code = request.POST.get('pin_code', None)
	icity = request.POST.get('city', None)
	icstate = request.POST.get('cstate', None)
	icountry = request.POST.get('country', None)

	msg = []
	err_flag = False

	if ipin_code is None or ipin_code == '':
		msg.append("Pin code cannot be empty")
		err_flag = True
	if icity is None or icity == '':
		msg.append("City cannot be empty")
		err_flag = True
	if icstate is None or icstate == '':
		msg.append("State cannot be empty")
		err_flag = True
	if icountry is None or icountry == '':
		msg.append("Country cannot be empty")
		err_flag = True
	
	q = Pin_city_state_country.objects.all()
	
	if ipin_code:
		q = q.filter(pin_code_id = ipin_code)
	if icity:
		q = q.filter(city_id = icity)
	if icstate:
		q = q.filter(state_id = icstate)
	if icity:
		cnt = Country.objects.filter(country_name = icountry).first()
		q = q.filter(country = cnt)
	
	if q is None or q.count() == 0:
		msg.append("Entered Pin code, City, State is invalid. Please correct and then proceed.")
		err_flag = True

	if not err_flag:
		msg.append("SUCCESS")
	
	return JsonResponse({'msg':msg})
'''	
	
def checkout_saveAddr_shippingMethod(request):
	today = datetime.datetime.today()
	order_id = int(request.POST.get('order_id', '0'))

	shipping_full_name = request.POST.get('shipping_full_name', '')
	shipping_phone_number = request.POST.get('shipping_phone_number', '')
	shipping_email_id = request.POST.get('shipping_email_id', '')
	shipping_company = request.POST.get('shipping_company', '')
	shipping_address_1 = request.POST.get('shipping_address_1', '')
	shipping_address_2 = request.POST.get('shipping_address_2', '')
	shipping_pin_code = request.POST.get('shipping_pin_code', '')
	shipping_city = request.POST.get('shipping_city', '')
	shipping_state = request.POST.getlist('shipping_state', [])
	shipping_country = request.POST.getlist('shipping_country', [])
	s_state = State.objects.filter(state_name = shipping_state[0]).first()
	s_country = Country.objects.filter(country_name = shipping_country[0]).first()
	
	billing_full_name = request.POST.get('billing_full_name', '')
	billing_phone_number = request.POST.get('billing_phone_number', '')
	billing_email_id = request.POST.get('billing_email_id', '')
	billing_company = request.POST.get('billing_company', '')
	billing_gst_number = request.POST.get('billing_gst_number', '')
	billing_address_1 = request.POST.get('billing_address_1', '')
	billing_address_2 = request.POST.get('billing_address_2', '')
	billing_pin_code = request.POST.get('billing_pin_code', '')
	billing_city = request.POST.get('billing_city', '')
	billing_state = request.POST.getlist('billing_state', [])
	billing_country = request.POST.getlist('billing_country', [])
	b_state = State.objects.filter(state_name = billing_state[0]).first()
	b_country = Country.objects.filter(country_name = billing_country[0]).first()
	
	err_msg = []
	if shipping_full_name == '':
		err_msg.append("Ship To name can't be blank")
	if billing_full_name == '':
		err_msg.append("Bill To name can't be blank")		
	if shipping_phone_number == '':
		err_msg.append("Ship To phone can't be blank")
	if billing_phone_number == '':
		err_msg.append("Bill To phone can't be blank")		
	if shipping_email_id == '':
		err_msg.append("Ship To email can't be blank")
	if billing_email_id == '':
		err_msg.append("Bill To email can't be blank")		
	if shipping_address_1 == '':
		err_msg.append("Enter atleast one line of Ship To street address")
	if billing_address_1 == '':
		err_msg.append("Enter atleast one line of Bill To street address")
	if shipping_city == '':
		err_msg.append("Ship To city can't be blank")
	if billing_city == '':
		err_msg.append("Bill To city can't be blank")
	if shipping_state == '':
		err_msg.append("Ship To state can't be blank")
	if billing_state == '':
		err_msg.append("Bill To state can't be blank")
	if shipping_country == '':
		err_msg.append("Ship To country can't be blank")
	if billing_country == '':
		err_msg.append("Bill To country can't be blank")


	if shipping_phone_number == '':
		err_msg.append("Shipping mobile number is required")
	if billing_phone_number == '':
		err_msg.append("Billing mobile number is required")		


	# get the order
	order = Order.objects.get(pk = order_id)
	order_number = order.order_number
	
	try:
		user = User.objects.get(username = request.user)
	except User.DoesNotExist:
		user = None
	
	try:
		# Check if the order shipping, billing record already exists
		ord_shipping = Order_shipping.objects.filter(order = order).first()
		ord_billing = Order_billing.objects.filter(order = order).first()
		
		# Save the records
		if ord_shipping:
			o = Order_shipping(
				order_shipping_id = ord_shipping.order_shipping_id,
				store = ord_shipping.store,
				order = order,
				user = user,
				shipping_address = ord_shipping.shipping_address,
				full_name = shipping_full_name,
				Company = shipping_company,
				address_1 = shipping_address_1,
				address_2 = shipping_address_2,
				land_mark = '',
				city = shipping_city,
				state = s_state,
				pin_code_id = shipping_pin_code,
				country = s_country,
				phone_number = shipping_phone_number,
				email_id = shipping_email_id,
				created_date = ord_shipping.created_date,
				updated_date =  today
			)	
			
		else :
			o = Order_shipping(
				store_id = settings.STORE_ID,
				order = order,
				user = user,
				shipping_address = None,
				full_name = shipping_full_name,
				Company = shipping_company,
				address_1 = shipping_address_1,
				address_2 = shipping_address_2,
				land_mark = '',
				city = shipping_city,
				state = s_state,
				pin_code_id = shipping_pin_code,
				country = s_country,
				phone_number = shipping_phone_number,
				email_id = shipping_email_id,
				created_date = today,
				updated_date =  today
			)	
		
		o.save()
	
		if user:		
			user_addr = User_shipping_address.objects.filter(user = user, 
				full_name = shipping_full_name, company = shipping_company,
				city = shipping_city, state = s_state, pin_code_id = shipping_pin_code)
			
			if not user_addr :
				u = User_shipping_address(
					store_id = settings.STORE_ID,
					user = user,
					full_name = shipping_full_name,
					company = shipping_company,
					address_1 = shipping_address_1,
					address_2 = shipping_address_2,
					land_mark = '',
					city = shipping_city,
					state = s_state,
					pin_code_id = shipping_pin_code,
					country = s_country,
					phone_number = shipping_phone_number,
					email_id = shipping_email_id,
					pref_addr = True,
					updated_date =  today
					)
				u.save()

		if ord_billing:
			b = Order_billing(
				order_billing_id = ord_billing.order_billing_id,
				store = ord_billing.store,
				order = order,
				user = user,
				billing_address = ord_billing.billing_address,
				full_name = billing_full_name,
				Company = billing_company,
				gst_number = billing_gst_number,
				address_1 = billing_address_1,
				address_2 = billing_address_2,
				land_mark = '',
				city = billing_city,
				state = b_state,
				pin_code_id = billing_pin_code,
				country = b_country,
				phone_number = billing_phone_number,
				email_id = billing_email_id,
				created_date = ord_billing.created_date,
				updated_date =  today
			)	
		else :
			b = Order_billing(
				store_id = settings.STORE_ID,
				order = order,
				user = user,
				billing_address = None,
				full_name = billing_full_name,
				Company = billing_company,
				gst_number = billing_gst_number,
				address_1 = billing_address_1,
				address_2 = billing_address_2,
				land_mark = '',
				city = billing_city,
				state = b_state,
				pin_code_id = billing_pin_code,
				country = b_country,
				phone_number = billing_phone_number,
				email_id = billing_email_id,
				created_date = today,
				updated_date =  today
			)	
		
		b.save()
		if user:		
			user_addr = User_billing_address.objects.filter(user = user, 
				full_name = billing_full_name, company = billing_company,
				city = billing_city, state = b_state, pin_code_id = billing_pin_code)
			
			if not user_addr :
				u = User_billing_address(
					store_id = settings.STORE_ID,
					user = user,
					full_name = billing_full_name,
					company = billing_company,
					gst_number = billing_gst_number,
					address_1 = billing_address_1,
					address_2 = billing_address_2,
					land_mark = '',
					city = billing_city,
					state = b_state,
					pin_code_id = billing_pin_code,
					country = b_country,
					phone_number = billing_phone_number,
					email_id = billing_email_id,
					pref_addr = True,
					updated_date =  today
					)
				u.save()

		
		# Get the shipping cost
		shipping_cost = get_shipping_cost_by_slab(order.order_total)
		

	except IntegrityError as e:
		err_msg.append('Apologies!! Could not save your order. Please use the "Contact Us" link at the bottom of this page and let us know. We will be glad to help you.')

	except Error as e:
		err_msg.append('Apologies!! Could not save your order. Please use the "Contact Us" link at the bottom of this page and let us know. We will be glad to help you.')

	
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

	
	# if there is any error, return to the same page
	if len(err_msg) > 0 :
		return render(request, "artevenue/checkout_step1_address_new.html", {'msg':err_msg, 'order_total':order.order_total,
						'sub_total':order.sub_total, 'tax':order.tax,'shipping_addr':o, 'billing_addr':b,  'order_shipping_cost':order.shipping_cost,
						'disc_amt':order.order_discount_amt, 'country_arr':country_arr, 'state_arr':state_arr, 
						'city_arr':city_arr, 'pin_code_arr':pin_code_arr, 'order_id':order_id, 'cart_id':order.cart_id})
	else:
		#return render(request, "artevenue/checkout_step2_shipping_method.html", { 
		return render(request, "artevenue/checkout_step2_shipping_cost_by_slab.html", { 
				'order_total':order.order_total, 'order_id': order_id, 'order_shipping_cost':order.shipping_cost,
				'sub_total':order.sub_total, 'tax':order.tax,'shipping_addr':o, 'billing_addr':b,
				'disc_amt':order.order_discount_amt, 'country_arr':country_arr, 'state_arr':state_arr, 
				'city_arr':city_arr, 'pin_code_arr':pin_code_arr, 'cart_id':order.cart_id, 'shipping_cost':shipping_cost,
				'order_number':order_number})

def checkout_step3_order_review(request):
	today = datetime.datetime.today()
	order_id = request.POST.get("order_id","")
	
	shipping_method = request.POST.get("shipping_method","")
	shipping_cost = Decimal(request.POST.get("shipping_cost","0"))
	shipper = request.POST.get("shipper","")
	
	if order_id == "":
		return render(request, "artevenue/checkout_step3_order_review.html", {'msg':'NO ORDER FOUND!!'})
	
	try:
		order = Order.objects.get(pk = order_id)
	except Order.DoesNotExist:
		return render(request, "artevenue/checkout_step3_order_review.html", {'msg':'NO ORDER FOUND!!'})

	shipping_full_name = request.POST.get('shipping_full_name', '')
	shipping_phone_number = request.POST.get('shipping_phone_number', '')
	shipping_email_id = request.POST.get('shipping_email_id', '')
	shipping_company = request.POST.get('shipping_company', '')
	shipping_address_1 = request.POST.get('shipping_address_1', '')
	shipping_address_2 = request.POST.get('shipping_address_2', '')
	shipping_pin_code = request.POST.get('shipping_pin_code', '')
	shipping_city = request.POST.get('shipping_city', '')
	shipping_state = request.POST.getlist('shipping_state', [])
	shipping_country = request.POST.getlist('shipping_country', [])
	s_state = State.objects.filter(state_name = shipping_state[0]).first()
	s_country = Country.objects.filter(country_name = shipping_country[0]).first()
	
	billing_full_name = request.POST.get('billing_full_name', '')
	billing_phone_number = request.POST.get('billing_phone_number', '')
	billing_email_id = request.POST.get('billing_email_id', '')
	billing_company = request.POST.get('billing_company', '')
	billing_gst_number = request.POST.get('billing_gst_number', '')
	billing_address_1 = request.POST.get('billing_address_1', '')
	billing_address_2 = request.POST.get('billing_address_2', '')
	billing_pin_code = request.POST.get('billing_pin_code', '')
	billing_city = request.POST.get('billing_city', '')
	billing_state = request.POST.getlist('billing_state', [])
	billing_country = request.POST.getlist('billing_country', [])
	b_state = State.objects.filter(state_name = billing_state[0]).first()
	b_country = Country.objects.filter(country_name = billing_country[0]).first()
	
	err_msg = []
	if shipping_full_name == '':
		err_msg.append("Ship To name can't be blank")
	if billing_full_name == '':
		err_msg.append("Bill To name can't be blank")		
	'''
	if shipping_phone_number == '':
		err_msg.append("Ship To phone can't be blank")
	if billing_phone_number == '':
		err_msg.append("Bill To phone can't be blank")		
	if shipping_email_id == '':
		err_msg.append("Ship To email can't be blank")
	if billing_email_id == '':
		err_msg.append("Bill To email can't be blank")
	'''
	if shipping_address_1 == '':
		err_msg.append("Enter atleast one line of Ship To street address")
	if billing_address_1 == '':
		err_msg.append("Enter atleast one line of Bill To street address")
	if shipping_city == '':
		err_msg.append("Ship To city can't be blank")
	if billing_city == '':
		err_msg.append("Bill To city can't be blank")
	if shipping_state == '':
		err_msg.append("Ship To state can't be blank")
	if billing_state == '':
		err_msg.append("Bill To state can't be blank")
	if shipping_country == '':
		err_msg.append("Ship To country can't be blank")
	if billing_country == '':
		err_msg.append("Bill To country can't be blank")


	# get the order
	##order = Order.objects.get(pk = order_id)
	order_number = order.order_number
	order_total = order.order_total
	
	try:
		user = User.objects.get(username = request.user)
	except User.DoesNotExist:
		user = None
	
	try:
		# Check if the order shipping, billing record already exists
		ord_shipping = Order_shipping.objects.filter(order = order).first()
		ord_billing = Order_billing.objects.filter(order = order).first()
		
		# Save the records
		if ord_shipping:
			o = Order_shipping(
				order_shipping_id = ord_shipping.order_shipping_id,
				store = ord_shipping.store,
				order = order,
				user = user,
				shipping_address = ord_shipping.shipping_address,
				full_name = shipping_full_name,
				Company = shipping_company,
				address_1 = shipping_address_1,
				address_2 = shipping_address_2,
				land_mark = '',
				city = shipping_city,
				state = s_state,
				pin_code_id = shipping_pin_code,
				country = s_country,
				phone_number = shipping_phone_number,
				email_id = shipping_email_id,
				created_date = ord_shipping.created_date,
				updated_date =  today
			)	
			
		else :
			o = Order_shipping(
				store_id = settings.STORE_ID,
				order = order,
				user = user,
				shipping_address = None,
				full_name = shipping_full_name,
				Company = shipping_company,
				address_1 = shipping_address_1,
				address_2 = shipping_address_2,
				land_mark = '',
				city = shipping_city,
				state = s_state,
				pin_code_id = shipping_pin_code,
				country = s_country,
				phone_number = shipping_phone_number,
				email_id = shipping_email_id,
				created_date = today,
				updated_date =  today
			)	
		
		o.save()
	
		if user:		
			user_addr = User_shipping_address.objects.filter(user = user, 
				full_name = shipping_full_name, company = shipping_company,
				city = shipping_city, state = s_state, pin_code_id = shipping_pin_code)
			
			if not user_addr :
				u = User_shipping_address(
					store_id = settings.STORE_ID,
					user = user,
					full_name = shipping_full_name,
					company = shipping_company,
					address_1 = shipping_address_1,
					address_2 = shipping_address_2,
					land_mark = '',
					city = shipping_city,
					state = s_state,
					pin_code_id = shipping_pin_code,
					country = s_country,
					phone_number = shipping_phone_number,
					email_id = shipping_email_id,
					pref_addr = True,
					updated_date =  today
					)
				u.save()

		if ord_billing:
			b = Order_billing(
				order_billing_id = ord_billing.order_billing_id,
				store = ord_billing.store,
				order = order,
				user = user,
				billing_address = ord_billing.billing_address,
				full_name = billing_full_name,
				Company = billing_company,
				gst_number = billing_gst_number,
				address_1 = billing_address_1,
				address_2 = billing_address_2,
				land_mark = '',
				city = billing_city,
				state = b_state,
				pin_code_id = billing_pin_code,
				country = b_country,
				phone_number = billing_phone_number,
				email_id = billing_email_id,
				created_date = ord_billing.created_date,
				updated_date =  today
			)	
		else :
			b = Order_billing(
				store_id = settings.STORE_ID,
				order = order,
				user = user,
				billing_address = None,
				full_name = billing_full_name,
				Company = billing_company,
				gst_number = billing_gst_number,
				address_1 = billing_address_1,
				address_2 = billing_address_2,
				land_mark = '',
				city = billing_city,
				state = b_state,
				pin_code_id = billing_pin_code,
				country = b_country,
				phone_number = billing_phone_number,
				email_id = billing_email_id,
				created_date = today,
				updated_date =  today
			)	
		
		b.save()
		if user:		
			user_addr = User_billing_address.objects.filter(user = user, 
				full_name = billing_full_name, company = billing_company,
				city = billing_city, state = b_state, pin_code_id = billing_pin_code)
			
			if not user_addr :
				u = User_billing_address(
					store_id = settings.STORE_ID,
					user = user,
					full_name = billing_full_name,
					company = billing_company,
					gst_number = billing_gst_number,
					address_1 = billing_address_1,
					address_2 = billing_address_2,
					land_mark = '',
					city = billing_city,
					state = b_state,
					pin_code_id = billing_pin_code,
					country = b_country,
					phone_number = billing_phone_number,
					email_id = billing_email_id,
					pref_addr = True,
					updated_date =  today
					)
				u.save()

		
		# Get the shipping cost
		shipping_cost = get_shipping_cost_by_slab(order.order_total)
		
		order_total = order.order_total + shipping_cost

	except IntegrityError as e:
		err_msg.append('Apologies!! Could not save your order. Please use the "Contact Us" link at the bottom of this page and let us know. We will be glad to help you.')

	except Error as e:
		err_msg.append('Apologies!! Could not save your order. Please use the "Contact Us" link at the bottom of this page and let us know. We will be glad to help you.')

	
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

	if o.phone_number is None or o.phone_number == '':
		err_msg.append("Mobile number in Shipping Address is required. Courier companies need contact number for delivering your order. Besides this, we don't share your personal information with any third parties.")
	if b.phone_number is None or b.phone_number == '':
		err_msg.append("Mobile number in BILLING ADDRESS is required. This is only used to get in touch with you regading order. As per our privacy policy, we don't share your personal information with any third parties.")

	if o.email_id is None or o.email_id == '':
		err_msg.append("Your email in Shipping Address is required. Courier companies need email for delivering your order. Besides this, we don't share your personal information with any third parties.")
	if b.email_id is None or b.email_id == '':
		err_msg.append("Your email in BILLING ADDRESS is required. This is only used to get in touch with you regading order. As per our privacy policy, we don't share your personal information with any third parties.")

	
	# if there is any error, return to the same page
	if len(err_msg) > 0 :
		return render(request, "artevenue/checkout_step1_address_new.html", {'msg':err_msg, 'order_total':order.order_total,
						'sub_total':order.sub_total, 'tax':order.tax,'shipping_addr':o, 'billing_addr':b,  'order_shipping_cost':order.shipping_cost,
						'disc_amt':order.order_discount_amt, 'country_arr':country_arr, 'state_arr':state_arr, 
						'city_arr':city_arr, 'pin_code_arr':pin_code_arr, 'order_id':order_id, 'cart_id':order.cart_id ,
						'order_number':order_number})

	## Order Review page starts....
	else:
		######## Information for Payment Gateway
		posted={}		
		##order_id = request.POST.get('order_id','')
		#for i in request.POST:
		#	posted[i]=request.POST[i]
			
		##order_id = posted['order_id']
		##order = Order.objects.get(order_id = order_id)
		
		order_billing = Order_billing.objects.get(order_id = order.order_id)
		
		posted['firstname'] = order_billing.full_name
		posted['lastname'] = order_billing.Company
		posted['amount'] = order.order_total
		posted['email'] = order_billing.email_id
		posted['phone'] = order_billing.phone_number
		posted['productinfo'] = str(order.quantity) + ' items in Order Id: ' + order_id 
		posted['surl'] = SURL
		posted['furl'] = FURL
		posted['service_provider'] = SERVICE_PROVIDER
		posted['curl'] = CURL
		posted['udf1'] = str(order.order_id) 
		posted['udf2'] = str(order.voucher_id)
		posted['udf3'] = str(order.referral_id)
		posted['udf4'] = str(order.order_discount_amt)
		posted['udf6'] = order_billing.Company




		################# ORDER REVIEW
		order_items = Order_items_view.objects.filter(order = order).first()
		usercart = Cart.objects.filter(cart_id = order.cart_id, cart_status = "AC").first()
		usercartitems = Cart_item_view.objects.select_related('product', 'promotion').filter(
				cart = usercart.cart_id, product__product_type_id = F('product_type_id')).values(
			'cart_item_id', 'product_id', 'product__publisher', 'quantity', 'item_total', 'moulding_id',
			'moulding__name', 'moulding__width_inches', 'print_medium_id', 'mount_id', 'mount__name',
			'acrylic_id', 'mount_size', 'product__name', 'image_width', 'image_height', 'stretch_id', 
			'product__thumbnail_url', 'cart_id', 'promotion__discount_value', 'promotion__discount_type', 'mount__color',
			'item_unit_price', 'item_sub_total', 'item_disc_amt', 'item_tax', 'item_total', 'product_type',
			'product__image_to_frame', 'moulding__width_inner_inches'
			).order_by('product_type')	
			
		# Update the order, for shipping
		if order :
			try:
				# Update only the order total, shipping_method(it is currently None), shipping cost and shipper(it is currently None)
				# All these have to relooked at after shipping is decided.
				# So, at the moment only shipping cost and order total is updated
				o = Order(
					order_id = order_id,
					order_number = order.order_number,
					order_date = order.order_date,
					cart = usercart,
					store_id = settings.STORE_ID,
					session_id = usercart.session_id,
					user = usercart.user,
					voucher = usercart.voucher,
					voucher_disc_amount = usercart.voucher_disc_amount,
					referral = usercart.referral,
					referral_disc_amount = usercart.referral_disc_amount,					
					unit_price = usercart.cart_unit_price,
					quantity = usercart.quantity,
					sub_total = usercart.cart_sub_total,
					order_discount_amt = usercart.cart_disc_amt,
					tax = usercart.cart_tax,
					shipping_cost = shipping_cost,
					order_total = order_total,
					shipping_method = order.shipping_method,
					shipper = order.shipper,		
					shipping_status = order.shipping_status,
					created_date = order.created_date,
					updated_date =  today,
					order_status = order.order_status	
				)	

				o.save()
				
				# also update the associated cart for the shipping cost and total cost.
				c = Cart(
					cart_id = usercart.cart_id,
					store = usercart.store,
					user_id = usercart.user_id,
					session_id = usercart.session_id,
					quantity =  usercart.quantity,
					cart_unit_price = usercart.cart_unit_price,
					cart_sub_total = usercart.cart_sub_total,
					cart_disc_amt  = usercart.cart_disc_amt,
					cart_tax  = usercart.cart_tax,
					cart_total = order_total ,
					voucher_id = usercart.voucher_id,
					voucher_disc_amount = usercart.voucher_disc_amount,
					referral = usercart.referral,
					referral_disc_amount = usercart.referral_disc_amount,					
					created_date = usercart.created_date,
					updated_date = today,
					cart_status = usercart.cart_status

				)
				c.save()			
		
			except IntegrityError as e:
				err_msg.append('Apologies!! Could not save your order. Please use the "Contact Us" and let us know. We will be glad to help you.')

			except Error as e:
				err_msg.append('Apologies!! Could not save your order. Please use the "Contact Us" and let us know. We will be glad to help you.')
		
		
		return render(request, "artevenue/checkout_step3_order_review.html", {'order':o, 'order_items':order_items, 
					'usercartitems':usercartitems, "posted":posted, 'env': env})

@csrf_exempt
def get_shipping_cost_by_slab(order_total):

	slabs = Shipping_cost_slabs.objects.filter( effective_from__lte = today, effective_to__gte = today ).order_by('slab_from')
	shipping_cost = 0
	for s in slabs :
		s_from = s.slab_from
		s_to = s.slab_to
		
		if order_total >= s_from and order_total <= s_to:
			shipping_cost = s.flat_shipping_cost
			
	return (shipping_cost)	
	

def get_other_channel_ord_next_number(channel):
	ord_no = get_order_next_order_number()
	ord_no = channel + "-" + ord_no
	
	return ord_no

def get_order_next_order_number():
	num = 0
	#Get curentyear, month in format YYYYMM
	dt = datetime.datetime.now()
	mnth = dt.strftime("%Y%m")

	# Get an suffix required 
	suffix = '-'
	
	monthyear = Generate_number_by_month.objects.filter(type='ORDER-NUMBER', month_year = mnth).first()
	if monthyear :
		num = monthyear.current_number + 1
	else :
		num = 1
		
	# Update generated number in DB
	gen_num = Generate_number_by_month(
		type = 'ORDER-NUMBER',
		description = "Billing number generation",
		month_year = mnth,
		current_number = num
		)
	
	gen_num.save()
		
	generated_num = 0
	if suffix:
		generated_num = (mnth + suffix + str(num))
	else:
		generated_num = (mnth + str(num))
	return generated_num 	
	
	
