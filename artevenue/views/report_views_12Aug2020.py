from django.shortcuts import render, get_object_or_404
from django.http import HttpResponse
from django.conf import settings
from django.http import JsonResponse
from django.contrib.auth.decorators import login_required
from django.views.decorators.csrf import csrf_protect, csrf_exempt
from django.db import IntegrityError, DatabaseError, Error
from django.contrib.auth.models import User
from django.core.paginator import EmptyPage, PageNotAnInteger, Paginator
from django.db.models import Count, Q, Max, Sum, F
from datetime import datetime
import datetime

from django.contrib.auth.models import User

from artevenue.decorators import is_manager
from artevenue.models import Order, Order_items_view, Ecom_site, Business_referral_fee, UserProfile
from artevenue.models import Business_profile
from artevenue.models import Cart, Cart_item_view


today = datetime.datetime.today()
ecom_site = Ecom_site.objects.get(store_id=settings.STORE_ID )

@csrf_exempt
@is_manager
def get_order_summary(request):
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
		order_list = order_list.filter(order_date__gte = startDt)
	if endDt:
		order_list = order_list.filter(order_date__lte = endDt)
		
	#order_items_list = Order_items_view.objects.filter(
	#	order__in = order_list, product__product_type_id = F('product_type_id')).select_related('product', 'promotion')

	## Totals
	totals = order_list.aggregate(Sum('unit_price'), Sum('quantity'), Sum('order_discount_amt'), 
		Sum('shipping_cost'), Sum('sub_total'), Sum('tax'), Sum('order_total'))


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
		return render(request, 'artevenue/order_summary_table.html', { 
			'orders': order_list, 'totals':totals, 'startDt':startDt, 'endDt':endDt,
			'ecom_site':ecom_site, 'total_cgst':total_cgst, 'total_sgst':total_sgst,
			'total_igst':total_igst})		


def store_order_summary(request):
	return render(request, 'artevenue/store_order_summary.html')
	
def my_business_report_wrap(request):
	return render(request, 'artevenue/my_business_report_wrap.html')
	

@login_required
@csrf_exempt
def my_business_report(request, user_id=None):
	msg = ''
	business_code = ''
	clients = {}
	client_total = 0
	clients_with_orders = {}
	orders = {}
	total_order_value = 0 
	pdf = request.GET.get('printpdf','')
	if pdf == 'TRUE':
		printpdf = True
	else:
		printpdf = False

	startDt = ''
	endDt = ''	
	page = request.POST.get('page', 1)	
	from_date = request.POST.get("fromdate", '')
	if from_date != '' :
		startDt = datetime.datetime.strptime(from_date, "%Y-%m-%d").date()
		
	to_date = request.POST.get("todate", '')
	if to_date != '' :
		endDt = datetime.datetime.strptime(to_date, "%Y-%m-%d").date()

	deferred_payment = False
	try:
		if user_id == None:
			username = request.user
			curruser = User.objects.get(username = request.user)
		else:
			curruser = User.objects.get(id = user_id)
		bus_profile = Business_profile.objects.get(user = curruser)
		business_code = bus_profile.business_code
		if bus_profile.profile_group:
			deferred_payment = bus_profile.profile_group.deferred_payment
	except Business_profile.DoesNotExist:
		bus_profile = None
		deferred_payment = False
	except User.DoesNotExist:
		curruser = None
	
	if curruser == None:
		msg = "You need to be logged in to view this page"
		return render(request, 'artevenue/my_business_report.html', {'client_total':client_total, 
				'clients_with_orders': clients_with_orders, 'clients':clients, 'orders':orders,
				'total_order_value':total_order_value, 'msg':msg})
	if bus_profile == None:
		msg = "You don't seem to have a business account with us. Please check out 'Business' link at the top of the page."
		return render(request, 'artevenue/my_business_report.html', {'client_total':client_total, 
				'clients_with_orders': clients_with_orders, 'clients':clients, 'orders':orders,
				'total_order_value':total_order_value, 'msg':msg})

	users = UserProfile.objects.filter( business_profile = bus_profile )
	client_ids = UserProfile.objects.filter( business_profile = bus_profile ).values('user_id')
	
	orders = Order.objects.filter( Q( user_id__in = client_ids, order_status = 'PC' ) | Q(
				user = curruser, order_status = 'PC' ) ).order_by('user_id')
	
	if startDt:
		orders = orders.filter(order_date__gte = startDt)
	if endDt:
		orders = orders.filter(order_date__lte = endDt)
	
	clients = User.objects.filter(id__in = client_ids).annotate(ord_amt=Sum('order__sub_total'),
		ord_num=Count('order__order_id'))

	referral = Business_referral_fee.objects.filter( order__in = orders )

	client_total = clients.count()
	clients_with_orders = orders.values('user').distinct().count()
	ord_total = orders.aggregate(ord_amt=Sum('sub_total'))
	total_order_value = ord_total['ord_amt']
	total_fee = referral.aggregate(ref_fee = Sum('fee_amount'))
	total_ref_fee = 0
	if total_fee:
		if total_fee['ref_fee']:
			total_ref_fee = total_fee['ref_fee']

	results = []
	for c in clients:
		row = {}
		name = c.first_name + ' ' + c.last_name + ', ' + c.email
		
		order_no = ''
		order_date = ''
		order_val = 0
		ref_fee = 0
		fee_paid_dt = "-"
		fee_paid_ref = ''
		def_pay = False
		for o in orders:
			if o.user_id == c.id:
				order_no = o.order_number
				order_date = o.order_date
				order_val = o.sub_total		
				def_pay = o.deferred_payment
				for r in referral:
					if o == r.order:
						ref_fee = r.fee_amount
						fee_paid_dt = r.fee_paid_date
						fee_paid_ref = r.fee_paid_reference
		row['id'] = c.id
		row['client'] = name
		row['order_number'] = order_no
		row['order_date'] = order_date
		row['ord_val'] = order_val
		row['ref_fee'] = ref_fee
		row['fee_paid_dt'] = fee_paid_dt
		row['fee_paid_ref'] = fee_paid_ref
		row['deferred_payment'] = def_pay
		results.append(row)

	if not printpdf :
		return render(request, 'artevenue/my_business_report.html', {'client_total':client_total, 
			'clients_with_orders': clients_with_orders, 'total_order_value':total_order_value, 
			'msg': msg, 'results':results, 'business_code':business_code, 'total_ref_fee':total_ref_fee})
	else:
		html_string = render_to_string('artevenue/my_business_report_pdf.html', {'client_total':client_total, 
			'clients_with_orders': clients_with_orders, 'total_order_value':total_order_value, 
			'msg': msg, 'results':results, 'business_code':business_code, 'total_ref_fee':total_ref_fee})

		html = HTML(string=html_string, base_url=request.build_absolute_uri())
		html.write_pdf(target= settings.TMP_FILES + str(request.user) + '_business_rep.pdf',
			stylesheets=[CSS(settings.CSS_FILES +  'style.default.css'), 
						CSS(settings.CSS_FILES +  'custom.css'),
						CSS(settings.VENDOR_FILES + 'bootstrap/css/bootstrap.min.css') ],
						presentational_hints=True);
		
		fs = FileSystemStorage(settings.TMP_FILES)
		with fs.open(str(request.user) + '_business_rep.pdf') as pdf:
			response = HttpResponse(pdf, content_type='application/pdf')
			response['Content-Disposition'] = 'attachment; filename="' + str(request.user) + '_business_rep.pdf"'
			return response

		return response	

@login_required
def my_client_order_report(request, client_id=None):
	msg = ''
	total_order_value = 0
	orders = {}
	if client_id == None:
		client_id = request.POST.get('client_id', none)
		
	if client_id == None:
		msg = "No client specified"
	
	orders = Order.objects.filter(user_id = client_id)
	order_total = orders.aggregate(ord_amt = Sum('order_total'))
	if order_total['ord_amt']:
		total_order_value = order_total['ord_amt']
	else:
		total_order_value = 0
	return render(request, 'artevenue/my_client_order_report.html', {
			'orders':orders, 'total_order_value':total_order_value, 'msg': msg}	)


@is_manager			
def cart_order_match_report(request):
	return render(request, 'artevenue/cart_order_sync_report.html')


@csrf_exempt
@is_manager			
def get_cart_order_match(request):
	startDt = ''
	endDt = ''	
	page = request.POST.get('page', 1)
	printpdf = request.POST.get('printpdf', 'NO')
	
	from_date = request.POST.get("fromdate", '')
	if from_date != '' :
		startDt = datetime.datetime.strptime(from_date, "%Y-%m-%d").date()
		
	to_date = request.POST.get("todate", '')
	if to_date != '' :
		endDt = datetime.datetime.strptime(to_date, "%Y-%m-%d").date()
	
	## Orders
	orders = Order.objects.filter(order_date__gte = startDt,
		order_date__lte = endDt).exclude(order_number = '').order_by(
		'-order_date')

	count = orders.count()
	
	order_ids = orders.values('order_id')
	order_items = Order_items_view.objects.select_related(
		'product', 'promotion').filter(
		order__in = orders, product__product_type_id = F('product_type_id')).order_by(
		'-order__order_date', 'order_id', 'product__product_id')
	
	order_cart_items_ids = order_items.values('cart_item_id')
	
	cart_ids = orders.values('cart_id')
	carts = Cart.objects.filter( cart_id__in = cart_ids )
	cart_items = Cart_item_view.objects.select_related(
		'product', 'promotion').filter( cart__in = carts,
		product__product_type_id = F('product_type_id') ).order_by(
		'product__product_id')

	n_cart_items = Cart_item_view.objects.select_related(
		'product', 'promotion').filter( cart__in = carts,
		product__product_type_id = F('product_type_id') ).exclude(
		cart_item_id__in = order_cart_items_ids).order_by(
		'product__product_id')
	
	if printpdf == "YES":
		html_string = render_to_string('artevenue/orders_carts_sync_table.html', {
			'orders':order, 'order_items':order_items, 'carts': carts, 
			'cart_items': cart_items, 'startDt': startDt, 'endDt': endDt, 'count': count})

		html = HTML(string=html_string, base_url=request.build_absolute_uri('/'))
		
		html.write_pdf(target= settings.TMP_FILES + str(request.user) + '_ord_pdf.pdf',
			stylesheets=[
						CSS(settings.CSS_FILES +  'style.default.css'), 
						CSS(settings.CSS_FILES +  'custom.css'),
						CSS(settings.VENDOR_FILES + 'bootstrap/css/bootstrap.min.css') 
						],
						presentational_hints=True);
		
		fs = FileSystemStorage(settings.TMP_FILES)
		with fs.open(str(request.user) + '_ord_cart_match.pdf') as pdf:
			response = HttpResponse(pdf, content_type='application/pdf')
			response['Content-Disposition'] = 'attachment; filename="' + str(request.user) + '_ord_cart_match.pdf"'
			return response

		return response		
	else:
		return render(request, 'artevenue/orders_carts_sync_table.html', {
		'orders':orders , 'order_items':order_items, 'carts': carts, 
			'cart_items': cart_items, 'n_cart_items': n_cart_items,
			'startDt': startDt, 'endDt': endDt, 'count': count} )
		
		'''
		'orders':order, 'order_items':order_items, 'carts': carts, 'cart_items': cart_items,
		'startDt': startDt, 'endDt': endDt}	)
		'''