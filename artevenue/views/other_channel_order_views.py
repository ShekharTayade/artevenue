from django.shortcuts import render, get_object_or_404
import datetime
from django.views.decorators.csrf import csrf_protect, csrf_exempt
from django.template.context_processors import csrf
from django.db import IntegrityError, DatabaseError, Error
from decimal import Decimal
from django.db.models import F
from django.conf import settings

from artevenue.models import Order, Order_items_view, Publisher
from artevenue.models import Order_sms_email, Order_shipping, Order_billing
from artevenue.models import Channel_order_amz, Channel_order_amz_items

today = datetime.datetime.today()

def amazon_orders_manage(request):
	amz_orders = {}
	return render(request, "artevenue/amazon_orders_manage.html", {'amz_orders':amz_orders} )

@csrf_exempt
def get_amz_orders(request):
	amz_orders = Channel_order_amz.objects.all().order_by('-amazon_order_date')
	amazon_order_no = request.POST.get("amazon_order_no", "").replace('\n','').replace('\t','')
	av_order_no = request.POST.get("av_order_no", "").replace('\n','').replace('\t','')
	from_date = request.POST.get("fromdate", '')
	if from_date != '' and from_date != 'NaN-NaN-NaN':
		startDt = datetime.datetime.strptime(from_date, "%Y-%m-%d")	
	else: 
		startDt = None
	to_date = request.POST.get("todate", '')
	if to_date != '' and to_date != 'NaN-NaN-NaN':
		endDt = datetime.datetime.strptime(to_date, "%Y-%m-%d")
	else:
		endDt = None
		
	if amazon_order_no:
		amz_orders = amz_orders.filter( amazon_order_no = amazon_order_no)
	if av_order_no:
		amz_orders = amz_orders.filter(order__order_number = av_order_no)
	if startDt:
		amz_orders = amz_orders.filter(amazon_order_date__gte = startDt)
	if endDt:
		amz_orders = amz_orders.filter(amazon_order_date__lte = endDt)

	return render(request, "artevenue/amazon_artevenue_orders_include.html", {'amz_orders':amz_orders} )

	

@csrf_exempt
def amazon_order_details(request):
	amz_orders = Channel_order_amz.objects.all()
	amazon_order_no = request.POST.get("amazon_order_no", "").replace('\n','').replace('\t','')
	amz_orders = amz_orders.filter(amazon_order_no = amazon_order_no)
	order_details = Channel_order_amz_items.objects.filter(
					channel_order_amz__in = amz_orders)
	return render(request, "artevenue/amazon_order_details.html", {'amz_orders':amz_orders,
			'order_details':order_details } )


def amazon_enter_new_order(request):
	return render(request, "artevenue/amazon_enter_new_order.html", {} )


def create_other_channel_order(request, channel):
	try:
		chn = Order_channel.objects.get(channel_id = channel)
	except Order_channel.DoesNotExist:
		return ({'msg':'INVALID-CHANNEL'})

		
	## Get sku details:	
	sku_list = request.POST.getlist('sku[]', [])
	
	ord_dt = request.POST.get('ord_date', '')
	order_date = datetime.datetime.strptime(ord_dt, "%Y-%m-%d")
	
	## Retrieve SKUs from amazon_data
	amz = Amazon_data.objects.filter(amazon_sku__in = sku_list)
	
	if not amz:
		return ({'msg':'SKU-NOT-FOUND'})
		
	## Get order number
	order_no = get_other_channel_ord_next_number('AMZ')
		
	## Create Order record
	order = Order(
		order_number = order_no,
		order_date =  order_date,
		cart = None,
		store = ecom.STORE_ID,
		session_id = '',
		user = None,
		voucher = None,
		voucher_disc_amount = 0,
		referral = None,
		referral_disc_amount = 0,
		unit_price = ord_unit_price,	#############
		quantity = ord_quantity,	#############
		sub_total = ord_sub_total,	#############
		order_discount_amt = ord_disc_amt,	#############
		tax = ord_tax,	#############
		shipping_cost = ord_shp_cost, #############
		order_total = ord_total,	#############
		shipping_method = None,	#############
		shipper = None,	#############
		shipping_status = None,	#############
		order_status = 'PC',
		created_date = today,
		updated_date = today,	
		invoice_number = '',
		invoice_date = None,
		channel = channel
		)
	order.save()
		
	## Create Order items
	for a in amz:
		if amz.product_type == 'STOCK-IMAGE':
			order_item = Order_stock_image()
			order_item.stock_image_id = amz.product_id
		elif amz.product_type == 'STOCK-COLLAGE':
			order_item = Order_stock_collage()
			order_item.stock_collage_id = amz.product_id
		elif amz.product_type == 'USER-IMAGE':
			order_item = Order_user_image()
			order_item.user_image_id = amz.product_id
		elif amz.product_type == 'ORIGINAL-ART':
			order_item = Order_oroginal_art()
			order_item.original_art_id = amz.product_id
		
		
		order_item.order = order
		order_item.cart_item = Nonez
		order_item.product = amz.product
		order_item.promotion = amz.promotion
		order_item.quantity = itm_qty  ##################
		order_item.item_unit_price = amz.item_unit_price * itm_qty
		order_item.item_sub_total = amz.item_sub_total * itm_qty
		order_item.item_disc_amt  = amz.item_disc_amt * itm_qty
		order_item.item_tax  = amz.item_tax * itm_qty
		order_item.item_total = amz.item_total * itm_qty
		order_item.moulding = amz.moulding
		order_item.moulding_size = amz.moulding_size
		order_item.print_medium = amz.print_medium
		order_item.print_medium_size = amz.print_medium_size
		order_item.mount = amz.mount
		order_item.mount_size = amz.mount_size
		order_item.board = amz.board
		order_item.board_size = amz.board_size
		order_item.acrylic = amz.acrylic
		order_item.acrylic_size = amz.acrylic_size
		order_item.stretch = amz.stretch
		order_item.stretch_size = amz.stretch_size
		order_item.image_width = amz.image_width
		order_item.image_height = amz_height
		order_item.created_date = today
		order_item.updated_date = today
		order_item.product_type = amz.product_type
			
		order_item.save()
			
				
			
		
		
		