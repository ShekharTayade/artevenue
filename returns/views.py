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

from datetime import datetime
import datetime

from artevenue.models import Order, Order_items_view
from returns.models import Return_order

@staff_member_required
def initiate_returns(request):
	return render(request, 'returns/returns.html')	

@staff_member_required
@csrf_exempt
def get_orders_for_returns(request):
	startDt = ''
	endDt = ''	
	page = request.POST.get('page', 1)
	order_number = request.POST.get("order_number", '')
	name = request.POST.get("name", '')
	email = request.POST.get("email", '')
	phone_number = request.POST.get("phone_number", '')

	from_date = request.POST.get("fromdate", '')
	if from_date != '' :
		startDt = datetime.datetime.strptime(from_date, "%Y-%m-%d")	
		
	to_date = request.POST.get("todate", '')
	if to_date != '' :
		endDt = datetime.datetime.strptime(to_date, "%Y-%m-%d")
		
	order_list = Order.objects.all().exclude(order_status = 'PP').exclude(
		order_status = 'CN').select_related('order_billing', 
		'order_shipping').order_by('-updated_date')
		
	order_items_list = {}
	if startDt:
		order_list = order_list.filter(order_date__gte = startDt)
	if endDt:
		order_list = order_list.filter(order_date__lte = endDt)

	if order_number:
		order_list = order_list.filter(order_number = order_number)	
	
	if	not startDt and not endDt and not order_number:
		return render(request, 'returns/orders_for_returns_table.html', {'count':0, 
			'orders': {}, 'order_items_list':{}, 
			'startDt':startDt, 'endDt':endDt})

	order_items_list = Order_items_view.objects.select_related('product', 'promotion').filter(
		order__in = order_list, product__product_type_id = F('product_type_id'))
	
	count = order_list.count()
	
	paginator = Paginator(order_list, 25)
	orders = paginator.get_page(page)
	try:
		orders = paginator.page(page)
	except PageNotAnInteger:
		orders = paginator.page(1)
	except EmptyPage:
		orders = paginator.page(paginator.num_pages)

		
	return render(request, 'returns/orders_for_returns_table.html', {'count':count, 
		'orders': orders, 'order_items_list':order_items_list, 
		'startDt':startDt, 'endDt':endDt, 'MEDIA_URL':settings.MEDIA_URL})		

def choose_products_for_return(request, order_id=None):

	if order_id == None or order_id == '' :
		order_id = request.POST.get("order_id", '')

	order = Order.objects.filter(order_id = order_id).exclude(order_status = 'PP').exclude(
		order_status = 'CN').select_related('order_billing', 
		'order_shipping').order_by('-updated_date').first()

	choose_order_items = Order_items_view.objects.select_related('product', 'promotion').filter(
		order_id = order_id, product__product_type_id = F('product_type_id'))
		
	ret_reason = Return_order.RET_REASON
	
	return render(request, 'returns/choose_products_for_return.html', {
		'order': order, 'choose_order_items':choose_order_items, 'ret_reason': ret_reason
		})
		
def process_returns(request)	:
	order_id = request.POST.get("order_id", "")
	selected_items = request.POST.get("selected_items", "")
	selected_items = selected_items.split(",")
	
	ret_items = []
	for i in selected_items:
		if i.strip() == '':
			continue
		else:
			ret_items.append(i)

	order = Order.objects.filter(order_id = order_id).exclude(order_status = 'PP').exclude(
		order_status = 'CN').select_related('order_billing', 
		'order_shipping').order_by('-updated_date').first()
	
	ret_order_items = Order_items_view.objects.select_related('product', 'promotion').filter(
		order_id = order_id, 
		order_item_id__in = ret_items,
		product__product_type_id = F('product_type_id'))


	return render(request, 'returns/process_returns_confirmation.html', {
		'order': order, 'ret_order_items':ret_order_items, 
		})
