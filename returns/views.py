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
from decimal import Decimal

from artevenue.models import Order, Order_items_view
from returns.models import Return_order, Return_order_item
from artevenue.models import Generate_number_by_month

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
	
	ret_order = Return_order.objects.filter(
		order__in = order_list).values_list('order_id', flat=True).distinct()
	
	ret_orderObjs = Return_order.objects.filter(
		order__in = order_list)
	
	print(ret_orderObjs)
	
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
		'startDt':startDt, 'endDt':endDt, 'MEDIA_URL':settings.MEDIA_URL,
		'ret_order': ret_order, 'ret_orderObjs': ret_orderObjs})		

@staff_member_required
def choose_products_for_return(request, order_id=None):
	if order_id == None or order_id == '' :
		order_id = request.POST.get("order_id", '')
	
	ret_initiated = request.POST.get("ret_initiated", "")
	order = Order.objects.filter(order_id = order_id).exclude(order_status = 'PP').exclude(
		order_status = 'CN').select_related('order_billing', 
		'order_shipping').order_by('-updated_date').first()

	choose_order_items = Order_items_view.objects.select_related('product', 'promotion').filter(
		order_id = order_id, product__product_type_id = F('product_type_id'))
		
	ret_order = None
	ret_order_items = None
	if ret_initiated:
		ret_order = Return_order.objects.filter(
			order = order).first()
		ret_order_items = Return_order_item.objects.filter(return_order = ret_order)
		
	ret_reason = Return_order.RET_REASON
	
	return render(request, 'returns/choose_products_for_return.html', {
		'order': order, 'choose_order_items':choose_order_items, 'ret_reason': ret_reason,
		'ret_order': ret_order, 'ret_order_items': ret_order_items 
		})

@staff_member_required
def cancel_return_request(request, order_id=None):
	if order_id == None or order_id == '' :
		order_id = request.POST.get("order_id", '')
	
	ret_initiated = request.POST.get("ret_initiated", "")
	order = Order.objects.filter(order_id = order_id).exclude(order_status = 'PP').exclude(
		order_status = 'CN').select_related('order_billing', 
		'order_shipping').order_by('-updated_date').first()

	choose_order_items = Order_items_view.objects.select_related('product', 'promotion').filter(
		order_id = order_id, product__product_type_id = F('product_type_id'))
		
	ret_order = None
	ret_order_items = None
	if ret_initiated:
		ret_order = Return_order.objects.filter(
			order = order).first()
		ret_order_items = Return_order_item.objects.filter(return_order = ret_order)
		
	ret_reason = Return_order.RET_REASON
	
	return render(request, 'returns/cancel_return_request.html', {
		'order': order, 'choose_order_items':choose_order_items, 'ret_reason': ret_reason,
		'ret_order': ret_order, 'ret_order_items': ret_order_items 
		})


@staff_member_required	
def process_returns(request):
	today = datetime.datetime.today()
	order_id = request.POST.get("order_id", "")
	selected_items = request.POST.get("selected_items", "")
	selected_items = selected_items.split(",")
	marked_items = request.POST.get("ini_items", "")
	marked_items = marked_items.split(",")
	ret_order_id = request.POST.get("ret_order_id", "")
	ret_reason = request.POST.get("ret_reason", "")
	req_date = request.POST.get("req_date", "")
	remarks = request.POST.get("remarks", "")
	reqDt = ''
	if req_date != '' :
		reqDt = datetime.datetime.strptime(req_date, "%Y-%m-%d")	
	refund_amount = Decimal(request.POST.get("refund_amount", "0"))
	
	ret_items = []
	for i in selected_items:
		if i.strip() == '':
			continue
		else:
			ret_items.append(i)

	ini_items = []
	for i in marked_items:
		if i.strip() == '':
			continue
		else:
			ini_items.append(i)
		
	order = Order.objects.filter(order_id = order_id).exclude(order_status = 'PP').exclude(
		order_status = 'CN').select_related('order_billing', 
		'order_shipping').order_by('-updated_date').first()
	
	ret_order_items = Order_items_view.objects.select_related('product', 'promotion').filter(
		order_id = order_id, 
		order_item_id__in = ret_items,
		product__product_type_id = F('product_type_id'))

	if order:
		if ret_order_id:
			##### UPDATE EXISTING RETURN
			ret_o = Return_order.objects.filter(
				ret_id = ret_order_id).update(
				ret_request_date = reqDt,
				ret_reason = ret_reason,
				refund_amount = refund_amount,
				ret_status = '0',
				remarks = remarks,
				updated_date = today
			)		
			ret_o = Return_order.objects.filter(
				ret_id = ret_order_id).first()
		else:
			##### NEW RETURN
			ret_o = Return_order (
				ret_number = get_next_return_number(),
				ret_request_date = reqDt,
				ret_reason = ret_reason,
				order = order,
				return_shipment_charges = 0,
				other_deductions = 0,
				total_deductions = 0,
				refund_amount = refund_amount,
				refund_transaction_reference = '',
				remarks = remarks,
				ret_process_date = None,
				ret_shipping_method = None,
				ret_shipper = None,
				ret_shipping_status = None,
				ret_status = '0',
				created_date = today,
				updated_date = today
			)
			ret_o.save()
		
		##################################################################
		## Remove items that were marked for returns earlier, if any.
		## And then add all the items selected for return
		##################################################################
		for i in ini_items:
			del_i = Return_order_item.objects.filter(
				order_item_id__in = ini_items).delete()
			
		for i in ret_order_items:
			ret_i = Return_order_item(
				return_order = ret_o,
				order_item_id = i.order_item_id,
				ret_item_quantity = i.quantity,
				ret_item_unit_price = i.item_unit_price,
				ret_item_sub_total = i.item_sub_total,
				ret_item_disc_amt  = i.item_disc_amt,
				ret_item_tax  = i.item_tax,
				ret_item_total = i.item_total,
				quality_check_date = None,
				quality_check_passed = False,
				quality_check_failed_reason = ''
			)
			ret_i.save()

	
	return render(request, 'returns/process_returns_confirmation.html', {
		'ret_order': ret_o, 'ret_order_items':ret_order_items, 
		})


def get_next_return_number():
	num = 0
	#Get curentyear, month in format YYYYMM
	dt = datetime.datetime.now()
	mnth = dt.strftime("%Y%m")

	# Get suffix required 
	suffix = '-'
	# Get prefix required 
	prefix = 'R-'
	
	monthyear = Generate_number_by_month.objects.filter(type='RETURN-NUMBER', month_year = mnth).first()
	if monthyear :
		num = monthyear.current_number + 1
	else :
		num = 1
		
	# Update generated number in DB
	gen_num = Generate_number_by_month(
		type = 'RETURN-NUMBER',
		description = "Return number generation",
		month_year = mnth,
		current_number = num
		)
	
	gen_num.save()
		
	generated_num = 0
	if prefix:
		mnth = prefix + mnth
	if suffix:
		generated_num = (mnth + suffix + str(num))
	else:
		generated_num = (mnth + str(num))
	return generated_num 	

@staff_member_required
def get_active_return_requests(request):

	returns = Return_order.objects.filter(ret_status__lt = 8).exclude(ret_status = 'X').order_by('ret_request_date')
	return render(request, 'returns/list_of_active_returns.html', {'returns':returns})
	
@staff_member_required	
def return_request_for_update(request, ret_id=None):
	today = datetime.datetime.today()
	if ret_id == None:
		ret_id = request.GET.get("ret_id", "")
	
	ret = Return_order.objects.filter(ret_id = ret_id).first()
	ret_o_items = Return_order_item.objects.filter(return_order_id = ret_id).values_list('order_item_id', flat=True)
	
	status = ret.ret_status 

	list = Return_order.RET_STATUS
	status_list = {}
	for l in list:
		status_list[l[0]] = l[1]

	remove = []
	for k, v in status_list.items():
		if k <= status:
			remove.append(k)
	for r in remove:
		status_list.pop(r)
		
	## Remove statues -> X: cancelled & 8:refund issued & 9: Request Closed
	status_list.pop('X')
	
	## Closure status
	closure_status = Return_order.CLOSURE_STATUS
	
	ret_items = Order_items_view.objects.select_related('product').filter(
		order_item_id__in = ret_o_items,
		product__product_type_id = F('product_type_id'))
	
	return render(request, 'returns/return_request_for_update.html', {'ret':ret, 'ret_items': ret_items, 
		'status_list': status_list.items(), 'closure_status': closure_status})
		
@staff_member_required
def update_return_req_status(request):
	today = datetime.datetime.today()
	
	ret_id = request.POST.get("ret_id", "")
	set_status = request.POST.get("set_status", "")
	remarks = request.POST.get("remarks", "")

	err_flag = False
	err_msg = ''
	if ret_id == '':
		err_flag = True
		err_msg = "Return Request Number was Invalid"
	if set_status == '':
		err_flag = True
		err_msg = "Return Request Status to be Set was Invalid"
	if remarks == '' and set_status == '9':
		err_flag = True
		err_msg = "Remarks are required for closing the return request"
	if remarks == '' and set_status == '8':
		err_flag = True
		err_msg = "Please add refund details(such as payU ref number) in remarks"
	

	ret = Return_order.objects.filter(ret_id = ret_id).first()
	rem = ret.remarks + " | " + remarks

	if set_status == '9':
		closure_status = request.POST.get("closure_status", "")
	else:
		closure_status = ''

	## Update
	if not err_flag:
		c = Return_order.objects.filter(ret_id = ret_id).update(
			ret_status = set_status, closure_status = closure_status, 
			remarks = rem, updated_date = today
		)
		
		if c == 0 :
			err_flag = True
			err_msg = "No requests updated: Ret Id:" + str(ret_id)

		if c > 1 :
			err_flag = True
			err_msg = "More than 1 requests updated: Ret Id:" + str(ret_id)

	## Refetch
	ret = Return_order.objects.filter(ret_id = ret_id).first()
	
	
	
	ret_o_items = Return_order_item.objects.filter(return_order_id = ret_id).values_list('order_item_id', flat=True)
	ret_items = Order_items_view.objects.select_related('product').filter(
		order_item_id__in = ret_o_items,
		product__product_type_id = F('product_type_id'))
	
	return render(request, 'returns/return_request_update_confirm.html', {'ret':ret, 'ret_items': ret_items, 'err_flag': err_flag,
		'err_msg': err_msg})
	


@staff_member_required
def returns_report(request):
	status_list = Return_order.RET_STATUS
	return render(request, 'returns/returns_report.html', {'status_list':status_list})		

@staff_member_required
@csrf_exempt
def get_returns_report(request):
	startDt = ''
	endDt = ''	
	page = request.POST.get('page', 1)

	ret_orders = Return_order.objects.all().order_by('ret_request_date')
	
	from_date = request.POST.get("fromdate", '')
	if from_date != '' :
		startDt = datetime.datetime.strptime(from_date + " 00:00:01", "%Y-%m-%d %H:%M:%S")	
		ret_orders = ret_orders.filter(ret_request_date__gte = startDt)
		
	to_date = request.POST.get("todate", '')
	if to_date != '' :
		endDt = datetime.datetime.strptime(to_date + " 23:59:59", "%Y-%m-%d %H:%M:%S")
		ret_orders = ret_orders.filter(ret_request_date__lte = endDt)

	sts = request.POST.getlist("checked_sts[]",'')
	if sts :
		'''
		f = Q()
		for s in sts:
			f = f | Q(ret_status = s)
		print(f)
		'''
		ret_orders = ret_orders.filter(ret_status__in = sts)
	
	#ret_orders = ret_orders.filter(ret_statuxs = sts)
		
	ret_order_items = Return_order_item.objects.filter(return_order__in = ret_orders)
	order_item_ids = ret_order_items.values_list('order_item_id', flat=True)

	order_items = Order_items_view.objects.select_related('product').filter(
			order_item_id__in = order_item_ids,
			product__product_type_id = F('product_type_id'))

	return render(request, 'returns/returns_report_table.html', {'ret_orders': ret_orders,
		'ret_order_items': ret_order_items, 'order_items': order_items})
