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




@staff_member_required
def order_management(request):
	return render(request, "artevenue/order_management.html")
	
				
@staff_member_required
def manage_order_details(request):
	today = datetime.datetime.today()
	msg = None

	if request.method == 'POST':		
	
		from artevenue.models import Order_sms_email, Voucher_used, Payment_details
		
		order_id = request.POST.get("order_id", "")
		process_order = request.POST.get("process_order", "")
		cancel_order = request.POST.get("cancel_order", "")

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
		
		if process_order == "PROCESS PAYMENT":
			o = Order.objects.filter(order_id = order_id).update(
				order_status = 'PC', order_date = today.date(),
				updated_date = today)
			c = Cart.objects.filter(cart_id = order.cart_id).update(cart_status = 'CO',
				updated_date = today)
			
			## Update referral records, if any
			if order.referral_disc_amount:
				if order.referral_disc_amount > 0:
					## Get referral record
					ref = Referral.objects.filter(id = order.referral_id)					
					## Check if user is a referrer or referee and update accordingly 
					for r in ref:
						if r.referred_by == order.user:
							ref_upd = Referral.objects.filter(id = order.referral_id).update(
								referred_by_claimed_date = today)
						elif r.email_id == order.user.email:
							ref_upd = Referral.objects.filter(id = order.referral_id).update(
								referee_claimed_date = today)			
			
			## Update the voucher used table, if a voucher was used
			if order.voucher_id and order.user:
				vu = Voucher_used( 
					voucher_id = order.voucher_id,
					user = order.user,
					created_date = today,
					updated_date = today
				)
				vu.save()
			

			# Update email, sms table
			o_email = Order_sms_email(
				order = order,
				customer_email_sent = False,
				factory_email_sent = False,
				customer_sms_sent = False,
				factory_sms_sent = False,
				created_date = today,	
				updated_date = today,
				customer_review_email_sent = False,
				customer_review_sms_sent = False
			)
			o_email.save()
			
			# Save the registration, subscription, payment, promotion code details 
			paymnt = Payment_details(
						first_name = order.order_billing.full_name,
						last_name = '',
						phone_number = order.order_billing.phone_number,
						email_id = order.order_billing.email_id,
						rec_id = order_id,
						payment_date = datetime.datetime.now(),
						amount = order.order_total,
						payment_txn_status = 'success',
						payment_txn_id = 'MANUAL',
						payment_txn_amount=None,
						payment_txn_posted_hash='',
						payment_txn_key='',
						payment_txn_productinfo= "Order Number " + order.order_number,
						payment_txn_email='',
						payment_txn_salt='',
						payment_firstname = '',
						payment_lastname = '',
						payment_email = '',
						payment_phone = '',
						payment_address1 = '',
						payment_address2 = '',
						payment_city = '',
						payment_state = '',
						payment_country = '',
						payment_zip_code = '',
						trn_type = 'ORD'
					)

			paymnt.save()
			msg = "PAYMENT FOR THIS ORDER IS PROCESSED"

		elif cancel_order == "CANCEL ORDER":
			o = Order.objects.filter(order_id = order_id).update(
				order_status = 'CN', 
				updated_date = today)
			c = Cart.objects.filter(cart_id = order.cart_id).update(cart_status = 'AB',
				updated_date = today)
			msg = "THIS ORDER IS CANCELLED"

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

	
	cartitems = Cart_item_view.objects.select_related('product').filter(cart = cart,
				product__product_type_id = F('product_type_id') ).order_by('product_id')
	orderitems = Order_items_view.objects.select_related('product').filter(order = order,
				product__product_type_id = F('product_type_id') ).order_by('product_id')

	mod_addr_flag = True
	ord_mod_flag = True
	if order.order_status == 'IN' or order.order_status == 'CO' or order.order_status == 'CN':
		mod_addr_flag = False
		ord_mod_flag = False
			
	return render(request, "artevenue/manage_order_details.html",
		{ 'msg': msg, 'env': env,
		 'order': order, 'cart': cart, 'mod_addr_flag': mod_addr_flag, 'ord_mod_flag': ord_mod_flag,
		 'orderitems': orderitems, 'cartitems': cartitems})	
	
@staff_member_required
def start_production(request):

	orders = Order.objects.filter(order_status = 'PC').order_by('order_date')
	orderitems = Order_items_view.objects.select_related('product').filter(order__in = orders,
				product__product_type_id = F('product_type_id'), quantity__gt = 0 ).order_by('product_id')
	
	c_ids = orderitems.values('product_id')
	collage = Collage_stock_image.objects.filter(stock_collage_id__in = c_ids).order_by('stock_collage_id')
	
	msg = ""
	return render(request, "artevenue/orders_start_production.html",
		{ 'msg': msg, 'env': env, 'ord_cnt': orders.count(),
		 'new_orders': orders, 'orderitems': orderitems, 'collage': collage})	

def set_in_production(request):
	today = datetime.datetime.today()
	sts = 'SUCCESS'
	order_id = request.GET.get('order_id', '');
	if order_id != None and order_id != '' :
		try:
			order = Order.objects.get(order_id = order_id)
		except Order.DoesNotExist:
			order = None
			sts = 'FAILURE'
		if order:
			o = Order.objects.filter(order_id = order.order_id).update(
				order_status = 'PR', updated_date =  today)
	else:
		sts = 'FAILURE'
	return JsonResponse({"status":sts})


@staff_member_required
def make_ready_for_shipping(request):

	orders = Order.objects.filter(order_status = 'PR').order_by('order_date')
	orderitems = Order_items_view.objects.select_related('product').filter(order__in = orders,
				product__product_type_id = F('product_type_id'), quantity__gt = 0 ).order_by('product_id')
	
	c_ids = orderitems.values('product_id')
	collage = Collage_stock_image.objects.filter(stock_collage_id__in = c_ids).order_by('stock_collage_id')
	
	msg = ""
	return render(request, "artevenue/make_ready_for_shipping.html",
		{ 'msg': msg, 'env': env, 'ord_cnt': orders.count(),
		 'new_orders': orders, 'orderitems': orderitems, 'collage': collage})	
		 
def set_ready_for_shipping(request):
	today = datetime.datetime.today()
	sts = 'SUCCESS'
	order_id = request.GET.get('order_id', '');
	
	if order_id != None and order_id != '' :
		try:
			order = Order.objects.get(order_id = order_id)
		except Order.DoesNotExist:
			order = None
			sts = 'FAILURE'
		if order:
			o = Order.objects.filter(order_id = order.order_id).update(
				order_status = 'SH', updated_date =  today)
				
			if order.invoice_number == '':		# If ready for shipping, generate the invoice number
				from artevenue.views.invoice_views import get_next_invoice_number
				inv_num = get_next_invoice_number()
				ord = Order.objects.filter(order_id = order.order_id).update(
					invoice_number = inv_num, invoice_date = today)
			
			# Send email to customer - Ready for shipping
			#from artevenue.views import email_sms_views
			#email_sms_views.send_ord_update_sh(order_id)
			from artevenue.models import Order_status_communication
			os = Order_status_communication.objects.filter(order_id = order.order_id).first()
			if os:
				oe = Order_status_communication.objects.filter(order_id = order.order_id).update(
					ready_to_ship_sms_sent = False,
					ready_to_ship_email_sent = False
				)

			else:
				oe = Order_status_communication(
					order_id = order.order_id,
					tracking_info_sms_sent = False,
					tracking_info_email_sent = False,
					in_production_sms_sent = False,
					in_production_email_sent = False,
					ready_to_ship_sms_sent = False,
					ready_to_ship_email_sent = False
				)
				oe.save()
	else:
		sts = 'FAILURE'
	return JsonResponse({"status":sts})

	
@staff_member_required
def order_shipping(request):
	from artevenue.models import Shipper, Shipping_method

	orders = Order.objects.filter(order_status = 'SH').order_by('order_date')
	orderitems = Order_items_view.objects.select_related('product').filter(order__in = orders,
				product__product_type_id = F('product_type_id'), quantity__gt = 0 ).order_by('product_id')
	
	c_ids = orderitems.values('product_id')
	collage = Collage_stock_image.objects.filter(stock_collage_id__in = c_ids).order_by('stock_collage_id')
	
	shippers = Shipper.objects.all().order_by('name')
	shipping_methods = Shipping_method.objects.all().order_by('name')
	
	
	msg = ""
	return render(request, "artevenue/order_shipping.html",
		{ 'msg': msg, 'env': env, 'ord_cnt': orders.count(),
		 'orders': orders, 'orderitems': orderitems, 'collage': collage,
		 'shippers': shippers, 'shipping_methods': shipping_methods})	

def make_in_transit(request):	
	today = datetime.datetime.today()
	sts = 'SUCCESS'
	order_id = request.GET.get('order_id', '');
	order_number = request.GET.get('order_number', '');
	shipper = request.GET.get('shipper', '');
	method = request.GET.get('method', '');
	track_no = request.GET.get('track_no', '');
	track_url = request.GET.get('track_url', '');
	ship_date = request.GET.get('ship_date', '');
	
	if shipper == '':
		sts = 'FAILURE'
		msg = 'Please select the shipper'
	
	if method == '':
		sts = 'FAILURE'
		msg = 'Please select the shipping method'

	if ship_date != '':
		shipDt = datetime.datetime.strptime(ship_date, "%Y-%m-%d")
	else:
		shipDt = None

	if sts == 'FAILURE':
		orders = Order.objects.filter(order_status = 'SH').order_by('order_date')
		orderitems = Order_items_view.objects.select_related('product').filter(order__in = orders,
					product__product_type_id = F('product_type_id'), quantity__gt = 0 ).order_by('product_id')
		
		c_ids = orderitems.values('product_id')
		collage = Collage_stock_image.objects.filter(stock_collage_id__in = c_ids).order_by('stock_collage_id')
		
		shippers = Shipper.objects.all().order_by('name')
		shipping_methods = Shipping_method.objects.all().order_by('name')
		return render(request, "artevenue/order_shipping.html",
			{ 'msg': msg, 'env': env, 'ord_cnt': orders.count(), 'order_number': order_number,
			 'orders': orders, 'orderitems': orderitems, 'collage': collage,
			 'shippers': shippers, 'shipping_methods': shipping_methods})	
		
	if order_id != None and order_id != '' :
		try:
			order = Order.objects.get(order_id = order_id)
		except Order.DoesNotExist:
			order = None
			sts = 'FAILURE'
		if order:
			o = Order.objects.filter(order_id = order.order_id).update(
				order_status = 'IN', shipper_id = shipper,
				shipping_method_id = method, tracking_number = track_no,
				shipment_date = shipDt, tracking_url = track_url,
				updated_date =  today)				

			## Email to customer, in case tracking number is updated			
			if track_no != '' :
				from artevenue.models import Order_status_communication
				os = Order_status_communication.objects.filter(order_id = order.order_id).first()
				if os:
					oe = Order_status_communication.objects.filter(order_id = order.order_id).update(
						tracking_info_sms_sent = False,
						tracking_info_email_sent = False
					)

				else:
					oe = Order_status_communication(
						order_id = order.order_id,
						tracking_info_sms_sent = False,
						tracking_info_email_sent = False,
						in_production_sms_sent = False,
						in_production_email_sent = False,
						ready_to_ship_sms_sent = False,
						ready_to_ship_email_sent = False
					)
					oe.save()

	else:
		sts = 'FAILURE'
	return JsonResponse({"status":sts})


def order_dashboard(request):
	today = datetime.date.today()
	filter_applied = False
	
	startDt = ''
	endDt = ''	
	page = request.POST.get('page', 1)
	
	order_number = request.POST.get('order_number', '')
	order_status = request.POST.getlist('ORDER_STATUS')

	f_new = False
	f_in_production = False
	f_ready_for_shipping = False
	f_in_transit = False
	f_delivered = False
	for o in order_status:
		if o == 'NEW':
			f_new = True
			filter_applied = True
		if o == 'IP':
			f_in_production = True
			filter_applied = True
		if o == 'RS':
			f_ready_for_shipping = True
			filter_applied = True
		if o == 'IN':
			f_in_transit = True
			filter_applied = True
		if o == 'CO':
			f_delivered = True
			filter_applied = True
			
			
	user_name = request.POST.get('user_name', '')
	user_email = request.POST.get('user_email', '')
	user_phone = request.POST.get('user_phone', '')
	printpdf = request.POST.get('printpdf', '')
	
	if printpdf == '':
		printpdf = request.POST.get('printpdf', 'NO')

	from_date = request.POST.get("fromdate", '')
	if from_date != '' :
		startDt = datetime.datetime.strptime(from_date, "%Y-%m-%d")
		filter_applied = True
		
	to_date = request.POST.get("todate", '')
	if to_date != '' :
		endDt = datetime.datetime.strptime(to_date, "%Y-%m-%d")
		filter_applied = True
		
	orders = Order.objects.exclude(order_status = 'CN').exclude(
				order_status = 'PP').order_by('-order_date')

	if order_number:
		orders = orders.filter(order_number = order_number)
		filter_applied = True
	if user_email:
		orders = orders.filter(user__email__iexact = user_email)
		filter_applied = True
	if user_phone:
		orders = orders.filter(order_billing__phone_number = user_phone)
		filter_applied = True
	if user_name:
		orders = orders.filter(order_billing__full_name__icontains = user_name)
		filter_applied = True
	if startDt:
		orders = orders.filter(order_date__gte = startDt)
		filter_applied = True
	if endDt:
		orders = orders.filter(order_date__lte = endDt)
		filter_applied = True
		
	f = Q()
	if f_new:
		f = Q(order_status = 'PC')
		#orders = orders.filter(order_status = 'PC')
	if f_in_production:	
		f = (f | Q(order_status = 'PR'))
		#orders = orders.filter(order_status = 'PR')
	if f_ready_for_shipping:
		f = (f | Q(order_status = 'SH'))
		#order = orders.filter(order_status = 'SH')
	if f_in_transit:	
		f = (f | Q(order_status = 'IN'))
		#orders = orders.filter(order_status = 'IN')
	if f_delivered:	
		f = (f | Q(order_status = 'CO'))

	#######If not filter applied, then by default shows last 1 weeks' data
	if not filter_applied:
		startDt = today - datetime.timedelta(days=7)
		orders = orders.filter(order_date__gte = startDt )
	
	orders = orders.filter(f)
		
	new = orders.filter(order_status = 'PC').count()
	in_prod = orders.filter(order_status = 'PR').count()
	ready_for_shipping = orders.filter(order_status = 'SH').count()
	in_transit = orders.filter(order_status = 'IN').count()	
	delivered = orders.filter(order_status = 'CO').count()	

	orderitems = Order_items_view.objects.select_related('product').filter(order__in = orders,
				product__product_type_id = F('product_type_id'), quantity__gt = 0 ).order_by('product_id')
	c_ids = orderitems.values('product_id')
	collage = Collage_stock_image.objects.filter(stock_collage_id__in = c_ids).order_by('stock_collage_id')

	return render(request, "artevenue/order_dashboard_details.html",
		{ 'ord_cnt': orders.count(), 'order': orders, 'order_number': order_number,
		 'orders': orders, 'orderitems': orderitems, 'collage': collage,
		 'startDt':startDt, 'endDt':endDt, 'user_email':user_email, 'user_phone':user_phone, 'user_name': user_name,
		 'new':new, 'in_prod':in_prod, 'ready_for_shipping':ready_for_shipping, 'in_transit':in_transit, 'delivered': delivered,
		'f_new': f_new, 'f_in_production' :f_in_production, 'f_ready_for_shipping' :f_ready_for_shipping,
		'f_in_transit' :f_in_transit, 'f_delivered': f_delivered, 'filter_applied' : filter_applied

		 })	

def print_pf_labels (request, order_id):
	from django.template.loader import render_to_string
	from weasyprint import HTML, CSS
	from django.core.files.storage import FileSystemStorage
	from artevenue.models import Publisher
	
	order = Order.objects.filter(order_id = order_id).first()
	orderitems = Order_items_view.objects.select_related('product').filter(order = order,
				product__product_type_id = F('product_type_id'), quantity__gt = 0 ).order_by('product_id')
	
	c_ids = orderitems.values('product_id')
	collage = Collage_stock_image.objects.filter(stock_collage_id__in = c_ids).order_by('stock_collage_id')

	publ = Publisher.objects.all()

	html_string = render_to_string('artevenue/printing_framing_label.html', {
		'order': order, 'orderitems': orderitems, 'collage': collage, 'MEDIA_URL':settings.MEDIA_URL,
		'ecom_site':ecom, 'publ': publ, 'env': env})

	html = HTML(string=html_string, base_url=request.build_absolute_uri())
	html.write_pdf(target= settings.TMP_FILES + order.order_number + '_printing_framing_label.pdf',
					presentational_hints=True);
	
	fs = FileSystemStorage(settings.TMP_FILES)
	with fs.open(order.order_number + '_printing_framing_label.pdf') as pdf:
		response = HttpResponse(pdf, content_type='application/pdf')
		response['Content-Disposition'] = 'attachment; filename="' + order.order_number + '_printing_framing_label.pdf"'
		return response	

@staff_member_required
def order_delivery(request):
	from artevenue.models import Shipper, Shipping_method

	orders = Order.objects.filter(order_status = 'IN').order_by('order_date')
	orderitems = Order_items_view.objects.select_related('product').filter(order__in = orders,
				product__product_type_id = F('product_type_id'), quantity__gt = 0 ).order_by('product_id')
	
	c_ids = orderitems.values('product_id')
	collage = Collage_stock_image.objects.filter(stock_collage_id__in = c_ids).order_by('stock_collage_id')
	
	shippers = Shipper.objects.all().order_by('name')
	shipping_methods = Shipping_method.objects.all().order_by('name')
	
	
	msg = ""
	return render(request, "artevenue/order_delivery.html",
		{ 'msg': msg, 'env': env, 'ord_cnt': orders.count(),
		 'orders': orders, 'orderitems': orderitems, 'collage': collage,
		 'shippers': shippers, 'shipping_methods': shipping_methods})	

def set_order_delivery(request):
	today = datetime.datetime.today()
	sts = 'SUCCESS'
	order_id = request.GET.get('order_id', '');
	delivery_date = request.GET.get('delivery_date', '');
	
	if delivery_date != '':
		deliveryDt = datetime.datetime.strptime(delivery_date, "%Y-%m-%d")
	else:
		deliveryDt = None


	if order_id != None and order_id != '' :
		try:
			order = Order.objects.get(order_id = order_id)
		except Order.DoesNotExist:
			order = None
			sts = 'FAILURE'
		if order:
			o = Order.objects.filter(order_id = order.order_id).update(
				order_status = 'CO', delivery_date = deliveryDt, updated_date =  today)
	else:
		sts = 'FAILURE'
	return JsonResponse({"status":sts})
	
	
@staff_member_required
def order_modification( request, order_id ):
	today = datetime.datetime.today()
	msg = None

	if order_id:
		order = Order.objects.filter(order_id = order_id).first()
		if order:
			cart = Cart.objects.filter(cart_id = order.cart_id).first()
		else:	
			cart = None
	else:
		order = None
		cart = None

	if order:
		order_items = Order_items_view.objects.select_related('product').filter(order = order,
					product__product_type_id = F('product_type_id'), quantity__gt = 0 ).order_by('product_id')
		c_ids = order_items.values('product_id')
		collage = Collage_stock_image.objects.filter(stock_collage_id__in = c_ids).order_by('stock_collage_id')
	else: 
		order_items = None
		collage = None

	return render(request, "artevenue/order_modification.html",
			{ 'msg': msg, 'env': env,
			 'order': order, 'order_items': order_items, 'collage': collage,
			 })	
			 
def order_addr_change(request, order_id=None):
	today = datetime.datetime.today()
	msg = None

	if not order_id:
		order_id = request.POST.get("order_id", "")
	
	order = Order.objects.filter(order_id = order_id).first()
		
	if order:
		order_items = Order_items_view.objects.select_related('product').filter(order = order,
					product__product_type_id = F('product_type_id'), quantity__gt = 0 ).order_by('product_id')
		c_ids = order_items.values('product_id')
		collage = Collage_stock_image.objects.filter(stock_collage_id__in = c_ids).order_by('stock_collage_id')
		
		try: 
			ord_s = order.order_shipping
		except Order_shipping.DoesNotExist:
			ord_s = None

		try: 
			ord_b = order.order_billing
		except Order_billing.DoesNotExist:
			ord_b = None
			
		if ord_s:
			ship_form = ship_addressForm(instance = order.order_shipping)
		else:
			ship_form = ship_addressForm()
		if ord_b:
			bill_form = bill_addressForm(instance = order.order_billing)
		else:
			bill_form = bill_addressForm()		
		
	else: 
		order_items = None
		collage = None
		ship_form = None
		bill_form = None

	return render(request, "artevenue/order_addr_change.html",
			{ 'msg': msg, 'env': env,
			 'order': order, 'order_items': order_items, 'collage': collage,
			 'bill_form': bill_form, 'ship_form': ship_form
			 })	
		
def order_addr_change_confirm(request, order_id=None):
	today = datetime.datetime.today()

	err_msg = []
	sts = 'SUCCESS'
	
	if not order_id :
		order_id = request.GET.get('order_id', '')
	order = Order.objects.filter(order_id = order_id).first()
	
	bill_addr_full_name = request.GET.get('bill_addr_full_name', '')
	bill_addr_company = request.GET.get('bill_addr_company', '')
	bill_addr_gst_number = request.GET.get('bill_addr_gst_number', '' )
	bill_addr_1 = request.GET.get('bill_addr_1', '' )
	bill_addr_2 = request.GET.get('bill_addr_2', '' )
	bill_addr_land_mark = request.GET.get('bill_addr_land_mark', '' )
	bill_addr_pin_code = request.GET.get('bill_addr_pin_code', '' )
	bill_addr_city = request.GET.get('bill_addr_city', '')
	bill_addr_state = request.GET.get('bill_addr_state', '')
	bill_addr_country = request.GET.get('bill_addr_country', '')
	bill_addr_phone_number = request.GET.get('bill_addr_phone_number', '')
	bill_addr_email_id = request.GET.get('bill_addr_email_id', '')
	
	ship_addr_full_name = request.GET.get('ship_addr_full_name', '')
	ship_addr_company = request.GET.get('ship_addr_company', '')
	ship_addr_gst_number = request.GET.get('ship_addr_gst_number', '' )
	ship_addr_1 = request.GET.get('ship_addr_1', '' )
	ship_addr_2 = request.GET.get('ship_addr_2', '' )
	ship_addr_land_mark = request.GET.get('ship_addr_land_mark', '' )
	ship_addr_pin_code = request.GET.get('ship_addr_pin_code', '' )
	ship_addr_city = request.GET.get('ship_addr_city', '')
	ship_addr_state = request.GET.get('ship_addr_state', '')
	ship_addr_country = request.GET.get('ship_addr_country', '')
	ship_addr_phone_number = request.GET.get('ship_addr_phone_number', '')
	ship_addr_email_id = request.GET.get('ship_addr_email_id', '')
	
	#################################
	## Billing address validation  ## 
	#################################
	if bill_addr_full_name == '':
		err_msg.append("Bill To Name can't be blank")
		sts = 'FAILURE'
	if bill_addr_1 == '':
		err_msg.append("Billing address 1st line can't be blank")
		sts = 'FAILURE'	
	if bill_addr_pin_code == '':
		err_msg.append("Billing address pin code is required")
		sts = 'FAILURE'
	else: 
		b_pin = Pin_code.objects.filter(pin_code = bill_addr_pin_code).first()
		if not b_pin:
			err_msg.append("Entered billing address pin code is not found")
			sts = 'FAILURE'			
	if bill_addr_city == '':
		err_msg.append("Billing address city is required")
		sts = 'FAILURE'
	else: 
		b_city = City.objects.filter(city__iexact = bill_addr_city).first()
		if not b_city:
			err_msg.append("Entered billing address city is not found")
			sts = 'FAILURE'
	if bill_addr_state == '':
		err_msg.append("Billing address state is required")
		sts = 'FAILURE'
	else: 
		b_state = State.objects.filter(state_name__iexact = bill_addr_state).first()
		if not b_state:
			err_msg.append("Entered billing address state is not found")
			sts = 'FAILURE'
	if bill_addr_country == '':
		err_msg.append("Billing address country is required")
		sts = 'FAILURE'
	else: 
		b_country = Country.objects.filter(country_name__iexact = bill_addr_country).first()
		if not b_country:
			err_msg.append("Entered billing address country is not found")
			sts = 'FAILURE'

	if sts != 'FAILURE':
		request.POST = {'pin_code': bill_addr_pin_code, 'city': b_city.city, 'cstate': b_state.state_name,
		'country': b_country.country_name}	
		val = validate_address(request)
		result = json.loads(val.content)	
		if 'msg' in result:
			if result['msg'] != ['SUCCESS']:
				err_msg.append(result['msg'])
				sts = 'FAILURE'	

	#################################
	## Shipping address validation ## 
	#################################
	if ship_addr_full_name == '':
		err_msg.append("Bill To Name can't be blank")
		sts = 'FAILURE'
	if ship_addr_1 == '':
		err_msg.append("Shipping address 1st line can't be blank")
		sts = 'FAILURE'	
	if ship_addr_pin_code == '':
		err_msg.append("Shipping address pin code is required")
		sts = 'FAILURE'
	else: 
		s_pin = Pin_code.objects.filter(pin_code = ship_addr_pin_code).first()
		if not s_pin:
			err_msg.append("Entered shipping address pin code is not found")
			sts = 'FAILURE'			
	if ship_addr_city == '':
		err_msg.append("Shipping address city is required")
		sts = 'FAILURE'
	else: 
		s_city = City.objects.filter(city__iexact = ship_addr_city).first()
		if not s_city:
			err_msg.append("Entered shipping address city is not found")
			sts = 'FAILURE'
	if ship_addr_state == '':
		err_msg.append("Shipping address state is required")
		sts = 'FAILURE'
	else: 
		s_state = State.objects.filter(state_name__iexact = ship_addr_state).first()
		if not s_state:
			err_msg.append("Entered shipping address state is not found")
			sts = 'FAILURE'
	if ship_addr_country == '':
		err_msg.append("Shipping address country is required")
		sts = 'FAILURE'
	else: 
		s_country = Country.objects.filter(country_name__iexact = ship_addr_country).first()
		if not s_country:
			err_msg.append("Entered shipping address country is not found")
			sts = 'FAILURE'

	if sts == 'SUCCESS':
		request.POST = {'pin_code': ship_addr_pin_code, 'city': s_city.city, 'cstate': s_state.state_name,
		'country': s_country.country_name}	
		val = validate_address(request)
		result = json.loads(val.content)	
		if 'msg' in result:
			if result['msg'] != ['SUCCESS']:
				err_msg.append(result['msg'])
				sts = 'FAILURE'	

	#################################
	## Update shipping address  #####
	#################################
	if sts == 'SUCCESS':
		try:
			ord_s = order.order_shipping						
		except Order_shipping.DoesNotExist:
			ord_s = None
		if ord_s:
			s_ord = Order_shipping.objects.filter( order_id = order_id).update(
				full_name = ship_addr_full_name,
				Company = ship_addr_company,
				address_1 = ship_addr_1,
				address_2 = ship_addr_2,
				land_mark = ship_addr_land_mark,
				city = s_city.city,
				state = s_state,
				pin_code = s_pin,
				country = s_country,
				phone_number = ship_addr_phone_number,
				email_id = ship_addr_email_id,
				updated_date = today
			)
		else:
			if request.user.is_authenticated:
				try:			
					user = User.objects.get(username = request.user)
				except User.DoesNotExist:
					user = None
			else:
				user = None
			s_ord = Order_shipping( 
				store_id = settings.STORE_ID,
				order = order,
				user = user,
				full_name = ship_addr_full_name,
				Company = ship_addr_company,
				address_1 = ship_addr_1,
				address_2 = ship_addr_2,
				land_mark = ship_addr_land_mark,
				city = s_city.city,
				state = s_state,
				pin_code = s_pin,
				country = s_country,
				phone_number = ship_addr_phone_number,
				email_id = ship_addr_email_id,
				created_date = today,
				updated_date = today
			)
			s_ord.save()
			
	#################################
	## Update billing address  #####
	#################################
	if sts == 'SUCCESS':
		try:
			ord_b = order.order_billing						
		except Order_billing.DoesNotExist:
			ord_b = None
		if ord_b:
			b_ord = Order_billing.objects.filter( order_id = order_id).update(
				full_name = bill_addr_full_name,
				Company = bill_addr_company,
				address_1 = bill_addr_1,
				address_2 = bill_addr_2,
				land_mark = bill_addr_land_mark,
				city = b_city.city,
				state = b_state,
				pin_code = b_pin,
				country = b_country,
				phone_number = bill_addr_phone_number,
				email_id = bill_addr_email_id,
				gst_number = bill_addr_gst_number,
				updated_date = today
			)
		else:
			if request.user.is_authenticated:
				try:			
					user = User.objects.get(username = request.user)
				except User.DoesNotExist:
					user = None
			else:
				user = None
				
			b_ord = Order_billing( 
				store_id = settings.STORE_ID,
				order = order,
				user = user,
				full_name = bill_addr_full_name,
				Company = bill_addr_company,
				address_1 = bill_addr_1,
				address_2 = bill_addr_2,
				land_mark = bill_addr_land_mark,
				city = b_city.city,
				state = b_state,
				pin_code = b_pin,
				country = b_country,
				phone_number = bill_addr_phone_number,
				email_id = bill_addr_email_id,
				gst_number = bill_addr_gst_number,
				created_date = today,
				updated_date = today
			)
			b_ord.save()

		## retrive order again to get updated values
		order = Order.objects.filter(order_id = order_id).first()

	if order:
		order_items = Order_items_view.objects.select_related('product').filter(order = order,
					product__product_type_id = F('product_type_id'), quantity__gt = 0 ).order_by('product_id')
		c_ids = order_items.values('product_id')
		collage = Collage_stock_image.objects.filter(stock_collage_id__in = c_ids).order_by('stock_collage_id')
		
		try:
			ord_s = order.order_shipping						
		except Order_shipping.DoesNotExist:
			ord_s = None
		if ord_s:
			ship_form = ship_addressForm(instance = order.order_shipping)
		else:
			ship_form = ship_addressForm()
			
		try:
			ord_b = order.order_billing						
		except Order_billing.DoesNotExist:
			ord_b = None
		if ord_b:
			bill_form = bill_addressForm(instance = order.order_billing)
		else:
			bill_form = bill_addressForm()				
	else: 
		order_items = None
		collage = None
		ship_form = None
		bill_form = None

	return render(request, "artevenue/order_addr_change.html",
			{ 'sts': sts, 'err_msg': err_msg, 'order': order, 'order_items': order_items,
			'collage': collage, 'ship_form': ship_form, 'bill_form': bill_form}
			)	

def order_modify_items(request, order_id = None):
	today = datetime.datetime.today()

	err_msg = []
	sts = 'SUCCESS'
	
	if not order_id :
		order_id = request.GET.get('order_id', '')
	order = Order.objects.filter(order_id = order_id).first()

	if order:
		order_items = Order_items_view.objects.select_related('product').filter(order = order,
					product__product_type_id = F('product_type_id') ).order_by('product_id')

	# Get print mediums
	printmedium = Print_medium.objects.all()
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


	return render(request, "artevenue/order_modify_items.html",
			{ 'sts': sts, 'err_msg': err_msg, 'order': order, 'order_items': order_items,
			'printmedium':printmedium, 'mouldings_show':paper_mouldings_show, 
			'mounts': mounts, 'env':settings.EXEC_ENV,
			})	

@staff_member_required		
@csrf_exempt
def staff_page(request):
	return render(request, "artevenue/staff_page.html")
	

@staff_member_required
def pf_label_bulk(request):
	return render(request, 'artevenue/print_pf_labels_bulk.html')	

@staff_member_required	
@csrf_exempt	
def print_bulk_pf_labels (request):
	from django.template.loader import render_to_string
	from weasyprint import HTML, CSS
	from django.core.files.storage import FileSystemStorage
	from artevenue.models import Publisher

	startDt = ''
	endDt = ''	

	order_number = request.POST.get('order_num','')
	
	from_date = request.POST.get("fromdate", '')
	if from_date != '' :
		startDt = datetime.datetime.strptime(from_date, "%Y-%m-%d")	
		
	to_date = request.POST.get("todate", '')
	if to_date != '' :
		endDt = datetime.datetime.strptime(to_date, "%Y-%m-%d")
	
	order = Order.objects.all()
	if order_number:
		order = order.filter(order_number = order_number)
	if startDt:
		order = order.filter(order_date__gte = startDt)
	if endDt:
		order = order.filter(order_date__lte = endDt)
	
	if order_number == None and startDt == None and endDt == None:
		order = None
		
	for o in order:
		orderitems = Order_items_view.objects.select_related('product').filter(order = o,
					product__product_type_id = F('product_type_id'), quantity__gt = 0 ).order_by('product_id')
		
		c_ids = orderitems.values('product_id')
		collage = Collage_stock_image.objects.filter(stock_collage_id__in = c_ids).order_by('stock_collage_id')

		publ = Publisher.objects.all()

		html_string = render_to_string('artevenue/printing_framing_label.html', {
			'order': o, 'orderitems': orderitems, 'collage': collage, 'MEDIA_URL':settings.MEDIA_URL,
			'ecom_site':ecom, 'publ': publ, 'env': env})

		html = HTML(string=html_string, base_url=request.build_absolute_uri())
		html.write_pdf(target= settings.TMP_FILES + o.order_number + '_printing_framing_label.pdf',
						presentational_hints=True);
		
		fs = FileSystemStorage(settings.TMP_FILES)
		with fs.open(o.order_number + '_printing_framing_label.pdf') as pdf:
			response = HttpResponse(pdf, content_type='application/pdf')
			response['Content-Disposition'] = 'attachment; filename="' + o.order_number + '_printing_framing_label.pdf"'
			return response

		return response


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
	
	
@staff_member_required
def get_stock_images_staff(request):
	
	page = request.GET.get("page_num", 1)

	sortOrder = request.GET.get("sort")
	show = request.GET.get("show", "100")
	result_limit = request.GET.get("result_limit", "0-50")

	ikeywords = request.GET.get('keywords', '')	
	f_keywords = ikeywords.split()

	f_shape = request.GET.get("shape", "").split(',')
	f_shape = [x.strip() for x in f_shape if x.strip()]

	i_width = request.GET.get("width", "0")
	if not i_width :
		f_width = 0
	else:
		f_width = int(i_width)
	i_height = request.GET.get("height", "0")
	if not i_width :
		f_height = 0
	else:
		f_height = int(i_height)
	
	f_colors = request.GET.get("colors", "").split(',')
	f_colors = [x.strip() for x in f_colors if x.strip()]

	f_art_type = request.GET.get("art_type", "")

	f_artist = request.GET.get("artist", "")
	f_image_code = request.GET.get("image_code", "")
	f_image_title = request.GET.get("image_title", "")
	f_category_id = request.GET.get("category_id", "")
	f_product_id = request.GET.get("product_id", "")
	
	if f_category_id:
		try:
			product_category = Stock_image_category.objects.filter(category_id = f_category_id).first()
			if product_category :				
				cat_id = product_category.category_id
			else:
				cat_id = 0
				product_category = None					
		except Stock_image_category.DoesNotExist:
			cat_id = 0
			product_category = None
		except Stock_image_category.MultipleObjectsReturned:
			cat_id = 0
			product_category = None		
	else:
		cat_id = 0
		product_category = None


	
	if page is None or page == 0:
		page = 1 # default


	if cat_id:
		category_prods = Stock_image_stock_image_category.objects.filter(
				stock_image_category_id = cat_id).values('stock_image_id')
		products = Stock_image.objects.filter(product_id__in = category_prods, 
				is_published = True)
	else :
		category_prods = {}
		products = Stock_image.objects.filter(is_published = True)

	categories = Stock_image_category.objects.filter(store_id=settings.STORE_ID, trending = True )
	
	if f_product_id:
		products = products.filter(product_id = f_product_id)
	
	if f_keywords:
		filt_applied = False
		for word in f_keywords:
			if word == '':
				continue
			products = products.filter( 
				Q(key_words__icontains = word) |
				Q(artist__icontains = word) |
				Q(name__icontains = word) |
				Q(part_number__icontains = word)
				)

	all_filters = Q()
	
	if f_shape:
		filter_shape = Q()
		for f in f_shape:		
			if f.upper().strip() == 'HORIZONTAL':
				filter_shape = filter_shape | Q(aspect_ratio__gt = 1.01, aspect_ratio__lte = 2)
				filt_applied = True
			elif f.upper().strip() == 'SLIM HORIZONTAL':
				filter_shape = filter_shape | Q(aspect_ratio__gt = 2)
				filt_applied = True
			elif f.upper().strip() == 'VERTICAL':
				filter_shape = filter_shape | Q(aspect_ratio__lt = 1, aspect_ratio__gte = 0.666)
				filt_applied = True
			elif f.upper().strip() == 'SLIM VERTICAL':
				filter_shape = filter_shape | Q(aspect_ratio__lt = 0.666)
				filt_applied = True
			elif f.upper().strip() == 'SQUARE':
				filter_shape = filter_shape | Q(aspect_ratio__gte = 0.97, aspect_ratio__lt = 1.01)
				filt_applied = True
		products = products.filter( filter_shape )

	if f_width:
		products = products.filter( min_width__lte = f_width, max_width__gte = f_width)
	if f_height:
		products = products.filter( min_height__lte = f_height, max_height__gte = f_height )

	if f_width and f_height:
		r = f_width / f_height
		r_start = r - r *10/100
		r_end = r + r *10/100
		products = products.filter( aspect_ratio__gte = r_start, aspect_ratio__lte = r_end )
	
	if f_colors:
		filter_color = Q()
		for f in f_colors:		
			filter_color = filter_color | Q(key_words__icontains = f)
			filt_applied = True
		products = products.filter( filter_color )
	
	if f_art_type:
		products = products.filter( image_type = f_art_type )
	
	if f_artist:
		products = products.filter( artist__icontains = f_artist )
		
	if f_image_code:
		products = products.filter( part_number__icontains = f_image_code )

	if f_image_title:
		products = products.filter( name__icontains = f_image_title )

	products = products.order_by('category_disp_priority', 'product_id')
	
	price = Publisher_price.objects.filter(print_medium_id = 'PAPER') 
	

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
	

	template = "artevenue/staff_image_search.html"
	
	env = settings.EXEC_ENV
	
	s = ","
	colors = s.join(f_colors)
	keywords = s.join(f_keywords)
	
	cate_id = None
	if product_category:
		cate_id = product_category.category_id
	return render(request, template, {
		'products':products, 'prods':prods, 'sortOrder':sortOrder, 'show':show,
		'price':price, 'keywords':keywords, 'product_id': f_product_id,
		'page':page, 
		'page_range':page_range, 'result_limit':result_limit,
		'total_count':total_count, 'sliced_count':sliced_count, 'result_limit':result_limit,
		'slab_0_50':slab_0_50, 'slab_50_100':slab_50_100, 'slab_100_150':slab_100_150, 
		'slab_150_200':slab_150_200, 'slab_200_plus':slab_200_plus, 'env':env, 
		'category_id' : cate_id, 'categories': categories,
		'width': f_width, 'colors': colors, 'art_type': f_art_type,
		'height': f_height, 'artist': f_artist, 'image_code' : f_image_code, 'image_title' : f_image_title,
		'cat_id': cat_id} )
	

@staff_member_required
def generate_print_data(request):

	orders = Order.objects.filter(order_status = 'PC').order_by('order_date')
	orderitems = Order_items_view.objects.select_related('product').filter(order__in = orders,
				product__product_type_id = F('product_type_id'), quantity__gt = 0 ).order_by('product_id')
	
	c_ids = orderitems.values('product_id')
	collage = Collage_stock_image.objects.filter(stock_collage_id__in = c_ids).order_by('stock_collage_id')
	
	msg = ""
	return render(request, "artevenue/generate_print_data.html",
		{ 'msg': msg, 'env': env, 'ord_cnt': orders.count(),
		 'new_orders': orders, 'orderitems': orderitems, 'collage': collage})	

@staff_member_required
def generate_print_data_csv(request):
	today = datetime.datetime.today()
	now = datetime.datetime.now()
	dt = str(now.day)
	mth = str(now.month)
	year = str(now.year)
	
	dt_suf = year + '-' + mth + "-" + dt
	
	order_ids = request.GET.get('order_ids', '')
	search_type = request.GET.get('opt', 'PC')
	print_for = request.GET.get('print_for', '')	
	printcsv = request.GET.get('printcsv', 'NO')
	iorder_num = request.GET.get('order_num', '')
	if iorder_num:
		order_num = iorder_num.split(",");
	else:
		order_num = None

	if order_ids:
		order_ids = order_ids.split(",")

	order_list = None
	## When printing the csv file, use only selected orders
	if  printcsv == "YES":	
		order_list = Order.objects.filter(order_id__in = order_ids).order_by('order_date')
	else:
		if search_type == 'ORD_NUM_FLG':		
			order_list = Order.objects.filter(order_number__in = order_num).order_by('order_date')
		elif search_type == 'PC':
			order_list = Order.objects.filter(order_status = 'PC').order_by('order_date') 
		elif search_type == 'PR':
			order_list = Order.objects.filter(order_status = 'PR').order_by('order_date')
		
	if order_list:
		orderitems = Order_items_view.objects.select_related('product').filter(order__in = order_list,
					product__product_type_id = F('product_type_id'), quantity__gt = 0 ).order_by('product_id')

		orderitems_stock_image = Order_items_view.objects.select_related('product').filter(order__in = order_list,
					product_type_id = 'STOCK-IMAGE',
					product__product_type_id = F('product_type_id'), quantity__gt = 0 ).order_by('product_id')

		orderitems_stock_collage = Order_items_view.objects.select_related('product').filter(order__in = order_list,
					product_type_id = 'STOCK-COLLAGE',
					product__product_type_id = F('product_type_id'), quantity__gt = 0 ).order_by('product_id')
	else :
		orderitems = {}
		orderitems_stock_image = {}
		orderitems_stock_collage = {}

	if printcsv == "YES":	
		######## CANVAS file
		if print_for == 'CANVAS':
			file_nm = "CANVAS_print_data_" + dt_suf + ".csv"
			response = HttpResponse(content_type='text/csv')
			response['Content-Disposition'] = 'attachment; filename=' + file_nm
			import csv
			writer = csv.writer(response)
			writer.writerow(['ITEM_NUMBER', 'QTY', 'MEDIUM', 'UNITS', 'IMAGEW', 'IMAGEH', 'BORDER1W', 'BORDER1_TYPE',
				'BORDER1_BVL', 'BORDER2W', 'BORDER2_TYPE', 'BORDER2_BVL', 'STRETCH_BDR', 'FOLD_MARKS', 'ROTATION',
				'FLIP', 'TAGLINE'])
			for i in orderitems_stock_image:
				if i.print_medium_id == 'CANVAS':
					row = [i.product.part_number, i.quantity, '', 'IN', i.image_width, i.image_height, 
					1.1 if i.stretch_id == 1 and i.print_medium_id == 'CANVAS' and not i.moulding_id else 0, 
					'MIRROR' if i.stretch_id == 1 and i.print_medium_id == 'CANVAS' and not i.moulding_id else 'FFFFFF',
					'', '', '', '',  0.9 if i.stretch_id == 1 and i.print_medium_id == 'CANVAS' and not i.moulding_id else 2,
					'Y', '0', '', "Artevenue.com | Give Life to Your Walls"
					]

					writer.writerow(row)

			for i in orderitems_stock_collage:
				collage_products = Collage_stock_image.objects.filter(stock_collage_id = i.product_id)
				for j in collage_products:
					if i.print_medium_id == 'CANVAS':
						row = [j.stock_image.part_number, i.quantity, '', 'IN', i.image_width, i.image_height, 
						1.1 if i.stretch_id == 1 and i.print_medium_id == 'CANVAS' and not i.moulding_id else 0, 
						'MIRROR' if i.stretch_id == 1 and i.print_medium_id == 'CANVAS' and not i.moulding_id else 'FFFFFF',
						'', '', '', '',  1 if i.stretch_id == 1 and i.print_medium_id == 'CANVAS' and not i.moulding_id else 2,
						'Y', '0', '', "Artevenue.com | Give Life to Your Walls"
						]					
						writer.writerow(row)


		########PAPER file
		if print_for == 'PAPER':
			file_nm = "PAPER_print_data_" + dt_suf + ".csv"
			response = HttpResponse(content_type='text/csv')
			response['Content-Disposition'] = 'attachment; filename=' + file_nm
			import csv
			writer = csv.writer(response)
			writer.writerow(['ITEM_NUMBER', 'QTY', 'MEDIUM', 'UNITS', 'IMAGEW', 'IMAGEH', 'BORDER1W', 'BORDER1_TYPE',
				'BORDER1_BVL', 'BORDER2W', 'BORDER2_TYPE', 'BORDER2_BVL', 'STRETCH_BDR', 'FOLD_MARKS', 'ROTATION',
				'FLIP', 'TAGLINE'])
			for i in orderitems_stock_image:
				if i.print_medium_id == 'PAPER':
					row = [i.product.part_number, i.quantity, '', 'IN', i.image_width, i.image_height, '', '',
					'', '', '', '',  1 if i.print_medium_id == 'PAPER' and not i.moulding_id else '',
					'', '0', '', "Artevenue.com | Give Life to Your Walls"
					]
					writer.writerow(row)

			for i in orderitems_stock_collage:
				collage_products = Collage_stock_image.objects.filter(stock_collage_id = i.product_id)
				for j in collage_products:
					if i.print_medium_id == 'PAPER':
						row = [j.stock_image.part_number, i.quantity, '', 'IN', i.image_width, i.image_height, '', '',
						'', '', '', '',  1 if i.print_medium_id == 'PAPER' and not i.moulding_id else '',
						'', '0', '', "Artevenue.com | Give Life to Your Walls"
						]
						writer.writerow(row)

		return response		
	else:
		return render(request, 'artevenue/generate_print_data_csv.html', { 
			'order_list': order_list, 'search_type': search_type, 'order_num': iorder_num, 'orderitems': orderitems,
			'orderitems_stock_collage': orderitems_stock_collage})


def create_voucher(request):
	today = datetime.datetime.today()
	
	# Get data from the request.
	json_data = json.loads(request.body.decode("utf-8"))


	for key, val in json_data.items():
	
		email = key
		
		for subkey, subvalue in val.items():
			if subkey == "USER_ID":	
				user_id = subvalue
			if subkey == "VOUCHER_CODE":	
				voucher_code = subvalue
				voucher = Voucher.objects.filter(voucher_code = voucher_code).first()
			if subkey == "DISCOUNT_TYPE":	
				disc_type = subvalue
			if subkey == "DISCOUNT_VALUE":	
				disc_value = subvalue	


			gift_amount = 0
			voucher = Voucher(
				voucher_code = voucher.voucher_code,
				store_id = settings.STORE_ID,
				effective_from = today,
				effective_to = today.replace(year=today.year + 1),
				discount_type = 'CASH',
				discount_value = Decimal(gift_amount),
				all_applicability = False,
				created_date = today,	
				updated_date = today
			)
			voucher.save()	
			
			
def create_user_vouchers_from_file(request=None):
	from pathlib import Path
	today = datetime.datetime.today()
	cfile = Path('coupon_data_2021_09_20_withUserId.csv')
	if not cfile.is_file():
		print("coupon_data_2021_09_20_withUserId.csv file not found")
		return
	file = open('coupon_data_2021_09_20_withUserId.csv')	
	cr = csv.reader(file, delimiter=',')
	
	cnt = 0
	for row in cr:
		if cnt == 0:	## Skipping first header row
			cnt = cnt + 1
			continue
		cnt = cnt + 1
		user_id = row[0]
		email_id = row[1]
		perc = Decimal(row[2])
		create_user_voucher(user_id, email_id, perc)

		
def create_user_voucher(user_id, email_id, perc, eff_from_date=None, eff_to_date=None):
	err_flag = False
	err_msg = ''
	voucher_code = ''

	if user_id and email_id and perc > 0 and perc < 60:
		user = User.objects.filter(id = user_id).first()
		if user:			
			try:
				if not eff_to_date:
					eff_to_date = datetime.datetime.strptime('2021-12-31', "%Y-%m-%d").date()
				if not eff_from_date:
					eff_from_date = today
				######################################################
				# Create the coupan/voucher applicable to the user
				######################################################
				import uuid
				voucher_code = uuid.uuid4().hex[:7].upper()

				# Make sure generated code is not already used
				voucher_exist = Voucher.objects.filter(voucher_code = voucher_code)
				while voucher_exist:
					voucher_code = uuid.uuid4().hex[:7].upper()
					voucher_exist = Voucher.objects.filter(voucher_code = voucher_code)				
					
				voucher_code = 'Si' + voucher_code + 'x'
				## Create
				voucher = Voucher(
					voucher_code = voucher_code,
						store_id = settings.STORE_ID,
						effective_from = today,
						effective_to = eff_to_date,
						discount_type = 'PERCENTAGE',
						discount_value = perc,
						all_applicability = False,
						created_date = today,	
						updated_date = today
					)
				voucher.save()	
			
				if voucher:
					voucher_user = Voucher_user(
						voucher = voucher,
						user_id = user_id,
						effective_from = today,
						effective_to = eff_to_date,
						used_date = None,
						created_date = today,
						updated_date = today
					)
				voucher_user.save()
				
			except Error as e:
				print("An error occured whilte creating VOUCHER.")
				print(e)
				err_flag = True
				err_msg = e
				
	return( {'err_flag': err_flag, 'err_msg':err_msg, 'voucher_code': voucher_code})
	

def apply_coupon_to_order(cart_id=None, order_number=None, voucher_code=None):

	if not order_number and not cart_id:
		status = "cart_id or order_number and voucher_code is required."
		return JsonResponse({"status":status})
	if not voucher_code:
		status = "cart_id or order_number and voucher_code is required."
		return JsonResponse({"status":status})

	today = datetime.date.today()
	status = 'SUCCESS'
	cart = {}
		
	if cart_id:
		try :
			cart = Cart.objects.get(cart_id = cart_id)
			order = Order.objects.filter(cart = cart).first()
			order_id = order.order_id
		except Cart.DoesNotExist:
			cart = None
			order_id = None
			status = "Cart Id: " + cart_id + " not found"
			return JsonResponse({"status":status})
	else:
		if order_number:
			order = Order.objects.filter(order_number = order_number).first()			
			if order:
				cart = Cart.objects.filter(cart_id = order.cart_id).first()
				cart_id = cart.cart_id
			else:	
				cart = None				
				order = None
				cart_id = None
				
	if voucher_code == '':
		return JsonResponse({"status":"Coupon Code not found"})

	voucher = Voucher.objects.filter(voucher_code = voucher_code, effective_from__lte = today, 
			effective_to__gte = today, store_id = settings.STORE_ID).first()
			
	if not voucher :
		return JsonResponse({"status":"Coupon Code is invalid"})		
	
	## Remove any applied voucher
	from django.http import HttpRequest
	request = HttpRequest()
	res = remove_voucher_active_cart_required(request, cart.cart_id, False)
	rep = json.loads(res.content.decode('utf-8'))
	if rep['status'] == 'FAILURE':
		status = rep['msg']
		return JsonResponse({"status":status})
		
	## Apply selected voucher to cart
	if cart:
		cart = Cart.objects.get(cart_id = cart_id)
		cart_items = Cart_item_view.objects.filter(cart = cart)
		cart_disc_amt = 0
		cart_sub_total = 0
		cart_tax = 0
		cart_total = 0
		
		for ci in cart_items:
			## Get applicable tax rate
			taxes = get_taxes()
			if ci.product_type_id == 'STOCK-IMAGE':
				tax_rate = taxes['stock_image_tax_rate']
			if ci.product_type_id == 'USER-IMAGE':
				tax_rate = taxes['user_image_tax_rate']
			if ci.product_type_id == 'STOCK-COLLAGE':
				tax_rate = taxes['stock_collage_tax_rate']
			if ci.product_type_id == 'ORIGINAL-ART':
				tax_rate = taxes['original_art_tax_rate']		
		
			item_disc_amt = (ci.item_sub_total * voucher.discount_value / 100)
			item_sub_total = ci.item_sub_total - item_disc_amt
			item_tax = item_sub_total * tax_rate /100			
			item_total = item_sub_total + item_tax
			
			cart_disc_amt = cart_disc_amt + item_disc_amt
			cart_sub_total = cart_sub_total + item_sub_total
			cart_tax = cart_tax + item_tax 
			cart_total = cart_total + item_total

			try:
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
			except IntegrityError as e:
				status = "System Error while updating item in the cart"
				return JsonResponse({"status":status})
		
		cart_total = round(cart_total)		
		## Update cart
		try:
			crt = Cart.objects.filter(cart_id = cart_id).update(
				voucher_id = voucher.voucher_id,
				voucher_disc_amount = cart_disc_amt,
				cart_sub_total = cart_sub_total,
				cart_disc_amt =  cart_disc_amt,
				cart_tax = cart_tax,
				cart_total = cart_total
			)
		except IntegrityError as e:
			return JsonResponse({"status":'FAILURE', 'msg': 'System Error while updating the cart values'})

		###########################################################################
		###########################################################################
		## Update the order
		###########################################################################
		###########################################################################
		if order:
			cart = Cart.objects.filter(cart_id = order.cart_id).first()
			cart_items = Cart_item_view.objects.filter(cart = cart)
			
			sub_total = cart.cart_sub_total
			tax = cart.cart_tax
			order_total = cart.cart_total

			order_items = Order_items_view.objects.filter(order = order)
			try:		
				for c in cart_items:
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
									item_sub_total = c.item_sub_total,
									item_disc_amt  = c.item_disc_amt,
									item_tax  = c.item_tax,
									item_total = c.item_total,
									created_date = 	today,
									updated_date = today
									)
						if c.product_type_id == 'USER-IMAGE':
							Order_user_image.objects.filter(
								order_item_id = ord_itm.order_item_id).update(
									item_sub_total = c.item_sub_total,
									item_disc_amt  = c.item_disc_amt,
									item_tax  = c.item_tax,
									item_total = c.item_total,
									)
						if c.product_type_id == 'STOCK-COLLAGE':
							Order_stock_collage.objects.filter(
								order_item_id = ord_itm.order_item_id).update(
									item_sub_total = c.item_sub_total,
									item_disc_amt  = c.item_disc_amt,
									item_tax  = c.item_tax,
									item_total = c.item_total,
									)
						if c.product_type_id == 'ORIGINAL-ART':
							Order_original_art.objects.filter(
								order_item_id = ord_itm.order_item_id).update(
									item_sub_total = c.item_sub_total,
									item_disc_amt  = c.item_disc_amt,
									item_tax  = c.item_tax,
									item_total = c.item_total,
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
				ord = Order.objects.filter(order_id = order.order_id).update(
					voucher = cart.voucher,
					voucher_disc_amount = cart.voucher_disc_amount,
					sub_total = cart.cart_sub_total,
					order_discount_amt = cart.cart_disc_amt,
					tax = cart.cart_tax,
					order_total = cart.cart_total,
					created_date =  order.created_date,
					updated_date =  today
				)
				
				if order.order_status in ('PC', 'PR', 'SH', 'IN'):
					## If a voucher is applied in order, and it was an egift then update the redemption
					if order.user:
						eGift = Egift.objects.filter(voucher = order.voucher, receiver_email = order.user.email).first()
						if eGift:
							eGift_redemption = Egift_redemption( 
								egift = eGift,
								redemption_date = today.date(),
								redemption_amount = order.voucher_disc_amount,
								created_date = datetime.datetime.now(),
								updated_date = datetime.datetime.now()				
							)

							# If the applied voucher was for a perticular user and if there is no more balance 
							# left in voucher, then update the voucher as used.			
							eGift_redemption = Egift_redemption.objects.filter( egift = eGift 
									).aggregate(total_redemption=Sum('redemption_amount'))		
							if eGift_redemption['total_redemption']:
								total_redemption = Decimal(eGift_redemption['total_redemption'])
							else: 
								total_redemption = 0
								
							voucher_bal_amount = eGift.voucher_amount - total_redemption - order.voucher_disc_amount
							
							voucher_user = Voucher_user.objects.filter(voucher = voucher, effective_from__lte = today.date(), 
									effective_to__gte = today.date(), user = order.user).first()
							if voucher_bal_amount <= 0:
								if voucher_user:
									v = Voucher_user (
										id = voucher_user.id,
										voucher = voucher_user.voucher,
										user = voucher_user.user,
										effective_from = voucher_user.effective_from,
										effective_to = voucher_user.effective_to,
										used_date = datetime.datetime.now(),
										created_date = voucher_user.created_date,
										updated_date = datetime.datetime.now()
									)
									v.save()		

		
				## Update the voucher used table, if a voucher was used
				if order.voucher_id and order.user:
					vu = Voucher_used( 
						voucher_id = order.voucher_id,
						user = order.user,
						created_date = today,
						updated_date = today
					)
					vu.save()					
			
			except Error as e:
				return JsonResponse({"status":'FAILURE', 'msg': 'System Error while updating the cart values'})
				
	return JsonResponse({"status":status})



def remove_voucher_active_cart_required(request, cart_id, active_cart_required=True):
	msg = ''
	status = "SUCCESS"

	try:
		cart = Cart.objects.get(cart_id = cart_id)
		if active_cart_required:
			cart = cart.filter(cart_status = 'AC')
	except Cart.DoesNotExist:
		return JsonResponse({"status":'FAILURE', 'msg': 'No such cart'})

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
		
		## Cart level totals
		cart_qty = 0
		cart_unit_price = 0
		cart_sub_total = 0
		cart_disc_amt = 0 
		cart_tax = 0
		cart_total = 0
		for ci in cart_items:
			if ci.product_type_id == 'STOCK-COLLAGE':
				collages = Collage_stock_image.objects.filter( stock_collage_id = ci.product_id )
				total_price = 0
				total_cash_disc = 0
				total_percent_disc = 0
				item_unit_price = 0
				total_item_unit_price = 0
				total_item_price_withoutdisc = 0
				total_disc_amt = 0
				disc_applied = False
				promotion_id = None
				#####################################
				#    Get the item price for each
				#####################################
				for c in collages:
					price = get_prod_price(ci.product_id, 
							prod_type='STOCK-IMAGE',
							image_width=ci.image_width, 
							image_height=ci.image_height,
							print_medium_id = ci.print_medium_id,
							acrylic_id = ci.acrylic_id,
							moulding_id = ci.moulding_id,
							mount_size = ci.mount_size,
							mount_id = ci.mount_id,
							board_id = ci.board_id,
							stretch_id = ci.stretch_id)

					item_price = price['item_price']
					msg = price['msg']
					cash_disc = price['cash_disc']
					percent_disc = price['percent_disc']
					item_unit_price = price['item_unit_price']
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
					total_item_unit_price = total_item_unit_price + item_unit_price 

				## Set variables as used in the code after getting price
				total_price = total_price
				cash_disc = total_cash_disc
				percent_disc = total_percent_disc
				item_unit_price = total_item_unit_price
				item_price_withoutdisc = total_item_price_withoutdisc
				disc_amt = total_disc_amt

			### IF NOT STOCK COLLAGE, ART SET

			else:

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
			item_unit_price = item_unit_price * ci.quantity
			item_sub_total = round( (total_price*ci.quantity) / (1 + (tax_rate/100)), 2 )
			item_tax = round(total_price - item_sub_total, 2)
			item_total = round(item_sub_total + item_tax)
			
			## Cummulative totals to be updated at cart level
			cart_qty = cart_qty + 1
			cart_unit_price = cart_unit_price + item_unit_price 
			cart_sub_total = cart_sub_total + item_sub_total
			cart_disc_amt =  cart_disc_amt + disc_amt
			cart_tax = cart_tax + item_tax
			cart_total = cart_total + item_total

			#######################################################################
			##Update the cart item now (this will remove any applied voucher disc)
			#######################################################################
			try:
				if ci.product_type_id == 'STOCK-IMAGE':
					c = Cart_stock_image.objects.filter(cart_item_id = ci.cart_item_id).update(
						item_unit_price = item_unit_price,
						item_sub_total = item_sub_total, item_tax = item_tax,
						item_disc_amt = disc_amt, item_total = item_total)
				if ci.product_type_id == 'USER-IMAGE':
					c = Cart_user_image.objects.filter(cart_item_id = ci.cart_item_id).update(
						item_unit_price = item_unit_price,
						item_sub_total = item_sub_total, item_tax = item_tax,
						item_disc_amt = disc_amt, item_total = item_total)
				if ci.product_type_id == 'STOCK-COLLAGE':
					c = Cart_stock_collage.objects.filter(cart_item_id = ci.cart_item_id).update(
						item_unit_price = item_unit_price,
						item_sub_total = item_sub_total, item_tax = item_tax,
						item_disc_amt = disc_amt, item_total = item_total)
				if ci.product_type_id == 'ORIGINAL-ART':
					c = Cart_original_art.objects.filter(cart_item_id = ci.cart_item_id).update(
						item_unit_price = item_unit_price,
						item_sub_total = item_sub_total, item_tax = item_tax,
						item_disc_amt = disc_amt, item_total = item_total)
			except IntegrityError as e:
				return JsonResponse({"status":'FAILURE', 'msg': 'System Error while updating item in the cart'})
				
		###################################
		## Update the amounts at cart level
		###################################
		## cart disc amt is the discount through each item promotion and 
		## referral disc
		cart_disc_amt = cart_disc_amt + cart.referral_disc_amount
			
		try:
			crt = Cart.objects.filter(cart_id = cart_id).update(
				voucher_id = None,
				voucher_disc_amount = 0,
				cart_unit_price = cart_unit_price,
				cart_sub_total = cart_sub_total,
				cart_disc_amt =  cart_disc_amt,
				cart_tax = cart_tax,
				cart_total = cart_total
			)
		except IntegrityError as e:
			return JsonResponse({"status":'FAILURE', 'msg': 'System Error while updating the cart values'})

		######################################
		## Remove Voucher_used record, if any
		######################################
		vu = Voucher_used.objects.filter(voucher_id = cart.voucher_id,
			user_id = cart.user_id).delete()

	return JsonResponse({"status":status, 'msg': msg})		



def update_tracking(order_list=None):

	if env == 'PROD':
		input_file = '/home/artevenue/website/estore/static/courier_tracking/tracking_file.txt'
	else:
		input_file = 'c:/artevenue/tracking_file.txt'
	
	cnt = 0
	not_found = 0		
	
	if order_number :		
		for o in order_list:
			cnt = cnt + 1
			order = Order.objects.filter(order_number = o)
			if order:
				awb = ''
				shipper_id = ''
				## API call to fetch the tracking detaals
				
				
				upd = Order.objects.filter(order_number = o, 
					order_date__isnull = False, invoice_date__isnull = False).update(
						tracking_number = awb, shipper_id = int(shipper_id),
						order_status = 'IN')
				if upd < 1:
					print("customer order not found for " + full_name)
					not_found = not_found + 1
	else:
		with open(input_file) as i_file:
			file = csv.reader(i_file, delimiter='\t')
			for n in file:
				if cnt == 0:
					cnt = cnt+1
					continue
				cnt = cnt+1
				full_name = n[0]
				awb = n[1]
				shipper_id = n[2]
				
				## 
				upd = Order.objects.filter(order_shipping__full_name__icontains = full_name, 
					order_date__isnull = False, invoice_date__isnull = False).update(
						tracking_number = awb, shipper_id = int(shipper_id),
						order_status = 'IN')
				if upd < 1:
					print("customer order not found for " + full_name)
					not_found = not_found + 1
				
	print(str(cnt-1) + " rows processed")
	print(str(not_found) + " names not found")
	

def hipship_api():

	#import urllib, urllib2, json
	import requests, json
	# API url
	book_url = 'https://test.hipship.com/api/test/v1.1/shipment/book'
	track_url = ' https://test.hipship.com/api/test/v1.1/shipment/track'
	
	# Required input data in json format
	data = {"AWBNumber": "787657678"}
	headers = {'Content-Type':'application/json', 'Authorization': 'Token bc985a170d862f7f685950e65b0a071979d6fba1'}
	
	# Https request objects
	#req = urllib2.Request(url, json.dumps(data), headers)
	
	response = requests.post(track_url, headers=headers, data=data)
	j = response.json()
	print(j)
	# Get response
	##response = urllib2.urlopen(req).read()
	
	# Read response
	#result = json.loads(response)
	
	#print(result)