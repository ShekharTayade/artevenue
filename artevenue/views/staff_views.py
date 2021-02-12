from django.shortcuts import render, get_object_or_404
from django.db.models import Count, Q, Max, Sum, F
from django.http import HttpResponse
from django.conf import settings
from django.http import JsonResponse
from django.contrib.auth.decorators import login_required
from django.contrib.admin.views.decorators import staff_member_required
from django.views.decorators.csrf import csrf_exempt
from django.db import IntegrityError, DatabaseError, Error
from django.contrib.auth.models import User
from django.core.paginator import EmptyPage, PageNotAnInteger, Paginator

from datetime import datetime, timedelta
import datetime
import csv

from artevenue.models import Order, Order_items_view
#from returns.models import Return_order

from artevenue.models import Cart, Stock_image, User_image, Stock_collage, Original_art, Cart_item
from artevenue.models import Product_view, Promotion, Order, Voucher, Voucher_user, Cart_item_view, Voucher_used

from .product_views import *
from .user_image_views import *
from .tax_views import *
from .price_views import *


env = settings.EXEC_ENV

@staff_member_required
def coupon_management(request):
	return render(request, 'artevenue/coupon_management.html')


@staff_member_required
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
		order_num = request.GET.get("order_num", "")
		cart_id = request.GET.get("cart_id", "")
		if order_num:
			order = Order.objects.filter(order_number = order_num).first()
			if order:
				cart = Cart.objects.filter(cart_id = order.cart_id).first()
			else:	
				cart = None
		elif cart_id:
			cart = Cart.objects.filter(cart_id = cart_id).first()
			order = Order.objects.filter(cart = cart).first()
		else:
			order = None
			cart = None

	coupons = Voucher.objects.filter(effective_from__lte = today,  effective_to__gte = today)
	
	cartitems = Cart_item_view.objects.select_related('product').filter(cart = cart,
				product__product_type_id = F('product_type_id') ).order_by('product_id')
	orderitems = Order_items_view.objects.select_related('product').filter(order = order,
				product__product_type_id = F('product_type_id') ).order_by('product_id')

			
	return render(request, "artevenue/apply_coupon.html",
		{ 'msg': msg, 'env': env,
		 'order': order, 'cart': cart, 'coupons': coupons,
		 'orderitems': orderitems, 'cartitems': cartitems})	

@staff_member_required	
@csrf_exempt
def after_coupon_view(request):
	cart_id = request.POST.get('cart_id', '')
	voucher_code = request.POST.get('voucher_code', '')
	voucher_use_check = request.POST.get('voucher_use_check', 'FALSE')
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
	
	